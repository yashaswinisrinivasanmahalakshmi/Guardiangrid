"""
GUARDIANGRID - Complete Dashboard
Run with: streamlit run guardiangrid_dashboard.py
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="GuardianGrid - Water Safety Dashboard",
    page_icon="🏊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        background-color: #0a0a1a;
    }
    .stApp {
        background-color: #0a0a1a;
    }
    .css-18e3th9 {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .css-1d391kg {
        background-color: #16213e;
    }
    .dashboard-title {
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #ff6b6b, #ffd93d, #6bcb77, #4d96ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .feature-card {
        background-color: #16213e;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #4d96ff;
    }
    .status-badge {
        padding: 0.25rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# DATA SIMULATION FUNCTIONS
# ============================================================

def simulate_pose_data(drowning=True):
    """Simulate pose keypoints for drowning detection"""
    if drowning:
        return {
            'head_y': 0.85,
            'arm_angle': 145,
            'speed': 0.02,
            'leg_activity': 0.05,
            'head_tilt': 18,
            'drowning': True,
            'confidence': 0.82
        }
    else:
        return {
            'head_y': 0.3,
            'arm_angle': 30,
            'speed': 0.4,
            'leg_activity': 0.5,
            'head_tilt': 3,
            'drowning': False,
            'confidence': 0.12
        }

def simulate_responders():
    """Simulate responder data"""
    np.random.seed(42)
    types = ['Lifeguard', 'Volunteer', 'CPR_Certified', 'Strong_Swimmer']
    n = 20
    
    responders = pd.DataFrame({
        'id': range(1, n+1),
        'type': np.random.choice(types, n),
        'lat': 12.97 + np.random.normal(0, 0.015, n),
        'lon': 77.59 + np.random.normal(0, 0.015, n),
        'available': np.random.choice([True, True, True, False], n),
        'response_time': np.random.randint(2, 8, n)
    })
    
    # Calculate distances from incident
    incident_lat, incident_lon = 12.985, 77.6
    distances = []
    for _, r in responders.iterrows():
        dist = np.sqrt((r['lat'] - incident_lat)**2 + (r['lon'] - incident_lon)**2) * 111
        distances.append(dist)
    responders['distance_km'] = distances
    
    return responders.sort_values('distance_km')

def simulate_risk_timeline(n_points=50):
    """Simulate risk factors over time"""
    time = np.arange(n_points)
    
    rain = np.clip(0.3 + 0.5 * np.sin(time * 0.3) + 0.1 * np.random.randn(n_points), 0, 1)
    temp = np.clip(30 + 8 * np.sin(time * 0.2) + 2 * np.random.randn(n_points), 20, 40)
    wind = np.clip(10 + 15 * np.sin(time * 0.25) + 3 * np.random.randn(n_points), 0, 30)
    water_level = np.clip(0.3 + 0.5 * (1 - np.exp(-rain * 3)) + 0.1 * np.random.randn(n_points), 0, 1)
    current = np.clip(0.3 + 0.4 * rain + 0.1 * np.random.randn(n_points), 0, 1)
    crowd = np.clip(0.5 + 0.4 * np.sin(time * 0.1) + 0.1 * np.random.randn(n_points), 0, 1)
    
    risk = (rain * 0.25 + 
            np.clip((temp - 30) / 10, 0, 1) * 0.15 + 
            (wind / 30) * 0.10 + 
            water_level * 0.20 + 
            current * 0.20 + 
            crowd * 0.10)
    
    return {
        'time': time,
        'risk': risk,
        'rain': rain,
        'temp': temp,
        'wind': wind,
        'water_level': water_level,
        'current': current,
        'crowd': crowd,
        'threshold': 0.55
    }

# ============================================================
# DASHBOARD COMPONENTS
# ============================================================

def render_header():
    """Render dashboard header"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<h1 class="dashboard-title">🏊 GuardianGrid</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #aaa;">Spatiotemporal Water Safety Risk Intelligence</p>', unsafe_allow_html=True)
        st.markdown('---')

def render_status_bar():
    """Render real-time status bar"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Simulate real-time data
    risk_data = simulate_risk_timeline(1)
    current_risk = risk_data['risk'][0]
    
    with col1:
        st.metric("📍 Location", "Lake View", "Active")
    with col2:
        if current_risk > 0.55:
            st.metric("🚨 Risk Level", f"{current_risk:.0%}", delta="HIGH", delta_color="inverse")
        else:
            st.metric("🚨 Risk Level", f"{current_risk:.0%}", delta="LOW")
    with col3:
        st.metric("🌡️ Water Temp", f"{22 + np.random.randn():.1f}°C", "Normal")
    with col4:
        st.metric("👥 Visitors", f"{int(45 + 30 * np.random.randn())}", "+12%")
    with col5:
        st.metric("⏰ Last Update", datetime.now().strftime("%H:%M:%S"), "Live")

# ============================================================
# FEATURE 1: DROWNING DETECTION
# ============================================================

def render_drowning_detection():
    """Render Feature 1: Real-time drowning detection"""
    st.markdown("---")
    st.markdown('<h2 style="color: white; text-align: center;">🔴 Feature 1: Real-Time Drowning Detection</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    # Left: Pose visualization
    with col1:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        
        # Show both states
        states = [
            ("Safe Swimmer", False, "🟢", "#6bcb77"),
            ("Drowning Detected", True, "🔴", "#ff6b6b")
        ]
        
        for state_name, is_drowning, icon, color in states:
            pose = simulate_pose_data(is_drowning)
            
            fig, ax = plt.subplots(figsize=(6, 8))
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 10)
            ax.axis('off')
            ax.set_facecolor('#16213e')
            
            # Water line
            ax.axhline(y=6, color='#4d96ff', alpha=0.3, linewidth=2)
            
            # Person
            person_y = 2 + 8 * (1 - pose['head_y'])
            person = Circle((5, person_y), 0.4, color=color, alpha=0.8)
            ax.add_patch(person)
            
            # Head
            head = Circle((5, person_y + 0.5), 0.2, color='white', alpha=0.8)
            ax.add_patch(head)
            
            # Arms
            if pose['arm_angle'] > 110:  # Drowning
                ax.plot([5, 5 + 0.5], [person_y, person_y - 0.3], 'w-', linewidth=3)
                ax.plot([5, 5 - 0.5], [person_y, person_y - 0.3], 'w-', linewidth=3)
            else:
                ax.plot([5, 5 + 0.5], [person_y, person_y + 0.3], 'w-', linewidth=3)
                ax.plot([5, 5 - 0.5], [person_y, person_y + 0.3], 'w-', linewidth=3)
            
            # Status
            status = f"{icon} {state_name}"
            ax.text(5, 9, status, color=color, ha='center', fontsize=14, weight='bold')
            ax.text(5, 0.5, f"Confidence: {pose['confidence']:.0%}", color='white', ha='center', fontsize=10)
            
            # Indicators
            indicators = []
            if pose['head_y'] > 0.7:
                indicators.append('• Head submerged')
            if pose['arm_angle'] > 110:
                indicators.append('• Downward arm push')
            if pose['speed'] < 0.1:
                indicators.append('• No forward movement')
            if pose['leg_activity'] < 0.15:
                indicators.append('• Minimal leg activity')
            
            ax.text(0.5, 1, '\n'.join(indicators), color='white', fontsize=8,
                   bbox=dict(boxstyle="round", facecolor='black', alpha=0.5))
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Right: Detection pipeline and stats
    with col2:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        
        # Detection pipeline
        st.markdown("### 🧠 AI Detection Pipeline")
        
        pipeline_steps = [
            ("📹 Camera Feed", "Active"),
            ("🎯 Pose Detection", "Active"),
            ("📊 Pattern Analysis", "Active"),
            ("🚨 Alert Trigger", "Standby")
        ]
        
        for step, status in pipeline_steps:
            col_status, col_step = st.columns([1, 3])
            with col_status:
                st.markdown(f"`{status}`")
            with col_step:
                st.progress(1.0 if status == "Active" else 0.5)
                st.text(step)
        
        # Key stats
        st.markdown("### 📊 Detection Statistics")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Accuracy", "94.2%", "+1.2%")
        with col_b:
            st.metric("Response Time", "1.8s", "-0.3s")
        with col_c:
            st.metric("False Positives", "2.1%", "-0.8%")
        
        # Critical window
        st.markdown("### ⏰ Critical Response Window")
        st.markdown("""
            <div style="background: #1a1a2e; padding: 1rem; border-radius: 10px; border: 2px solid #ff6b6b;">
                <p style="color: white; text-align: center; font-size: 1.2rem;">
                    ⏱️ <span style="color: #ff6b6b; font-weight: bold;">4-6 Minutes</span> 
                    to prevent brain damage
                </p>
                <div style="background: #333; height: 10px; border-radius: 5px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #6bcb77, #ffd93d, #ff6b6b); 
                         width: 100%; height: 100%;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; color: #aaa; font-size: 0.8rem; margin-top: 0.2rem;">
                    <span>0s</span>
                    <span>2min</span>
                    <span>4min ⚠️</span>
                    <span>6min 🚨</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# FEATURE 2: NEAREST RESPONDER
# ============================================================

def render_responder_system():
    """Render Feature 2: Nearest-responder alert system"""
    st.markdown("---")
    st.markdown('<h2 style="color: white; text-align: center;">🟢 Feature 2: Nearest-Responder Alert System</h2>', unsafe_allow_html=True)
    
    responders = simulate_responders()
    incident_lat, incident_lon = 12.985, 77.6
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        
        # Create map using plotly
        fig = go.Figure()
        
        # Incident marker
        fig.add_trace(go.Scattergeo(
            lon=[incident_lon],
            lat=[incident_lat],
            mode='markers',
            marker=dict(
                size=20,
                color='red',
                symbol='x',
                line=dict(width=2, color='white')
            ),
            name='🚨 Incident',
            text=['🚨 Drowning Incident'],
            hoverinfo='text'
        ))
        
        # Response zone
        theta = np.linspace(0, 2*np.pi, 100)
        r = 0.0045
        zone_lon = incident_lon + r * np.cos(theta)
        zone_lat = incident_lat + r * np.sin(theta)
        
        fig.add_trace(go.Scattergeo(
            lon=zone_lon,
            lat=zone_lat,
            mode='lines',
            line=dict(color='red', width=2, dash='dash'),
            fill='toself',
            fillcolor='rgba(255,0,0,0.1)',
            name='Response Zone'
        ))
        
        # Responders
        colors = {
            'Lifeguard': 'blue',
            'Volunteer': 'green',
            'CPR_Certified': 'orange',
            'Strong_Swimmer': 'purple'
        }
        
        for _, r in responders.iterrows():
            color = colors.get(r['type'], 'gray')
            size = 15 if r['available'] else 10
            opacity = 1.0 if r['available'] else 0.3
            
            fig.add_trace(go.Scattergeo(
                lon=[r['lon']],
                lat=[r['lat']],
                mode='markers',
                marker=dict(
                    size=size,
                    color=color,
                    opacity=opacity,
                    symbol='circle',
                    line=dict(width=1, color='white')
                ),
                name=r['type'],
                text=f"{r['type']}<br>Distance: {r['distance_km']:.2f}km<br>{'Available' if r['available'] else 'Unavailable'}",
                hoverinfo='text',
                showlegend=False
            ))
        
        fig.update_layout(
            geo=dict(
                projection_type='mercator',
                center=dict(lon=77.6, lat=12.965),
                lonaxis_range=[77.55, 77.65],
                lataxis_range=[12.94, 12.99],
                bgcolor='#16213e',
                showland=True,
                landcolor='#2d3748',
                lakecolor='#4d96ff',
                showocean=True,
                oceancolor='#1a1a2e',
                showcountries=False,
                showframe=False,
                showcoastlines=False
            ),
            plot_bgcolor='#16213e',
            paper_bgcolor='#16213e',
            height=500,
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(
                font=dict(color='white'),
                bgcolor='rgba(0,0,0,0.5)'
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        
        st.markdown("### 🚨 Alert Dispatch Summary")
        
        # Show top 5 responders
        st.markdown("#### Nearest Responders")
        
        for idx, (_, r) in enumerate(responders.head(5).iterrows()):
            if r['available']:
                status = "✅ Responding" if np.random.random() < 0.8 else "❌ Declined"
                color = "#6bcb77" if "Responding" in status else "#ff6b6b"
                eta = f"{r['distance_km'] * np.random.randint(2, 6):.0f} min"
            else:
                status = "⚪ Unavailable"
                color = "#666"
                eta = "N/A"
            
            st.markdown(f"""
                <div style="background: #1a1a2e; padding: 0.5rem; border-radius: 5px; margin: 0.2rem 0; 
                            border-left: 3px solid {color};">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: white; font-weight: bold;">{r['type']}</span>
                        <span style="color: {color};">{status}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; color: #aaa; font-size: 0.8rem;">
                        <span>📍 {r['distance_km']:.3f} km</span>
                        <span>⏱️ {eta}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Stats
        available = len(responders[responders['available']])
        total = len(responders)
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Available Responders", f"{available}/{total}")
        with col_b:
            st.metric("Avg Response Time", f"{np.mean(responders['distance_km'] * 4):.1f} min")
        
        # Dispatch button
        if st.button("🚨 Dispatch Alert (Test)", use_container_width=True):
            st.success("📱 Alert sent to 3 nearest responders!")
            st.info("• Lifeguard: 2.3 min ETA\n• Volunteer: 3.1 min ETA\n• CPR Certified: 4.5 min ETA")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# FEATURE 3: PROACTIVE WARNING
# ============================================================

def render_warning_system():
    """Render Feature 3: Proactive warning system"""
    st.markdown("---")
    st.markdown('<h2 style="color: white; text-align: center;">🟡 Feature 3: Proactive Warning System</h2>', unsafe_allow_html=True)
    
    # Simulate data
    data = simulate_risk_timeline(50)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        
        # Risk timeline
        fig = make_subplots(rows=2, cols=1, 
                           shared_xaxes=True,
                           vertical_spacing=0.05,
                           subplot_titles=('Risk Score Over Time', 'Risk Factors'))
        
        # Risk plot
        fig.add_trace(
            go.Scatter(
                x=data['time'],
                y=data['risk'],
                mode='lines',
                name='Risk Score',
                line=dict(color='#4d96ff', width=3),
                fill='tozeroy',
                fillcolor='rgba(77, 150, 255, 0.2)'
            ),
            row=1, col=1
        )
        
        # Threshold
        fig.add_trace(
            go.Scatter(
                x=data['time'],
                y=[data['threshold']] * len(data['time']),
                mode='lines',
                name='Warning Threshold',
                line=dict(color='red', width=2, dash='dash')
            ),
            row=1, col=1
        )
        
        # Warning areas
        warnings = np.array(data['risk']) > data['threshold']
        if any(warnings):
            warning_start = None
            for i, w in enumerate(warnings):
                if w and warning_start is None:
                    warning_start = i
                elif not w and warning_start is not None:
                    fig.add_trace(
                        go.Scatter(
                            x=data['time'][warning_start:i],
                            y=[0] * (i - warning_start),
                            mode='lines',
                            fill='tozeroy',
                            fillcolor='rgba(255,0,0,0.3)',
                            name='Warning Active',
                            showlegend=False
                        ),
                        row=1, col=1
                    )
                    warning_start = None
            if warning_start is not None:
                fig.add_trace(
                    go.Scatter(
                        x=data['time'][warning_start:],
                        y=[0] * (len(data['time']) - warning_start),
                        mode='lines',
                        fill='tozeroy',
                        fillcolor='rgba(255,0,0,0.3)',
                        name='Warning Active',
                        showlegend=False
                    ),
                    row=1, col=1
                )
        
        # Risk factors
        factors = {
            'Rain': data['rain'],
            'Water Level': data['water_level'],
            'Current': data['current'],
            'Crowd': data['crowd']
        }
        
        colors = ['#ff6b6b', '#4d96ff', '#ffd93d', '#6bcb77']
        
        for (name, values), color in zip(factors.items(), colors):
            fig.add_trace(
                go.Scatter(
                    x=data['time'],
                    y=values,
                    mode='lines',
                    name=name,
                    line=dict(color=color, width=2)
                ),
                row=2, col=1
            )
        
        fig.update_layout(
            height=500,
            plot_bgcolor='#16213e',
            paper_bgcolor='#16213e',
            font=dict(color='white'),
            legend=dict(
                font=dict(color='white'),
                bgcolor='rgba(0,0,0,0.5)'
            ),
            xaxis=dict(gridcolor='#2d3748'),
            yaxis=dict(gridcolor='#2d3748')
        )
        
        fig.update_xaxes(row=1, col=1, gridcolor='#2d3748')
        fig.update_xaxes(row=2, col=1, gridcolor='#2d3748')
        fig.update_yaxes(row=1, col=1, gridcolor='#2d3748', range=[0, 1])
        fig.update_yaxes(row=2, col=1, gridcolor='#2d3748', range=[0, 1])
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        
        # Current status
        current_risk = data['risk'][-1]
        warning_active = current_risk > data['threshold']
        
        st.markdown("### 📊 Current Status")
        
        if warning_active:
            if current_risk > 0.8:
                level = "CRITICAL"
                color = "#ff6b6b"
                emoji = "🔴"
                action = "🚨 Evacuate Now!"
            elif current_risk > 0.6:
                level = "HIGH"
                color = "#ffd93d"
                emoji = "⚠️"
                action = "📢 Issue Public Alert"
            else:
                level = "MODERATE"
                color = "orange"
                emoji = "⚡"
                action = "👀 Increase Monitoring"
        else:
            level = "LOW"
            color = "#6bcb77"
            emoji = "✅"
            action = "📋 Routine Monitoring"
        
        st.markdown(f"""
            <div style="background: #1a1a2e; padding: 1rem; border-radius: 10px; text-align: center; 
                        border: 2px solid {color};">
                <div style="font-size: 3rem;">{emoji}</div>
                <div style="color: {color}; font-size: 1.5rem; font-weight: bold;">{level} RISK</div>
                <div style="color: white; font-size: 1rem;">Score: {current_risk:.0%}</div>
                <div style="color: #aaa; font-size: 0.9rem; margin-top: 0.5rem;">
                    Action: {action}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Factor contributions
        st.markdown("### 🔍 Contributing Factors")
        
        current_factors = {
            'Rain': data['rain'][-1],
            'Water Level': data['water_level'][-1],
            'Current': data['current'][-1],
            'Crowd': data['crowd'][-1]
        }
        
        for name, value in current_factors.items():
            st.progress(value, text=f"{name}: {value:.0%}")
        
        # Historical stats
        st.markdown("### 📈 Historical Stats")
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Avg Risk", f"{np.mean(data['risk']):.0%}")
        with col_b:
            st.metric("Warnings", f"{sum(np.array(data['risk']) > data['threshold'])}")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():
    """Render sidebar with system info"""
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; padding: 1rem 0;">
                <h2 style="color: white;">🏊 GuardianGrid</h2>
                <p style="color: #aaa; font-size: 0.8rem;">v2.0 - Second Review</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("### 🎯 System Status")
        
        # Mock status
        st.success("✅ Camera Feed: Active")
        st.success("✅ AI Engine: Running")
        st.success("✅ Responder Network: Online")
        st.warning("⚠️ Weather: Moderate Conditions")
        
        st.markdown("---")
        
        st.markdown("### 📋 Features")
        features = [
            ("🔴", "Drowning Detection", "Active"),
            ("🟢", "Responder Alert", "Active"),
            ("🟡", "Warning System", "Active")
        ]
        
        for icon, name, status in features:
            st.markdown(f"<div style='display: flex; justify-content: space-between; padding: 0.3rem 0;'>"
                       f"<span style='color: white;'>{icon} {name}</span>"
                       f"<span style='color: #6bcb77;'>{status}</span></div>", 
                       unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("### 📊 Today's Stats")
        st.metric("Total Alerts", "3", "+2")
        st.metric("Responders Online", "15/20", "-1")
        st.metric("Risk Level", "Low-Medium", "Stable")
        
        st.markdown("---")
        
        st.caption("🔄 Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        st.caption("📍 Location: Lake View Area")
        st.caption("🎯 AD5302 - Data Science Project")

# ============================================================
# MAIN DASHBOARD
# ============================================================

def main():
    """Render the complete dashboard"""
    
    render_sidebar()
    render_header()
    render_status_bar()
    render_drowning_detection()
    render_responder_system()
    render_warning_system()
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #666; padding: 1rem;">
            <p>🏊 GuardianGrid - Spatiotemporal Water Safety Risk Intelligence</p>
            <p style="font-size: 0.8rem;">Team: Sahaana S, Yashaswini Srinivasan Mahalakshmi, T.Tharangini | AD5302</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()