# WildGuard — Human-Wildlife Conflict Prediction System

> *Protecting wildlife and people through intelligent conflict prediction.*

WildGuard is a conservation technology platform that combines real-time animal detection, spatiotemporal machine learning, and interactive geospatial visualization to forecast human-wildlife conflict hotspots before they occur. It was developed as a final-year project and validated across two geographic regions: **Parks Canada** and **Chitwan National Park, Nepal**.

---

## The Problem

Human-wildlife conflicts are escalating in wildlife corridor regions worldwide — causing crop damage, livestock predation, property destruction, and threatening both human safety and wildlife conservation. Communities and park authorities currently respond *reactively* rather than *proactively*, lacking the predictive tools to anticipate and prevent conflicts before they happen.

---

## The Solution

WildGuard integrates four core ML/AI components into a unified web dashboard:

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Animal Detection | YOLOv8 | Identify species from uploaded images with bounding boxes and confidence scores |
| Risk Classification | Random Forest | Predict conflict risk level (HIGH / MEDIUM / LOW) for a given location and time |
| Hotspot Mapping | DBSCAN + KMeans | Cluster historical incidents into spatial hotspots and risk zones |
| Conflict Forecasting | SARIMAX | Time-series forecast of monthly incident frequency up to 12 months ahead |

---

## Features

- **Animal Detection** — Upload a field photo and get instant species identification, confidence score, and bounding box overlay
- **Interactive Risk Map** — Color-coded heatmap of conflict zones with toggleable layers (RF Risk Heatmap, DBSCAN Hotspots, KMeans Zones, Live Reports)
- **Risk Assessment Tool** — Input a location and month to receive a predicted risk rating with confidence breakdown
- **Analytics Dashboard** — Species distribution charts, monthly trend lines, seasonal heatmaps, and SARIMAX forecast plots for both Canada and Chitwan
- **Live Reports Feed** — Real-time community sighting submissions with auto-refresh
- **User Authentication** — Register and sign in with session persistence and personalized avatar initials

---

## Datasets

| Dataset | Source | Period | Records |
|---------|--------|--------|---------|
| Parks Canada Human-Wildlife Coexistence Database | [open.canada.ca](https://open.canada.ca/data/en/dataset/743a0b4a-9e33-4b12-981a-9f9fd3dd1680) | 2010–2023 | ~49,000 incidents |
| Shuklaphanta / Chitwan Conflict Data | Research paper (GPS-level) | 1998–2018 | ~756 incidents |

Both datasets are used under open government / research licenses. The Canadian dataset provides robust model training; the Chitwan dataset validates cross-regional transferability.

---

## Tech Stack

**Machine Learning**
- YOLOv8 (animal detection)
- Random Forest Classifier (risk prediction)
- DBSCAN (spatial clustering / hotspot detection)
- KMeans (regional zone segmentation)
- SARIMAX (time-series conflict forecasting)

**Frontend**
- HTML, CSS, JavaScript (vanilla)
- Plotly (interactive charts)
- Folium / Leaflet.js (interactive maps)

**Backend** *(in progress)*
- Python — Flask or FastAPI
- PostgreSQL / MongoDB
- Deployment: Render or Railway

---

## Repository Structure

```
WildGuard-HWC-Prediction-System/
├── README.md
├── notebooks/
│   ├── chitwan/
│   │   ├── DBSCAN_clustering.ipynb
│   │   ├── Random_forest_classification.ipynb
│   │   ├── Risk_Analysis_(Classification)_(dataset_cleaning).ipynb
│   │   └── Time_Series_Analysis.ipynb
│   └── canada_parks/
│       ├── Random_Forest_Dataset_Preparation_(Parks_Canada).ipynb
│       ├── parks_canada_arima.ipynb
│       ├── parks_canada_dbscan.ipynb
│       └── parks_canada_rf_v2.ipynb
└── frontend/
    ├── index.html                          ← entry point
    ├── pages/                              ← app screens
    │   ├── wildguard_analytics_html_.html
    │   ├── wildguard_animal_detection.html
    │   ├── wildguard_field_protocol.html
    │   ├── wildguard_live_reports.html
    │   ├── wildguard_login_html_.html
    │   ├── wildguard_notifications.html
    │   ├── wildguard_privacy_policy.html
    │   ├── wildguard_profile_html_.html
    │   ├── wildguard_risk_assessment_html_.html
    │   ├── wildguard_risk_map_html.html
    │   └── wildguard_terms_of_service.html
    └── visualizations/                     ← ML output charts
        ├── canada/                         ← Parks Canada dataset
        │   ├── canada_viz3_dbscan_hotspot_map.html
        │   ├── canada_viz6_rf_risk_heatmap.html
        │   ├── canada_viz7_kmeans_zones.html
        │   ├── canada_viz_8_species_risk_heatmap.html
        │   └── canada_viz10_species_donut.html
        ├── chitwan/                        ← Chitwan National Park dataset
        │   ├── chitwan_viz1_conflict_heatmap.html
        │   ├── chitwan_viz2_kmeans_zones_map.html
        │   ├── chitwan_viz3_dbscan_hotspot.html
        │   ├── chitwan_viz4_sarima_forecast.html
        │   ├── chitwan_viz5_species_donut.html
        │   ├── chitwan_viz6_monthly_trend.html
        │   └── chitwan_viz11_species_month_heatmap.html
        └── combined/                       ← cross-regional comparisons
            ├── viz4_sarimax_forecast.html
            └── viz5_monthly_trend.html
```

---

## Team

| Member | Role |
|--------|------|
| Deepika | ML models — Random Forest, DBSCAN, KMeans, SARIMAX; dataset preparation |
| Ina | Computer Vision — YOLOv8 training and species detection |
| Shikshya | Backend — Flask/FastAPI, database, API endpoints |
| Riya | Frontend — dashboard, detection, risk assessment, live reports pages |
| Prasamsha | Visualizations — Plotly charts, Folium maps, analytics dashboard |

---

## Running Locally

```bash
# Clone the repo
git clone https://github.com/Deepikahaha/WildGuard-HWC-Prediction-System.git
cd WildGuard-HWC-Prediction-System/frontend

# Serve with Python (required — direct file:// won't load iframes)
python -m http.server 8000

# Then open in browser
http://localhost:8000
```

> **Note:** Open via `localhost`, not by double-clicking the HTML file. Browsers block iframe loading from `file://` paths.

---

## Status

- [x] Frontend prototype complete (all 11 pages)
- [x] ML notebooks complete (Random Forest, DBSCAN, KMeans, SARIMAX)
- [x] YOLOv8 model trained (7 species)
- [x] Plotly visualizations complete (Canada + Chitwan)
- [ ] Backend API (in progress)
- [ ] Backend–frontend integration (pending backend deployment)
- [ ] Live camera trap integration (future)

---

## License

This project was developed for academic and conservation research purposes. Data sourced from Parks Canada is used under the [Open Government Licence – Canada](https://open.canada.ca/en/open-government-licence-canada).
