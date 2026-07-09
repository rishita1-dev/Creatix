import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Read API Key
API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=API_KEY)

# Load Gemini Model
model = genai.GenerativeModel("gemini-2.5-flash")


def ask_gemini(prompt):
    """
    Sends a prompt to Gemini and returns the response.
    """

    response = model.generate_content(prompt)

    return response.text


if __name__ == "__main__":

    user_prompt = input("Ask Creatix: ")

    answer = ask_gemini(user_prompt)

    print("\n")
    print("Creatix")
    print("--------------------------------")
    print(answer)