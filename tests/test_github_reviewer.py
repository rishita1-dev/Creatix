from github_tools.github_api import get_repository, get_repository_content
from agents.github_reviewer import review_repository


# Step 1: Get the GitHub repository
repo = get_repository("rishita1-dev/Creatix")

# Step 2: Read and combine the repository content
repository_text = get_repository_content(repo)

# Step 3: Send repository content to Gemini for AI review
review = review_repository(repository_text)

# Step 4: Print the AI-generated review
print(review)