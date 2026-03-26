import os
import sys
import joblib
import shap
import pandas as pd
import matplotlib.pyplot as plt

# Ensure project root and src are on the path so this script
# can be run as `python src/models/explain.py` from project root.
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

from src.config import set_seed
from src.data.preprocess import clean_data, create_rhri, classify_rhri
from src.features.feature_engineering import create_features


def explain_xgboost(data_path):

    # Ensure deterministic behavior where possible
    set_seed()

    os.makedirs("results", exist_ok=True)

    # Load dataset
    df = pd.read_csv(data_path)

    df = clean_data(df)
    df = create_rhri(df)
    df = classify_rhri(df)
    df = create_features(df)

    # Remove leakage features (match training design)
    X = df.drop(columns=[
        "Respiratory_Risk",
        "Risk_Percentage",
        "RHRI",
        "City",
        "Date",
        "PM2.5", "PM10", "NO2", "SO2", "O3", "CO",
        "PM2.5_norm", "PM10_norm", "NO2_norm",
        "SO2_norm", "O3_norm", "CO_norm"
    ], errors="ignore")

    X = X.select_dtypes(include=["number"])
    X = X.fillna(0)

    # Load model + scaler
    model = joblib.load("models/xgb_model.pkl")
    scaler = joblib.load("models/scaler.pkl")

    X_scaled = scaler.transform(X)

    # Use small subset for speed
    X_sample = X_scaled[:1000]
    feature_names = X.columns

    # SHAP Explainer
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)

    # Summary Plot
    plt.figure()
    shap.summary_plot(shap_values, X_sample, feature_names=feature_names, show=False)
    plt.savefig("results/xgb_shap_summary.png", bbox_inches="tight")
    plt.close()

    # Bar Plot
    plt.figure()
    shap.summary_plot(shap_values, X_sample, feature_names=feature_names,
                      plot_type="bar", show=False)
    plt.savefig("results/xgb_shap_bar.png", bbox_inches="tight")
    plt.close()

    print("SHAP explanation plots saved in results/ folder.")


if __name__ == "__main__":
    explain_xgboost("data/processed/final_with_weather.csv")