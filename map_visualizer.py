import pandas as pd
import folium

# Load the main datasets
stops_df = pd.read_excel("busDataset_fixed.xlsx")
redundant_df = pd.read_csv("redundant_stops_with_llm.csv")
gap_df = pd.read_csv("coverage_gaps.csv")

# Center the map on the average location of all stops
center_lat = stops_df["stop_lat"].median()
center_lon = stops_df["stop_lon"].median()
m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

# Plot regular bus stops (blue)
for _, row in stops_df.iterrows():
    folium.CircleMarker(
        location=[row["stop_lat"], row["stop_lon"]],
        radius=4,
        color="blue",
        fill=True,
        fill_opacity=0.6,
        popup=f"Stop: {row['stop_name']}<br>Route: {row['route_short_name']}"
    ).add_to(m)

# Plot redundant stop pairs with orange lines
for _, row in redundant_df.iterrows():
    stop1 = stops_df[stops_df["stop_name"] == row["stop_1"]]
    stop2 = stops_df[stops_df["stop_name"] == row["stop_2"]]

    if not stop1.empty and not stop2.empty:
        lat1, lon1 = stop1.iloc[0][["stop_lat", "stop_lon"]]
        lat2, lon2 = stop2.iloc[0][["stop_lat", "stop_lon"]]

        folium.PolyLine(
            locations=[[lat1, lon1], [lat2, lon2]],
            color="orange",
            weight=3,
            popup=folium.Popup(row["llm_explanation"], max_width=300)
        ).add_to(m)

# Plot gap points with green icons
for _, row in gap_df.iterrows():
    folium.Marker(
        location=[row["lat"], row["lon"]],
        icon=folium.Icon(color="green", icon="plus", prefix="fa"),
        popup=f"Gap: No stop within {int(row['min_distance'])} meters"
    ).add_to(m)

# Add legend box
legend_html = '''
 <div style="position: fixed; 
             bottom: 50px; left: 50px; width: 200px; height: 120px; 
             background-color: white; z-index:9999; font-size:14px;
             border:2px solid grey; padding: 10px;">
 <b>🗺️ Legend</b><br>
 🔵 Regular Stop<br>
 🟠 Merge Candidate<br>
 ➕ Coverage Gap
 </div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Save the output map
m.save("transit_map.html")
print("✅ Map saved to 'transit_map.html'")
