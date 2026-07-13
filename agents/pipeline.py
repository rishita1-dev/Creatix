from agents.agent_router import AgentRouter


class CreatixPipeline:
    """
    Main autonomous pipeline for Creatix.

    The pipeline receives a task from the backend
    and sends it to the AgentRouter.
    """

    def __init__(self):
        self.router = AgentRouter()

    def run(
        self,
        task_type,
        user_prompt,
        repo_url=None
    ):
        """
        Run the complete Creatix multi-agent workflow.

        Parameters:
            task_type:
                Auto,
                Generate Code,
                Explain Code,
                Debug Code,
                Review GitHub Repository,
                Repository Q&A (RAG)

            user_prompt:
                User's coding request or question.

            repo_url:
                Optional GitHub repository URL.

        Returns:
            Dictionary containing the complete pipeline result.
        """

        try:

            result = self.router.route(
                task_type=task_type,
                user_prompt=user_prompt,
                repo_url=repo_url
            )

            return {
                "success": True,
                **result
            }

        except Exception as e:

            return {
                "success": False,
                "error": f"{type(e).__name__}: {str(e)}"
            }