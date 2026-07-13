from agents.planner_agent import PlannerAgent
from agents.repo_qa_agent import RepoQAAgent
from agents.reviewer_agent import ReviewerAgent
from agents.code_generator import generate_code
from agents.code_explainer import explain_code
from agents.code_debugger import debug_code
from agents.github_reviewer import review_repository
import os
from dotenv import load_dotenv
import google.generativeai as genai
load_dotenv()
class AgentRouter:
    """
    Uses the Planner Agent to understand the user's request
    and automatically routes it to the correct specialized agent.
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file.")

        genai.configure(api_key=api_key)

        model = genai.GenerativeModel("gemini-3.5-flash")
        self.planner = PlannerAgent()
        self.repo_qa_agent = RepoQAAgent()
        self.reviewer = ReviewerAgent()

    def route(self, user_prompt, repo_url=None):
        """
        Create a plan, execute the correct specialized agent,
        review the response, and revise it if necessary.
        """

        # Step 1: Ask Planner Agent to classify the task
        plan = self.planner.create_plan(
            user_prompt=user_prompt,
            repo_url=repo_url
        )

        task = plan["task"]
        reason = plan["reason"]

        print(f"Planner selected: {task}")
        print(f"Reason: {reason}")

        # Step 2: Execute the correct specialized agent
        original_response = self._execute_task(
            task=task,
            user_prompt=user_prompt,
            repo_url=repo_url
        )

        print("Original response generated.")

        # Step 3: Ask Reviewer Agent to review the response
        review = self.reviewer.review(
            user_prompt=user_prompt,
            task=task,
            response=original_response
        )

        print(f"Reviewer decision: {review['approved']}")

        # Step 4: If approved, return original response
        if review["approved"]:
            final_response = original_response
            revised = False

        # Step 5: If rejected, improve the response
        else:
            print("Response rejected. Revising...")

            final_response = self._revise_response(
                user_prompt=user_prompt,
                task=task,
                original_response=original_response,
                revision_instructions=review["revision_instructions"]
            )

            revised = True

        # Step 6: Return complete result
        return {
            "task": task,
            "reason": reason,
            "original_response": original_response,
            "review": review,
            "revised": revised,
            "response": final_response
        }
    def _generate_code(self, prompt):
        return generate_code(prompt)

    def _explain_code(self, prompt):
        return explain_code(prompt)

    def _debug_code(self, prompt):
        return debug_code(prompt)
    def _review_repository(self, prompt, repo_url):
        return review_repository(prompt, repo_url)
    def _execute_task(self, task, user_prompt, repo_url=None):
        """
        Execute the correct specialized agent.
        """

        if task == "Generate Code":
            return self._generate_code(user_prompt)

        elif task == "Explain Code":
            return self._explain_code(user_prompt)

        elif task == "Debug Code":
            return self._debug_code(user_prompt)

        elif task == "Review GitHub Repository":

            if not repo_url:
                raise ValueError(
                    "Repository URL is required for repository review."
                )

            return self._review_repository(
                user_prompt,
                repo_url
            )

        elif task == "Repository Q&A (RAG)":

            if not repo_url:
                raise ValueError(
                    "Repository URL is required for Repository Q&A."
                )

            if self.repo_qa_agent.repo_url != repo_url:
                self.repo_qa_agent.load_repository(repo_url)

            return self.repo_qa_agent.ask(user_prompt)

        else:
            raise ValueError(
                f"Unsupported task: {task}"
            )
    def _revise_response(
        self,
        user_prompt,
        task,
        original_response,
        revision_instructions
    ):
        """
        Improve a rejected response using reviewer feedback.
        """

        revision_prompt = f"""
    You are the Revision Agent for Creatix,
    an autonomous coding assistant.

    The original user request was:

    {user_prompt}

    The selected task was:

    {task}

    The original agent response was:

    {original_response}

    The Reviewer Agent rejected this response and provided
    the following revision instructions:

    {revision_instructions}

    Create an improved final response.

    Rules:
    - Follow the reviewer's instructions carefully.
    - Correct technical errors.
    - Preserve correct parts of the original response.
    - Make the response complete and clear.
    - If code is required, provide working code.
    - Return only the improved response.
    """

        model = genai.GenerativeModel("gemini-3.5-flash")

        result = model.generate_content(revision_prompt)

        return result.text