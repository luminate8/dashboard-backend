import requests
import os
from dotenv import load_dotenv

load_dotenv()

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

MODELS = [
    "sentence-transformers/all-MiniLM-L6-v2",
    "BAAI/bge-small-en-v1.5",
    "intfloat/multilingual-e5-small"
]

headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

for model_id in MODELS:
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    print(f"\nTrying model: {model_id}")
    try:
        response = requests.post(api_url, headers=headers, json={"inputs": "Test text"}, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            res = response.json()
            if isinstance(res, list):
                if isinstance(res[0], list):
                    print(f"Success! Vector length: {len(res[0])}")
                else:
                    print(f"Success! Vector length: {len(res)}")
                break
            else:
                print(f"Response: {res}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
