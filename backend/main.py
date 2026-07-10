from fastapi import FastAPI
from pydantic import BaseModel

from agents.code_generator import generate_code
from agents.code_explainer import explain_code
from agents.code_debugger import debug_code

from github_tools.github_api import get_repository, get_repository_content
from agents.github_reviewer import review_repository

app = FastAPI(
    title="Creatix API",
    description="Backend API for Creatix Autonomous Coding Assistant",
    version="1.0"
)


class PromptRequest(BaseModel):
    task: str
    prompt: str=""
    repo_url: str=""


@app.get("/")
def home():
    return {
        "message": "Welcome to Creatix API"
    }


@app.post("/generate")
def generate(request: PromptRequest):

    if request.task == "Generate Code":
        answer = generate_code(request.prompt)

    elif request.task == "Explain Code":
        answer = explain_code(request.prompt)

    elif request.task == "Debug Code":
        answer = debug_code(request.prompt)
    
    elif request.task == "Review GitHub Repository":

        if not request.repo_url:
            return {"response": "Please provide a GitHub repository URL."}

        repo_url = request.repo_url.rstrip("/")

        parts = repo_url.split("/")

        if len(parts) < 2:
            return {"response": "Invalid GitHub repository URL."}

        owner = parts[-2]
        repo_name = parts[-1]

        full_repo_name = f"{owner}/{repo_name}"

        repo = get_repository(full_repo_name)

        repository_text = get_repository_content(repo)

        result = review_repository(repository_text)

    else:
        answer = "Feature coming soon."

    return {
        "response": answer
    }