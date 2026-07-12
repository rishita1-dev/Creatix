from agents.agent_router import AgentRouter


router = AgentRouter()


test_prompts = [
    "Create a Python function to check whether a number is prime.",
    "Explain what a Python for loop does.",
    "My Python code gives ModuleNotFoundError. Help me fix it."
]


for prompt in test_prompts:

    print("\n" + "=" * 60)
    print("User prompt:", prompt)

    try:
        result = router.route(user_prompt=prompt)

        print("Selected task:", result["task"])
        print("Reason:", result["reason"])
        print("Response:", result["response"])

    except Exception as e:
        print("Error:", str(e))