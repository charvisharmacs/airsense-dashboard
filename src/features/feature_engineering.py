import pandas as pd


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Time-series-safe feature engineering for air quality + weather data.

    - Enforces chronological ordering (per city when available)
    - Adds pollutant lag features (1, 3, 7 days)
    - Adds rolling mean and std features (7-day window)
    - Adds simple seasonal features (month, weekday)
    - Adds weather–pollutant interaction features
    - Uses forward-fill only to avoid temporal leakage
    """

    df = df.copy()

    # Ensure datetime handling is consistent
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])

    # Sort chronologically if possible (per-city where available)
    if "City" in df.columns and "Date" in df.columns:
        df = df.sort_values(["City", "Date"])
    elif "Date" in df.columns:
        df = df.sort_values("Date")

    pollutants = ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]

    # Lag features (past pollution levels)
    for col in pollutants:
        if col in df.columns:
            if "City" in df.columns:
                grouped = df.groupby("City")[col]
                df[f"{col}_lag1"] = grouped.shift(1)
                df[f"{col}_lag3"] = grouped.shift(3)
                df[f"{col}_lag7"] = grouped.shift(7)
            else:
                df[f"{col}_lag1"] = df[col].shift(1)
                df[f"{col}_lag3"] = df[col].shift(3)
                df[f"{col}_lag7"] = df[col].shift(7)

    # Rolling statistics (past 7-day pollution trend)
    window = 7
    for col in pollutants:
        if col in df.columns:
            if "City" in df.columns:
                grouped = df.groupby("City")[col]
                df[f"{col}_roll{window}_mean"] = (
                    grouped.rolling(window).mean().reset_index(level=0, drop=True)
                )
                df[f"{col}_roll{window}_std"] = (
                    grouped.rolling(window).std().reset_index(level=0, drop=True)
                )
            else:
                df[f"{col}_roll{window}_mean"] = df[col].rolling(window).mean()
                df[f"{col}_roll{window}_std"] = df[col].rolling(window).std()

    # Calendar time features (safe because derived from timestamp itself)
    if "Date" in df.columns:
        df["Month"] = df["Date"].dt.month
        df["Weekday"] = df["Date"].dt.weekday

    # Weather–pollutant interaction features
    weather_vars = [
        col
        for col in ["Temperature", "Temp_Min", "Temp_Max", "Precipitation", "WindSpeed"]
        if col in df.columns
    ]

    for pol in pollutants:
        if pol in df.columns:
            for w_col in weather_vars:
                df[f"{pol}_x_{w_col}"] = df[pol] * df[w_col]

    # Simple temperature–PM2.5 interaction (kept for backward compatibility)
    if "Temperature" in df.columns and "PM2.5" in df.columns:
        df["Temp_PM25"] = df["Temperature"] * df["PM2.5"]

    # Forward fill only (no backward fill to avoid temporal leakage)
    if "City" in df.columns:
        df = df.groupby("City", group_keys=False).apply(lambda x: x.ffill())
    else:
        df = df.ffill()

    return df