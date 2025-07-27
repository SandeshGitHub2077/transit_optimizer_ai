import pandas as pd
from utils import ask_llm

# Load redundant stop pairs
df = pd.read_csv("redundant_stops_directional.csv")

explanations = []

for _, row in df.iterrows():
    prompt = (
        f"These two stops on Route {row['route_id']} are only {row['distance_m']} meters apart:\n"
        f"- {row['stop_1']}\n"
        f"- {row['stop_2']}\n"
        "Which stop should be kept and why? Suggest merging if appropriate."
    )
    
    explanation = ask_llm(prompt, backend="groq")
    
    explanations.append(explanation)

# Save with reasoning
df["llm_explanation"] = explanations
df.to_csv("redundant_stops_with_llm.csv", index=False)

print("✅ Saved file with LLM suggestions: redundant_stops_with_llm.csv")
