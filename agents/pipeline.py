from agents.agent_router import AgentRouter

class CreatixPipeline:
    """
    Main autonomous pipeline for Creatix.
    """

    def __init__(self):
        self.router = AgentRouter()

    def run(self,task_type, user_prompt, repo_url=None):
        """
        Run the complete Creatix agent workflow.
        """

        try:
            result = self.router.route(
                user_prompt=user_prompt,
                repo_url=repo_url,
                task_type=task_type
            )

            return {
                "success": True,
                **result
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }