from llm.gemini import ask_gemini


def review_repository(repository_text, user_prompt=""):

    if user_prompt.strip():

        instruction = f"""
The user has requested the following:

{user_prompt}

While reviewing the repository, pay special attention to this request.
"""

    else:

        instruction = """
Perform a complete repository review.

Include:

1. Repository Summary
2. Folder Structure Review
3. Code Quality
4. Possible Bugs
5. Improvement Suggestions
"""

    prompt = f"""
You are a Senior Software Engineer.

{instruction}

Repository:

{repository_text}
"""

    return ask_gemini(prompt)