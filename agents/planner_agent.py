import os
import json
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()


class PlannerAgent:
    """
    Analyzes a user's coding request and decides
    which specialized Creatix agent should handle it.
    """

    VALID_TASKS = [
        "Generate Code",
        "Explain Code",
        "Debug Code",
        "Review GitHub Repository",
        "Repository Q&A (RAG)",
    ]

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in .env file."
            )

        self.model = genai.GenerativeModel("gemini-3.5-flash")


    def create_plan(self, user_prompt, repo_url=None):
        """
        Analyze the request and return a structured execution plan.
        """

        prompt = f"""
You are the Planner Agent for Creatix, an autonomous coding assistant.

Analyze the user's request and decide which specialized agent should handle it.

Available tasks:

1. Generate Code
   Use when the user wants new code, a feature, function, class, or application.

2. Explain Code
   Use when the user wants existing code explained.

3. Debug Code
   Use when the user reports an error, bug, exception, or broken code.

4. Review GitHub Repository
   Use when the user wants an overall code review of a GitHub repository.

5. Repository Q&A (RAG)
   Use when the user asks a specific question about a GitHub repository.

User request:
{user_prompt}

Repository URL:
{repo_url or "Not provided"}

Return ONLY valid JSON in exactly this format:

{{
    "task": "one exact task name from the available tasks",
    "reason": "short explanation of why this task was selected"
}}
"""

        response = self.model.generate_content(prompt)

        response_text = response.text.strip()

        # Remove possible Markdown code fences
        if response_text.startswith("```"):
            response_text = response_text.replace(
                "```json", ""
            ).replace(
                "```", ""
            ).strip()

        try:
            plan = json.loads(response_text)

        except json.JSONDecodeError:
            raise ValueError(
                f"Planner returned invalid JSON: {response_text}"
            )

        selected_task = plan.get("task")

        if selected_task not in self.VALID_TASKS:
            raise ValueError(
                f"Planner selected invalid task: {selected_task}"
            )

        return plan