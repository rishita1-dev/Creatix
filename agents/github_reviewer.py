from llm.gemini import ask_gemini


def review_repository(repository_content):

    prompt = f"""
You are a senior software engineer.

Review the following repository.

Suggest

1. Code Improvements

2. Bugs

3. Better Naming

4. Documentation Improvements

Repository:

{repository_content}
"""

    return ask_gemini(prompt)