guardiangrid/
├── README.md
├── requirements.txt
├── setup.py
├── .env
│
├── data/
│   ├── raw/
│   │   ├── ncrb_drowning_data.csv
│   │   ├── water_bodies_geojson.json
│   │   └── historical_incidents.csv
│   ├── processed/
│   │   ├── cleaned_incidents.csv
│   │   ├── feature_engineered_data.csv
│   │   └── risk_scores_daily.csv
│   └── external/
│       ├── weather_api_cache/
│       └── map_tiles/
│
├── src/
│   ├── __init__.py
│   │
│   ├── data_pipeline/
│   │   ├── __init__.py
│   │   ├── collector.py          # Data collection from APIs
│   │   ├── cleaner.py            # Data cleaning & preprocessing
│   │   ├── feature_engineering.py # Feature creation
│   │   └── data_loader.py        # Unified data loading
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── risk_predictor.py     # Regression: Risk score prediction
│   │   ├── severity_classifier.py # Classification: Incident triage
│   │   ├── risk_cluster.py       # Clustering: Risk archetypes
│   │   ├── model_trainer.py      # Training pipeline
│   │   └── model_evaluator.py    # Validation & metrics
│   │
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── eda.py                # Exploratory Data Analysis
│   │   ├── statistical_tests.py  # ANOVA, Chi-square, Correlation
│   │   └── fairness_audit.py     # Responsible AI / Equity audit
│   │
│   ├── features/
│   │   ├── __init__.py
│   │   ├── drowning_detection.py # Feature 1: Pose analysis
│   │   ├── responder_system.py   # Feature 2: Nearest responder
│   │   └── warning_system.py     # Feature 3: Proactive warning
│   │
│   └── visualization/
│       ├── __init__.py
│       ├── dashboard.py          # Streamlit dashboard
│       ├── plots.py              # Matplotlib/Seaborn visualizations
│       └── map_utils.py          # Folium/Plotly maps
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_model_training.ipynb
│   ├── 04_model_evaluation.ipynb
│   └── 05_risk_analysis_dashboard.ipynb
│
├── tests/
│   ├── test_data_pipeline.py
│   ├── test_models.py
│   └── test_features.py
│
├── outputs/
│   ├── models/
│   │   ├── risk_predictor.pkl
│   │   ├── severity_classifier.pkl
│   │   └── risk_cluster.pkl
│   ├── plots/
│   │   ├── eda/
│   │   ├── model_performance/
│   │   └── feature_importance/
│   └── reports/
│       ├── fairness_audit_report.html
│       └── model_validation_report.html
│
└── config/
    ├── config.yaml
    └── logging_config.yaml
