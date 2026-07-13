from agents.reviewer_agent import ReviewerAgent


reviewer = ReviewerAgent()


user_prompt = """
Create a Python function to check whether a number is prime.
"""


task = "Generate Code"


agent_response = """
def is_prime(n):
    return True
"""


print("Original user request:")
print(user_prompt)

print("\nAgent response:")
print(agent_response)

print("\nReviewing response...")

try:
    review = reviewer.review(
        user_prompt=user_prompt,
        task=task,
        response=agent_response
    )

    print("\nReview Result:")
    print("Approved:", review["approved"])
    print("Score:", review["score"])
    print("Feedback:", review["feedback"])
    print(
        "Revision instructions:",
        review["revision_instructions"]
    )

except Exception as e:
    print("\nError:", str(e))