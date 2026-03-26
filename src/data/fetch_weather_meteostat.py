import os
import time
import pandas as pd
from meteostat import Daily, Stations
from geopy.geocoders import Nominatim


# -----------------------------
# Initialize Geocoder
# -----------------------------
geolocator = Nominatim(user_agent="aqi_weather_project")


def get_coordinates(city_name):
    """
    Automatically get latitude and longitude of city using geopy.
    """

    try:
        location = geolocator.geocode(f"{city_name}, India")
        if location:
            return location.latitude, location.longitude
        else:
            print(f"⚠ Could not geocode {city_name}")
            return None
    except Exception as e:
        print(f"Geocoding error for {city_name}: {e}")
        return None


def fetch_weather_for_city(city_name, start_date, end_date):

    coords = get_coordinates(city_name)

    if coords is None:
        return None

    lat, lon = coords

    # Find nearest weather station
    stations = Stations()
    stations = stations.nearby(lat, lon)
    station = stations.fetch(1)

    if station.empty:
        print(f"⚠ No weather station near {city_name}")
        return None

    station_id = station.index[0]

    data = Daily(station_id, start_date, end_date)
    weather = data.fetch()

    if weather.empty:
        print(f"⚠ No weather data for {city_name}")
        return None

    weather.reset_index(inplace=True)

    weather.rename(columns={
        "time": "Date",
        "tavg": "Temperature",
        "tmin": "Temp_Min",
        "tmax": "Temp_Max",
        "prcp": "Precipitation",
        "wspd": "WindSpeed"
    }, inplace=True)

    return weather


def merge_weather_with_aqi(aqi_path, output_path):

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    df = pd.read_csv(aqi_path)
    df["Date"] = pd.to_datetime(df["Date"])

    final_df = pd.DataFrame()
    cities = df["City"].unique()

    print(f"\nTotal cities found: {len(cities)}")

    for city in cities:

        print(f"\nFetching weather for {city}...")

        city_df = df[df["City"] == city].copy()

        start = city_df["Date"].min()
        end = city_df["Date"].max()

        weather_df = fetch_weather_for_city(city, start, end)

        # Avoid hitting API too fast
        time.sleep(1)

        if weather_df is None:
            continue

        merged = pd.merge(city_df, weather_df, on="Date", how="left")

        final_df = pd.concat([final_df, merged], ignore_index=True)

    final_df.sort_values(["City", "Date"], inplace=True)

    # Fill missing weather values using forward-fill only,
    # and strictly within each city to stay time-series safe.
    weather_cols = ["Temperature", "Temp_Min", "Temp_Max", "Precipitation", "WindSpeed"]

    for col in weather_cols:
        if col in final_df.columns:
            final_df[col] = (
                final_df
                .groupby("City")[col]
                .ffill()
            )

    final_df.to_csv(output_path, index=False)

    print(f"\n✅ Weather merged successfully!")
    print(f"Saved to: {output_path}")
    print(f"Final dataset shape: {final_df.shape}")

if __name__ == "__main__":

    merge_weather_with_aqi(
        aqi_path="data/raw/city_day.csv",
        output_path="data/processed/final_with_weather.csv"
    )
