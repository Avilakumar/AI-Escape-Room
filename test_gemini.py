
import os
from dotenv import load_dotenv
from google import genai

load_dotenv(override=True)

print("1. Loading API configuration...", flush=True)

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL")

print("2. Model:", model, flush=True)
print("3. API key loaded:", bool(api_key), flush=True)

try:
    client = genai.Client(api_key=api_key)

    print("4. Connecting to Gemini...", flush=True)

    response = client.models.generate_content(
        model=model,
        contents="Say Gemini is working!"
    )

    print("5. SUCCESS:", response.text, flush=True)

except Exception as e:
    print("5. FAILED:", type(e).__name__, flush=True)
    print("ERROR DETAILS:", str(e), flush=True)