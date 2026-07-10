from llm.gemini import ask_gemini


def review_repository(repository_text):

    prompt = f"""
You are a Senior Software Engineer.

Analyze this GitHub repository.

Give:

1. Repository Summary

2. Folder Structure Review

3. Code Quality

4. Possible Bugs

5. Improvement Suggestions

Repository:

{repository_text}
"""

    return ask_gemini(prompt)