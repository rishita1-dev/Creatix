from agents.planner_agent import PlannerAgent
from agents.repo_qa_agent import RepoQAAgent


class AgentRouter:
    """
    Uses the Planner Agent to understand the user's request
    and automatically routes it to the correct specialized agent.
    """

    def __init__(self):
        self.planner = PlannerAgent()
        self.repo_qa_agent = RepoQAAgent()

    def route(self, user_prompt, repo_url=None):
        """
        Create a plan and execute the correct agent.
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

        # Step 2: Route to correct specialized agent

        if task == "Generate Code":
            return {
                "task": task,
                "reason": reason,
                "response": self._generate_code(user_prompt)
            }

        elif task == "Explain Code":
            return {
                "task": task,
                "reason": reason,
                "response": self._explain_code(user_prompt)
            }

        elif task == "Debug Code":
            return {
                "task": task,
                "reason": reason,
                "response": self._debug_code(user_prompt)
            }

        elif task == "Review GitHub Repository":
            if not repo_url:
                raise ValueError(
                    "Repository URL is required for repository review."
                )

            return {
                "task": task,
                "reason": reason,
                "response": self._review_repository(
                    user_prompt,
                    repo_url
                )
            }

        elif task == "Repository Q&A (RAG)":
            if not repo_url:
                raise ValueError(
                    "Repository URL is required for Repository Q&A."
                )

            # Don't rebuild index for the same repository
            if self.repo_qa_agent.repo_url != repo_url:
                self.repo_qa_agent.load_repository(repo_url)

            answer = self.repo_qa_agent.ask(user_prompt)

            return {
                "task": task,
                "reason": reason,
                "response": answer
            }

        else:
            raise ValueError(f"Unsupported task: {task}")

    def _generate_code(self, prompt):
        """
        Temporary connection point for your existing
        code-generation agent.
        """
        return (
            "Generate Code selected. "
            "Connect your existing code generator here."
        )

    def _explain_code(self, prompt):
        """
        Temporary connection point for your existing
        code-explanation agent.
        """
        return (
            "Explain Code selected. "
            "Connect your existing code explainer here."
        )

    def _debug_code(self, prompt):
        """
        Temporary connection point for your existing
        debugger agent.
        """
        return (
            "Debug Code selected. "
            "Connect your existing debugger here."
        )

    def _review_repository(self, prompt, repo_url):
        """
        Temporary connection point for your existing
        repository-review agent.
        """
        return (
            "Review GitHub Repository selected. "
            "Connect your existing repository reviewer here."
        )