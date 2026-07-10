from llm.gemini import ask_gemini


def debug_code(user_prompt):

    prompt = f"""
You are an expert software debugger.

Find bugs in this code.

Explain the issue.

Provide corrected code.

Code:

{user_prompt}
"""

    return ask_gemini(prompt)