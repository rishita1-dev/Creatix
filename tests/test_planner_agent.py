from agents.planner_agent import PlannerAgent


planner = PlannerAgent()


test_prompts = [
    "Create a Python function to check whether a number is prime.",

    "Explain what this Python function does.",

    "My code gives a ModuleNotFoundError. Help me fix it.",

    "Review my complete GitHub repository and suggest improvements.",

    "How does authentication work in this GitHub repository?",
]


for prompt in test_prompts:

    print("\n" + "=" * 60)
    print("User prompt:", prompt)

    try:
        plan = planner.create_plan(
            user_prompt=prompt,
            repo_url="https://github.com/example/project"
        )

        print("Selected task:", plan["task"])
        print("Reason:", plan["reason"])

    except Exception as e:
        print("Error:", str(e))