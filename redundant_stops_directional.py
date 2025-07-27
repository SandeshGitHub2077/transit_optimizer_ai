import pandas as pd
from utils import haversine
from itertools import combinations

# Load GTFS core files
stop_times = pd.read_csv("gtfs_data/stop_times.txt")
trips = pd.read_csv("gtfs_data/trips.txt")
stops = pd.read_csv("gtfs_data/stops.txt")

# Merge stop_times with trips to get direction info
merged = stop_times.merge(trips[["trip_id", "route_id", "direction_id"]], on="trip_id")

# Ensure stop_id is string in both
merged['stop_id'] = merged['stop_id'].astype(str)
stops['stop_id'] = stops['stop_id'].astype(str)

# Merge with lat/lon from stops.txt using stop_id
merged = merged.merge(
    stops[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']],
    on="stop_id", how="inner"
)

# For each route + direction combo, find close stop pairs
results = []
for (route_id, direction), group in merged.groupby(["route_id", "direction_id"]):
    stops_group = group.drop_duplicates(subset=['stop_id', 'stop_lat', 'stop_lon']).reset_index(drop=True)
    for i, j in combinations(range(len(stops_group)), 2):
        lat1, lon1 = stops_group.loc[i, ["stop_lat", "stop_lon"]]
        lat2, lon2 = stops_group.loc[j, ["stop_lat", "stop_lon"]]
        dist = haversine(lat1, lon1, lat2, lon2)
        if dist < 125:  # relaxed threshold
            results.append({
                "route_id": route_id,
                "direction_id": direction,
                "stop_1": stops_group.loc[i, "stop_name"],
                "stop_2": stops_group.loc[j, "stop_name"],
                "distance_m": round(dist, 2)
            })

# Save results
red_df = pd.DataFrame(results)
red_df.to_csv("redundant_stops_directional.csv", index=False)
print(f"✅ Saved {len(red_df)} directional redundant stop pairs.")
