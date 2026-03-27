from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
from pathlib import Path

app = FastAPI(title="Air Quality Risk API")

# ✅ CORS (FINAL FIX)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all (safe for dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Load models
BASE = Path(__file__).parent / "models"
model = joblib.load(BASE / "xgb_model.pkl")
scaler = joblib.load(BASE / "scaler.pkl")
feat_names = joblib.load(BASE / "feature_names.pkl")

# Labels
RISK_LABELS = {0: "Low", 1: "Moderate", 2: "High"}
RISK_COLORS = {0: "#00e5a0", 1: "#fbbf24", 2: "#f87171"}

# Input schema
class PollutantInput(BaseModel):
    PM2_5: float
    PM10: float
    NO2: float
    SO2: float
    CO: float
    O3: float
    Temperature: float = 25.0
    Precipitation: float = 0.0
    WindSpeed: float = 10.0

# Root
@app.get("/")
def root():
    return {"status": "ok", "message": "API running"}

# Health check
@app.get("/health")
def health():
    return {"status": "healthy"}

# Predict endpoint
@app.post("/predict")
def predict(data: PollutantInput):
    try:
        # Base parameters
        temp = data.Temperature
        precip = data.Precipitation
        wind = data.WindSpeed
        
        pollutants = {
            "PM2.5": data.PM2_5, "PM10": data.PM10, 
            "NO2": data.NO2, "SO2": data.SO2, 
            "CO": data.CO, "O3": data.O3
        }

        # Dynamically map missing sensor values to the mathematical Mean of the training distribution
        # to prevent XGBoost from interpreting omitted variables as extreme edge-case outliers
        row = {feat_names[i]: float(scaler.mean_[i]) for i in range(len(feat_names))}
        
        # Populate Base Weather
        if 'Temperature' in row: row['Temperature'] = temp
        if 'Temp_Min' in row: row['Temp_Min'] = temp - 2.0
        if 'Temp_Max' in row: row['Temp_Max'] = temp + 2.0
        if 'Precipitation' in row: row['Precipitation'] = precip
        if 'WindSpeed' in row: row['WindSpeed'] = wind
        if 'AQI' in row: row['AQI'] = max(data.PM2_5, data.PM10 * 0.5)

        # Extrapolate Rolling, Lagging, and Interaction features mathematically
        for p_name, p_val in pollutants.items():
            for lag in [1, 3, 7]:
                if f"{p_name}_lag{lag}" in row: row[f"{p_name}_lag{lag}"] = p_val
            if f"{p_name}_roll7_mean" in row: row[f"{p_name}_roll7_mean"] = p_val

            # Explicit Interaction Features
            if f"{p_name}_x_Temperature" in row: row[f"{p_name}_x_Temperature"] = p_val * temp
            if f"{p_name}_x_Temp_Min" in row: row[f"{p_name}_x_Temp_Min"] = p_val * (temp - 2.0)
            if f"{p_name}_x_Temp_Max" in row: row[f"{p_name}_x_Temp_Max"] = p_val * (temp + 2.0)
            if f"{p_name}_x_Precipitation" in row: row[f"{p_name}_x_Precipitation"] = p_val * precip
            if f"{p_name}_x_WindSpeed" in row: row[f"{p_name}_x_WindSpeed"] = p_val * wind

        # Special legacy interaction check
        if 'Temp_PM25' in row: row['Temp_PM25'] = temp * data.PM2_5

        # Convert to dataframe
        X = pd.DataFrame([row])[feat_names]

        # Scale
        X_scaled = scaler.transform(X)

        # Predict
        import builtins
        import json
        
        pred_raw = model.predict(X_scaled)[0]
        pred = builtins.int(pred_raw.item() if hasattr(pred_raw, 'item') else pred_raw)

        proba_raw = model.predict_proba(X_scaled)[0]
        proba = proba_raw.tolist() if hasattr(proba_raw, 'tolist') else list(proba_raw)

        PRECAUTIONS = {
            0: ["Enjoy unrestricted outdoor activities", "Natural ventilation is highly recommended", "Perfect conditions for respiratory health"],
            1: ["Unusually sensitive groups should reduce prolonged outdoor exertion", "Keep rescue inhalers accessible if asthmatic", "Monitor air quality if conditions worsen"],
            2: ["Strictly avoid all outdoor physical activity", "Keep all windows closed and operate HEPA purifiers", "Mandatory N95/KN95 mask usage if going outdoors"]
        }

        res = {
            "risk_level": builtins.int(pred),
            "risk_label": str(RISK_LABELS.get(pred, "Unknown")),
            "risk_color": str(RISK_COLORS.get(pred, "#ffffff")),
            "confidence": builtins.float(round(max(proba) * 100, 1)),
            "probabilities": {
                "Low": builtins.float(round(proba[0] * 100, 1)),
                "Moderate": builtins.float(round(proba[1] * 100, 1)),
                "High": builtins.float(round(proba[2] * 100, 1)),
            },
            "precautions": PRECAUTIONS.get(pred, ["Data unavailable"])
        }
        
        # Guaranteed safe return bypassing FastAPI pydantic leaks
        return json.loads(json.dumps(res))

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}