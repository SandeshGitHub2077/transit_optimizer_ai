import math
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load keys from .env if present

# -----------------------------------
# Haversine Distance Function (in meters)
# -----------------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # in meters

# -----------------------------------
# ask_llm() – Get explanation from LLM
# backend: "groq", "huggingface", "ollama"
# -----------------------------------
def ask_llm(prompt: str, backend="groq"):
    if backend == "groq":
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }

        try:
            res = requests.post(url, json=payload, headers=headers, timeout=15)
            res.raise_for_status()
            return res.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"[LLM Error] {str(e)}"

    elif backend == "huggingface":
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        model = "mistralai/Mistral-7B-Instruct-v0.1"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 256}
        }
        try:
            res = requests.post(
                f"https://api-inference.huggingface.co/models/{model}",
                headers=headers, json=payload
            )
            res.raise_for_status()
            return res.json()[0]["generated_text"].strip()
        except Exception as e:
            return f"[LLM Error] {str(e)}"

    elif backend == "ollama":
        try:
            res = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama3", "prompt": prompt, "stream": False}
            )
            return res.json().get("response", "").strip()
        except Exception as e:
            return f"[LLM Error] {str(e)}"

    else:
        return "[LLM Error] Invalid backend specified"
