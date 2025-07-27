import pandas as pd
import numpy as np
from utils import haversine  # still used for single distance fallback if needed

# Vectorized Haversine for arrays
def haversine_np(lat1, lon1, lat2_array, lon2_array):
    R = 6371000  # Earth radius in meters
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2_array = np.radians(lat2_array)
    lon2_array = np.radians(lon2_array)

    dlat = lat2_array - lat1
    dlon = lon2_array - lon1

    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2_array) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    return R * c  # array of distances in meters

# Load the fixed GTFS stops file
df = pd.read_excel("busDataset_fixed.xlsx")

# Define bounding box with margin
lat_margin = 0.05
lon_margin = 0.05
min_lat = df["stop_lat"].min() - lat_margin
max_lat = df["stop_lat"].max() + lat_margin
min_lon = df["stop_lon"].min() - lon_margin
max_lon = df["stop_lon"].max() + lon_margin

# Generate grid points (~400m spacing)
lat_range = np.arange(min_lat, max_lat, 0.004)
lon_range = np.arange(min_lon, max_lon, 0.004)

stop_lats = df["stop_lat"].to_numpy()
stop_lons = df["stop_lon"].to_numpy()

gap_points = []
for lat in lat_range:
    for lon in lon_range:
        dists = haversine_np(lat, lon, stop_lats, stop_lons)
        min_dist = np.min(dists)
        if min_dist > 400:  # 400 meters
            gap_points.append({
                "lat": lat,
                "lon": lon,
                "min_distance": round(min_dist, 2)
            })

# Save to CSV
gaps_df = pd.DataFrame(gap_points)
gaps_df.to_csv("coverage_gaps.csv", index=False)

print(f"✅ Saved {len(gaps_df)} coverage gaps.")
