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
        "Innovation Analysis"
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
You are the Planner Agent for Creatix, an AI-powered Student Innovation Platform.

Your job is to understand the student's request and select the most appropriate
existing Creatix capability.

Creatix helps students:

- explore existing technological resources
- understand technologies and code
- identify reusable components
- build prototypes and solutions
- debug and improve solutions
- extract knowledge from repositories
- discover opportunities for further innovation

Available tasks:
1. Innovation Analysis
   Use when the student describes an idea, problem, prototype,
   technology concept, or innovation and wants to understand:

   - the problem
   - relevant technologies
   - existing technological resources
   - how existing resources can be reused or adapted
   - valuable technical insights
   - possible improvements
   - possible innovation opportunities
   - a suggested development path

If the user's request is about developing a new idea or innovation
and they are asking for guidance rather than directly asking for
code, select "Innovation Analysis".


2. Generate Code
Use when the user wants to build a solution, prototype, feature, function,
application, or implementation.

3. Explain Code
Use when the user wants to understand existing code or technology.

4. Debug Code
Use when the user wants to identify and fix errors or improve broken code.

5. Review GitHub Repository
Use when the user wants to explore an existing repository, understand its
structure, evaluate its implementation, identify reusable components, or
discover possible improvements.

6. Repository Q&A (RAG)
Use when the user asks a specific question about an existing repository or
wants knowledge extracted from its codebase.

IMPORTANT FOR INNOVATION REQUESTS:

If the user describes a new idea, societal problem, technology idea, prototype,
or innovation concept, understand the idea first and select the capability
that can provide the most useful next step.

For innovation-related requests, the response should focus on:

- Problem Understanding
- Relevant Technologies
- Existing Resources
- How Existing Resources Can Be Used
- Possible Improvements
- Innovation Opportunities
- Suggested Development Path

Do not invent external resources or claim that Creatix searched the entire
internet unless the user explicitly provides those resources.

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