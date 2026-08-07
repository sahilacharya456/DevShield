import os
from dotenv import load_dotenv

# Load from .env if running standalone
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

import google.generativeai as genai

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("[ERROR] GEMINI_API_KEY is not set in environment!")
    exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash')

try:
    response = model.generate_content("Hello! Give me a 3 word response.")
    print("[SUCCESS] Gemini API is working properly!")
    print("Response:", response.text)
except Exception as e:
    print("[ERROR] Failed to connect to Gemini API:")
    print(e)
