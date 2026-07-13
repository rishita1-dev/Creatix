import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("\nAvailable Models:\n")

for model in genai.list_models():
    print(model.name)
    print("Supported:", model.supported_generation_methods)
    print("-" * 60)