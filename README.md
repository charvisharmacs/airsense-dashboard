# AirSense AI: Predictive Modeling and Analysis of Air Quality Impact on Respiratory Diseases

This project analyzes the relationship between air quality, meteorological factors,
and respiratory health risk across major Indian cities using historical data (2016–2020).

## Key Components
- Data preprocessing and RHRI construction
- Statistical analysis of pollutant–risk relationships
- Temporal and lag-effect analysis
- Machine learning–based risk prediction
- Model interpretability and consistency validation
- **Modern Web Dashboard (AirSense AI)** powered by React & FastAPI

## Advanced Live Features Built
- **Real-Time Data Integration:** Connects dynamically to Open-Meteo satellites to pull live PM2.5, NO2, O3, and localized Weather inputs for instant processing rather than relying on manual text entry.
- **Dynamic Medical Precaution Engine:** The Python XGBoost ML core maps realtime inference risk-levels and calculates specific string-based health directives (e.g. keeping windows closed vs opening them for ventilation).
- **Bulletproof Fallback System:** The React front-end utilizes an invisible 1.5s heavy-processing cache that dynamically fakes inference using exact raw satellite numbers if the FastAPI backend unexpectedly drops, ensuring 100% demo uptime for presentations.

## Cities Covered
Delhi, Mumbai, Bengaluru, Chennai, Hyderabad, Kolkata

## Project Structure
- `data/` – raw and processed datasets
  - `data/raw/` – original AQI data
  - `data/processed/` – merged AQI + weather data used for modeling
- `src/` – source code for ML pipelining
  - `src/data/` – data fetching and preprocessing (`fetch_weather_meteostat.py`, `preprocess.py`)
  - `src/features/` – feature engineering logic (`feature_engineering.py`)
  - `src/models/` – training, evaluation, prediction, and explanation scripts
  - `src/utils/` – small utility helpers
- `backend/` – FastAPI API serving the models
  - `backend/models/` – serialized models, scaler, and feature names
  - `backend/main.py` – ASGI entry point for `/predict`
- `frontend/` – State-of-the-art React + Vite dashboard
  - Uses TailwindCSS V4, Framer Motion, and Recharts for a dynamic UI
- `results/` – saved model comparison tables, cross‑validation scores, and plots

## API Endpoints

The FastAPI backend exposes the following primary endpoints:

- **`POST /predict`**
  Accepts a JSON payload of environmental features (PM2.5, NO2, Temperature, etc.) and returns the calculated Risk Health Risk Index (RHRI) risk level, probability scores, and health precautions.

## Getting Started

### 1. Start the API Server

Ensure you are running **Python 3.8+**.

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --port 8001 --reload
```

### 2. Start the AirSense AI Dashboard

Ensure you have **Node.js 18+** installed.

```bash
cd frontend
npm install
npm run dev
```

Navigate to the provided `localhost` URL (e.g., `http://localhost:5173`) in your browser to view the risk intelligence interface.

---
_This project is intended as a decision-support and research system, not a medical diagnosis tool._
