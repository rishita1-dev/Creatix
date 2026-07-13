import os

from dotenv import load_dotenv
import google.generativeai as genai

from agents.planner_agent import PlannerAgent
from agents.repo_qa_agent import RepoQAAgent
from agents.reviewer_agent import ReviewerAgent

from agents.code_generator import generate_code
from agents.code_explainer import explain_code
from agents.code_debugger import debug_code
from agents.github_reviewer import review_repository


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()


class AgentRouter:
    """
    Routes user requests to the correct specialized agent.

    If task_type is "Auto", the Planner Agent automatically
    decides which specialized agent should handle the request.

    After execution, the Reviewer Agent checks the response.
    If rejected, the response is revised.
    """

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in .env file."
            )

        genai.configure(api_key=api_key)

        self.planner = PlannerAgent()
        self.repo_qa_agent = RepoQAAgent()
        self.reviewer = ReviewerAgent()


    # --------------------------------------------------
    # Main routing method
    # --------------------------------------------------

    def route(
        self,
        task_type,
        user_prompt,
        repo_url=None
    ):
        """
        Route the request, execute the correct agent,
        review the response, and revise it if necessary.
        """

        # ----------------------------------------------
        # Step 1: Determine task
        # ----------------------------------------------

        if task_type == "Auto":

            plan = self.planner.create_plan(
                user_prompt=user_prompt,
                repo_url=repo_url
            )

            task = plan["task"]
            reason = plan["reason"]

        else:

            task = task_type
            reason = (
                f"User manually selected the '{task}' task."
            )


        print("\n========== CREATIX ROUTER ==========")
        print(f"Selected task: {task}")
        print(f"Reason: {reason}")
        print("====================================\n")


        # ----------------------------------------------
        # Step 2: Execute specialized agent
        # ----------------------------------------------

        original_response = self._execute_task(
            task=task,
            user_prompt=user_prompt,
            repo_url=repo_url
        )

        print("Original response generated successfully.")


        # ----------------------------------------------
        # Step 3: Reviewer Agent checks response
        # ----------------------------------------------

        review = self.reviewer.review(
            user_prompt=user_prompt,
            task=task,
            response=original_response
        )

        print(
            f"Reviewer decision: {review['approved']}"
        )


        # ----------------------------------------------
        # Step 4: Approve or revise response
        # ----------------------------------------------

        if review["approved"]:

            final_response = original_response
            revised = False

        else:

            print("Response rejected. Revising...")

            final_response = self._revise_response(
                user_prompt=user_prompt,
                task=task,
                original_response=original_response,
                revision_instructions=review[
                    "revision_instructions"
                ]
            )

            revised = True


        # ----------------------------------------------
        # Step 5: Return complete result
        # ----------------------------------------------

        return {
            "task": task,
            "reason": reason,
            "original_response": original_response,
            "review": review,
            "revised": revised,
            "response": final_response
        }


    # --------------------------------------------------
    # Execute selected task
    # --------------------------------------------------

    def _execute_task(
        self,
        task,
        user_prompt,
        repo_url=None
    ):

        if task == "Generate Code":

            return generate_code(user_prompt)


        elif task == "Explain Code":

            return explain_code(user_prompt)


        elif task == "Debug Code":

            return debug_code(user_prompt)


        elif task == "Review GitHub Repository":

            if not repo_url or not repo_url.strip():

                raise ValueError(
                    "Repository URL is required "
                    "for repository review."
                )

            return review_repository(
                user_prompt,
                repo_url.strip()
            )


        elif task == "Repository Q&A (RAG)":

            if not repo_url or not repo_url.strip():

                raise ValueError(
                    "Repository URL is required "
                    "for Repository Q&A."
                )

            clean_repo_url = repo_url.strip()

            # Load repository only when necessary
            current_repo = getattr(
                self.repo_qa_agent,
                "repo_url",
                None
            )

            if current_repo != clean_repo_url:

                self.repo_qa_agent.load_repository(
                    clean_repo_url
                )

            return self.repo_qa_agent.ask(
                user_prompt
            )


        else:

            raise ValueError(
                f"Unsupported task: {task}"
            )


    # --------------------------------------------------
    # Revise rejected response
    # --------------------------------------------------

    def _revise_response(
        self,
        user_prompt,
        task,
        original_response,
        revision_instructions
    ):

        revision_prompt = f"""
You are the Revision Agent for Creatix,
an autonomous AI coding assistant.

Original user request:
{user_prompt}

Selected task:
{task}

Original agent response:
{original_response}

The Reviewer Agent rejected the response.

Revision instructions:
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

        model = genai.GenerativeModel(
            "gemini-3.5-flash"
        )

        result = model.generate_content(
            revision_prompt
        )

        return result.text