import pandas as pd
import numpy as np


def clean_data(df):
    """
    Basic cleaning with time-respecting imputation.

    - Ensure Date is datetime
    - Sort within each city chronologically
    - Forward-fill missing values within each city only
      (no back-filling to avoid using future information)
    """
    df = df.copy()

    # Handle Date column safely
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])

    # Sort chronologically when possible
    if "City" in df.columns and "Date" in df.columns:
        df = df.sort_values(["City", "Date"])
    elif "Date" in df.columns:
        df = df.sort_values("Date")

    # Forward-fill within each city; do not back-fill so that
    # early missing values do not borrow information from the future.
    if "City" in df.columns:
        df = df.groupby("City", group_keys=False).apply(lambda x: x.ffill())
    else:
        df = df.ffill()

    return df


def create_rhri(df):

    limits = {
        "PM2.5": 15,
        "PM10": 45,
        "NO2": 25,
        "SO2": 40,
        "O3": 100,
        "CO": 4
    }

    rhri_sum = 0
    count = 0

    for pollutant, limit in limits.items():
        if pollutant in df.columns:
            df[f"{pollutant}_norm"] = df[pollutant] / limit
            rhri_sum += df[f"{pollutant}_norm"]
            count += 1

    df["RHRI"] = rhri_sum / count
    df["Risk_Percentage"] = np.clip(df["RHRI"] / 3, 0, 1) * 100

    return df


def classify_rhri(df):

    conditions = [
        df["RHRI"] < 1,
        (df["RHRI"] >= 1) & (df["RHRI"] < 2),
        df["RHRI"] >= 2
    ]

    categories = [0, 1, 2]  # Low, Moderate, High

    df["Respiratory_Risk"] = np.select(conditions, categories)

    return df