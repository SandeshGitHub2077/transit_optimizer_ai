import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from utils import haversine, ask_llm
import numpy as np
import os

st.set_page_config(page_title="Transit Optimization App", layout="wide")
st.title("🚌 Transit Optimization Assistant")

uploaded = st.file_uploader("📤 Upload your GTFS-based stop file (busDataset_fixed.xlsx)", type="xlsx")

if uploaded:
    df = pd.read_excel(uploaded)
    st.success("✅ File uploaded and loaded!")
    st.dataframe(df.head(), use_container_width=True)

    # Redundancy Check
    st.header("🧮 Detect Redundancies (<100m)")
    if st.button("🟠 Run Redundancy Check"):
        from itertools import combinations
        results = []
        for route, group in df.groupby("route_short_name"):
            stops = group.reset_index(drop=True)
            for i, j in combinations(range(len(stops)), 2):
                lat1, lon1 = stops.loc[i, ["stop_lat", "stop_lon"]]
                lat2, lon2 = stops.loc[j, ["stop_lat", "stop_lon"]]
                dist = haversine(lat1, lon1, lat2, lon2)
                if dist < 100:
                    results.append({
                        "route": route,
                        "stop_1": stops.loc[i, "stop_name"],
                        "stop_2": stops.loc[j, "stop_name"],
                        "distance_m": round(dist, 2)
                    })
        red_df = pd.DataFrame(results)
        red_df.to_csv("redundant_stops.csv", index=False)
        st.session_state.redundant_df = red_df
        st.success(f"🟠 Found {len(red_df)} redundant stop pairs.")
        st.dataframe(red_df)

    # LLM Suggestions
    if "redundant_df" in st.session_state:
        st.header("🤖 LLM Merge Suggestions")
        if st.button("Generate LLM Suggestions"):
            explanations = []
            for _, row in st.session_state.redundant_df.iterrows():
                prompt = f"These two stops on Route {row['route']} are only {row['distance_m']} meters apart:\n- {row['stop_1']}\n- {row['stop_2']}\nWhich stop should be kept and why?"
                reply = ask_llm(prompt)
                explanations.append(reply)
            st.session_state.redundant_df["llm_explanation"] = explanations
            st.session_state.redundant_df.to_csv("redundant_stops_with_llm.csv", index=False)
            st.success("✅ Suggestions saved to 'redundant_stops_with_llm.csv'")
            st.dataframe(st.session_state.redundant_df)

    # Gap Detection
    st.header("🧭 Find Coverage Gaps (>400m)")
    if st.button("🟢 Find Gaps"):
        lat_steps = np.linspace(df["stop_lat"].min(), df["stop_lat"].max(), 50)
        lon_steps = np.linspace(df["stop_lon"].min(), df["stop_lon"].max(), 50)
        gap_points = []
        for lat in lat_steps:
            for lon in lon_steps:
                dists = df.apply(lambda row: haversine(lat, lon, row["stop_lat"], row["stop_lon"]), axis=1)
                if dists.min() > 400:
                    gap_points.append({"lat": lat, "lon": lon, "min_distance": dists.min()})
        gap_df = pd.DataFrame(gap_points)
        gap_df.to_csv("coverage_gaps.csv", index=False)
        st.session_state.gap_df = gap_df
        st.success(f"🟢 Found {len(gap_df)} underserved gap locations.")
        st.dataframe(gap_df)

    # Map
    st.header("🗺️ Show Map")
    if st.button("View Map"):
        m = folium.Map(location=[df["stop_lat"].median(), df["stop_lon"].median()], zoom_start=12)

        # Regular stops
        for _, row in df.iterrows():
            folium.CircleMarker(
                location=[row["stop_lat"], row["stop_lon"]],
                radius=4,
                color="blue",
                fill=True,
                fill_opacity=0.6,
                popup=row["stop_name"]
            ).add_to(m)

        # Redundant pairs
        if "redundant_df" in st.session_state:
            for _, row in st.session_state.redundant_df.iterrows():
                s1 = df[df["stop_name"] == row["stop_1"]]
                s2 = df[df["stop_name"] == row["stop_2"]]
                if not s1.empty and not s2.empty:
                    lat1, lon1 = s1.iloc[0][["stop_lat", "stop_lon"]]
                    lat2, lon2 = s2.iloc[0][["stop_lat", "stop_lon"]]
                    folium.PolyLine(
                        locations=[[lat1, lon1], [lat2, lon2]],
                        color="orange",
                        weight=3,
                        popup=row.get("llm_explanation", "")
                    ).add_to(m)

        # Gap markers
        if "gap_df" in st.session_state:
            for _, row in st.session_state.gap_df.iterrows():
                folium.Marker(
                    location=[row["lat"], row["lon"]],
                    icon=folium.Icon(color="green", icon="plus", prefix="fa"),
                    popup=f"Gap > {int(row['min_distance'])}m"
                ).add_to(m)

        # Legend
        legend_html = '''
         <div style="position: fixed; bottom: 50px; left: 50px; width: 200px; height: 120px; 
                     background-color: white; z-index:9999; font-size:14px;
                     border:2px solid grey; padding: 10px;">
         <b>🗺️ Legend</b><br>
         🔵 Regular Stop<br>
         🟠 Merge Candidate<br>
         ➕ Coverage Gap
         </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        st_folium(m, width=1000, height=600)

    # CSV Download Buttons
    st.header("📄 Download Reports")
    if "redundant_df" in st.session_state:
        st.download_button("📥 Download Merge Suggestions CSV", data=st.session_state.redundant_df.to_csv(index=False), file_name="redundant_stops_with_llm.csv")
    if "gap_df" in st.session_state:
        st.download_button("📥 Download Gap Locations CSV", data=st.session_state.gap_df.to_csv(index=False), file_name="coverage_gaps.csv")
