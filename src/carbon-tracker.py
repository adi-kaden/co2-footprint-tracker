import os
import requests
from matplotlib import pyplot as plt
import pandas as pd
from typing import Tuple # For type hints
import logging # For logging errors
import requests.exceptions # For handling request exceptions

GOOGLE_API_KEY = "AIzaSyCGYrfLXmt1884HCYV328Qhz2kpfd_Ayh4"
CLIMATIQ_API_KEY = "9DR7XT96QD4CH94TJ6WD5P51P0"

def get_lat_lon(address: str, api_key) -> Tuple[float, float]:
    try:
        url = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {'address': address, 'key': api_key}
        response = requests.get(url, params=params)
        data = response.json()
        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            lat, lng = location['lat'], location['lng']
            return lat, lng
        else:
            raise ValueError(f"Geocoding failed: {data['status']}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error in geocoding: {e}")
        raise

def find_distance(origin_lat, origin_lon, dest_lat, dest_lon, api_key):
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        # Ask only for the fields we need
        "X-Goog-FieldMask": "routes.distanceMeters,routes.duration"
    }
    payload = {
        "origin": {
            "location": {
                "latLng": {"latitude": origin_lat, "longitude": origin_lon}
            }
        },
        "destination": {
            "location": {
                "latLng": {"latitude": dest_lat, "longitude": dest_lon}
            }
        },
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE",
        "computeAlternativeRoutes": False,
        "routeModifiers": {
            "avoidTolls": False,
            "avoidHighways": False,
            "avoidFerries": False
        },
        "units": "METRIC"
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        route = data["routes"][0]
        distance_meters = route["distanceMeters"]
        return distance_meters
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error in distance calculation: {e}")
        raise

def find_co2(distance_km, api_key):
    url = 'https://api.climatiq.io/data/v1/estimate'  # Switch to stable endpoint (beta4 may limit factors)

    headers = {"Authorization": "Bearer " + api_key}

    payload = {
        "emission_factor": {
            "activity_id": "passenger_vehicle-vehicle_type_car-fuel_source_na-engine_size_na-vehicle_age_na-vehicle_weight_na",
            "data_version": "^15",
            "region": "US"
        },
        "parameters": {
            "distance": distance_km,
            "distance_unit": "km"
        }
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        return data['co2e'] / 1000
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

def visualize_data(df):
    fig, ax = plt.subplots()
    plt.plot(df['distance_km'] / 1000, df['co2_kg'] / 1000)
    ax.set_xlabel("Distance travelled (km)")
    ax.set_ylabel("CO2 usage (kg)")
    plt.title("CO2 Emissions vs Distance Travelled")
    plt.savefig('co2_vs_distance.png')

while True:
    start_city = input("Enter name of a city where you started your travels: ").strip()
    if start_city:
        break
    print("Start city cannot be empty. Try again.")

while True:
    end_city = input("Enter name of a city where you ended your travels: ")
    if end_city:
        break
    print("End city cannot be empty. Try again.")

if __name__ == "__main__":
    lat, lon = get_lat_lon(start_city, GOOGLE_API_KEY)
    lat2, lon2 = get_lat_lon(end_city, GOOGLE_API_KEY)
    distance = find_distance(lat, lon, lat2, lon2, GOOGLE_API_KEY)
    co2_usage = find_co2(distance, CLIMATIQ_API_KEY)

    print(f"{start_city} - Latitude: {lat}, Longitude: {lon}")
    print(f"{end_city} - Latitude: {lat2}, Longitude: {lon2}")
    print(f"Distance from {start_city} to {end_city}: {round(distance / 1000, 1)} km")
    print(f"Estimated CO2 emissions for the trip: {round(co2_usage)} kg")

    os.makedirs('./data', exist_ok=True)
    file_path = './data/history.csv'
    columns = ['start_city', 'end_city', 'distance_km', 'co2_kg', 'date']

    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        df = pd.DataFrame(columns=columns)

    data_to_append = {
        'start_city': start_city,
        'end_city': end_city,
        'distance_km': distance,
        'co2_kg': co2_usage,
        'date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    df_new = pd.DataFrame([data_to_append])
    df = pd.concat([df, df_new], ignore_index=True)
    df.to_csv(file_path, index=False)
    visualize_data(df)
    print("Trip data saved to history.csv")