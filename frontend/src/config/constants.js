export const cityData = {
  "Delhi": { coords: { lat: 28.6139, lon: 77.2090 }, historical: [{ month: 'Jan', pm25: 280, risk: 2.8 }, { month: 'Feb', pm25: 240, risk: 2.6 }, { month: 'Mar', pm25: 180, risk: 2.1 }, { month: 'Apr', pm25: 140, risk: 1.8 }, { month: 'Jul', pm25: 80, risk: 1.0 }, { month: 'Oct', pm25: 180, risk: 2.2 }, { month: 'Dec', pm25: 320, risk: 3.2 }]},
  "Mumbai": { coords: { lat: 19.0760, lon: 72.8777 }, historical: [{ month: 'Jan', pm25: 110, risk: 1.5 }, { month: 'Mar', pm25: 95, risk: 1.3 }, { month: 'Jun', pm25: 45, risk: 0.5 }, { month: 'Sep', pm25: 40, risk: 0.5 }, { month: 'Dec', pm25: 130, risk: 1.7 }]},
  "Bengaluru": { coords: { lat: 12.9716, lon: 77.5946 }, historical: [{ month: 'Jan', pm25: 60, risk: 0.8 }, { month: 'Apr', pm25: 75, risk: 1.1 }, { month: 'Jul', pm25: 35, risk: 0.4 }, { month: 'Oct', pm25: 50, risk: 0.7 }, { month: 'Dec', pm25: 70, risk: 1.0 }]},
  "Chennai": { coords: { lat: 13.0827, lon: 80.2707 }, historical: [{ month: 'Jan', pm25: 70, risk: 1.0 }, { month: 'Apr', pm25: 55, risk: 0.7 }, { month: 'Jul', pm25: 40, risk: 0.4 }, { month: 'Oct', pm25: 75, risk: 1.1 }, { month: 'Dec', pm25: 85, risk: 1.2 }]},
  "Hyderabad": { coords: { lat: 17.3850, lon: 78.4867 }, historical: [{ month: 'Jan', pm25: 80, risk: 1.1 }, { month: 'Apr', pm25: 95, risk: 1.4 }, { month: 'Jul', pm25: 50, risk: 0.7 }, { month: 'Oct', pm25: 70, risk: 1.0 }, { month: 'Dec', pm25: 90, risk: 1.3 }]},
  "Kolkata": { coords: { lat: 22.5726, lon: 88.3639 }, historical: [{ month: 'Jan', pm25: 220, risk: 2.5 }, { month: 'Apr', pm25: 130, risk: 1.5 }, { month: 'Jul', pm25: 60, risk: 0.8 }, { month: 'Oct', pm25: 160, risk: 1.8 }, { month: 'Dec', pm25: 240, risk: 2.7 }]},
  "Pune": { coords: { lat: 18.5204, lon: 73.8567 }, historical: [{ month: 'Jan', pm25: 90, risk: 1.2 }, { month: 'Apr', pm25: 85, risk: 1.1 }, { month: 'Jul', pm25: 45, risk: 0.6 }, { month: 'Oct', pm25: 75, risk: 1.0 }, { month: 'Dec', pm25: 110, risk: 1.4 }]}
};

export const metrics = {
  pollutants: [
    { key: "PM2_5", label: "PM2.5", min: 0, max: 500, step: 1, unit: "µg/m³" },
    { key: "PM10", label: "PM10", min: 0, max: 500, step: 1, unit: "µg/m³" },
    { key: "NO2", label: "NO2", min: 0, max: 200, step: 1, unit: "µg/m³" },
    { key: "SO2", label: "SO2", min: 0, max: 100, step: 0.1, unit: "µg/m³" },
    { key: "CO", label: "CO", min: 0, max: 50, step: 0.1, unit: "mg/m³" },
    { key: "O3", label: "O3", min: 0, max: 200, step: 1, unit: "µg/m³" },
  ],
  weather: [
    { key: "Temperature", label: "Temperature", min: -10, max: 50, step: 0.5, unit: "°C", icon: "Thermometer" },
    { key: "WindSpeed", label: "Wind Speed", min: 0, max: 100, step: 1, unit: "km/h", icon: "Wind" },
    { key: "Precipitation", label: "Precipitation", min: 0, max: 50, step: 0.1, unit: "mm", icon: "Droplets" },
  ]
};
