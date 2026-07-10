from llm.gemini import ask_gemini


def generate_code(user_prompt):

    prompt = f"""
You are an expert software engineer.

Generate clean, efficient and well-commented code.

User Request:
{user_prompt}

Only generate the code.
"""

    return ask_gemini(prompt)