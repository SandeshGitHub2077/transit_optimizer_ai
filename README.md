# 🚌 Transit Optimization Assistant

This tool helps **NGOs, transit agencies**, or **researchers** analyze GTFS (bus stop) data to:

- 🧮 Detect **redundant bus stops** (too close together)
- 🧭 Identify **underserved areas** (no stop within 400m)
- 🤖 Use **LLMs (via Groq)** to explain what action to take
- 🗺️ Visualize results on an **interactive map**
- 📄 Export results as **CSV** for planning or reporting

---

## 📁 File Structure

```
BUSDATA/
├── .env                         # 🔐 Groq API key
├── app.py                      # 📌 One-click Streamlit UI
├── busDataset_fixed.xlsx       # ✅ GTFS stops with lat/lon
├── gap_detection.py            # 🧭 Detect coverage gaps
├── llm_reasoning.py            # 🤖 LLM suggestions
├── map_visualizer.py           # 🗺️ Optional standalone map generator
├── redundant_stops_directional.py  # 🔁 Redundant stop detector (with direction support)
├── redundant_stops_directional.csv # 📝 Output of redundant stop pairs
├── redundant_stops_with_llm.csv    # 🤖 LLM merge suggestions
├── requirements.txt            # 📦 Dependencies
├── transit_map.html            # 🗺️ Optional static map preview
├── utils.py                    # 🔧 Shared helper functions
│
└── gtfs_data/                  # 📥 Raw GTFS input files
    ├── routes.txt
    ├── stop_times.txt
    ├── stops.txt
    └── trips.txt
```

---

## ✅ Files to Run (In Order)

### 👉 Option 1: One-Click UI (Streamlit)

Just run:

```bash
streamlit run app.py
```

Inside the web app:

1. 📤 Upload `busDataset_fixed.xlsx`
2. 🧮 Click **Detect Redundancies**
3. 🤖 Click **Generate LLM Suggestions**
4. 🧭 Click **Find Gaps**
5. 🗺️ Click **Show Map**
6. 📄 Download CSVs as needed

---

### 👉 Option 2: CLI Mode (Manual Workflow)

```bash
# 1. Detect close stops (same route + direction)
python redundant_stops_directional.py

# 2. Generate merge suggestions via LLM
python llm_reasoning.py

# 3. Find underserved areas
python gap_detection.py

# 4. Generate interactive map (optional)
python map_visualizer.py
```

---

## ⚙️ Requirements

Install all dependencies:

```bash
pip install -r requirements.txt
```

Contents of `requirements.txt`:

```
streamlit
streamlit-folium
pandas
folium
openpyxl
python-dotenv
shapely
requests
```

---

## 🔐 .env Example

Create a `.env` file in the root with your Groq API key:

```env
GROQ_API_KEY=your_groq_key_here
```

---

## 📦 Output Files

| File | Description |
|------|-------------|
| `redundant_stops_directional.csv` | Pairs of stops <125m apart, same route + direction |
| `redundant_stops_with_llm.csv` | Suggested merges with LLM explanations |
| `coverage_gaps.csv` | Areas >400m from nearest stop |
| `transit_map.html` | Optional static map (if not using Streamlit) |
