from llm.gemini import ask_gemini


def explain_code(user_prompt):

    prompt = f"""
You are an expert programming teacher.

Explain the following code in simple language.

Code:

{user_prompt}
"""

    return ask_gemini(prompt)