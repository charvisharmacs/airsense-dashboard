import joblib
import pandas as pd

from src.features.feature_engineering import create_features


def predict(model_name, input_dict):

    model = joblib.load(f"models/{model_name}.pkl")
    scaler = joblib.load("models/scaler.pkl")
    feature_names = joblib.load("models/feature_names.pkl")

    # Create dataframe from input
    df = pd.DataFrame([input_dict])

    # Fake columns required for feature engineering
    if "City" not in df.columns:
        df["City"] = "SampleCity"

    if "Date" not in df.columns:
        df["Date"] = pd.Timestamp.today()

    # Run feature engineering
    df = create_features(df)

    # Keep only trained features
    df = df.reindex(columns=feature_names, fill_value=0)

    # Scale
    df_scaled = scaler.transform(df)

    # Predict
    prediction = model.predict(df_scaled)[0]
    probability = model.predict_proba(df_scaled)[0]

    return prediction, probability