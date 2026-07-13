from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from agents.code_generator import generate_code
from agents.code_explainer import explain_code
from agents.code_debugger import debug_code

from github_tools.github_api import get_repository, get_repository_content
from agents.github_reviewer import review_repository

from agents.repo_qa_agent import RepoQAAgent
from agents.agent_router import AgentRouter
agent_router = AgentRouter()
repo_qa_agent = RepoQAAgent()
import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from agents.pipeline import CreatixPipeline

app = FastAPI(
    title="Creatix API",
    description="Backend API for Creatix Autonomous Coding Assistant",
    version="1.0"
)

pipeline = CreatixPipeline()

class PromptRequest(BaseModel):
    task: str
    prompt: str=""
    repo_url: Optional[str] = None


@app.get("/")
def home():
    return {
        "message": "Welcome to Creatix API"
    }


@app.post("/generate")
def generate(request: PromptRequest):
    if request.task == "Auto":
        result = pipeline.run(
            user_prompt=request.prompt,
            repo_url=request.repo_url
        )

        return {
            "response": result["response"],
            "selected_task": result["task"],
            "reason": result["reason"]
        }
    if request.task == "Generate Code":
        answer = generate_code(request.prompt)

    elif request.task == "Explain Code":
        answer = explain_code(request.prompt)

    elif request.task == "Debug Code":
        answer = debug_code(request.prompt)
    
    elif request.task == "Review GitHub Repository":

        try:
            print("\n--- GITHUB REVIEW STARTED ---")

            # 1. Get and clean repository URL
            repo_url = request.repo_url.strip()

            print("STEP 1 - Received URL:", repr(repo_url))

            if not repo_url:
                answer = "Error: Please provide a GitHub repository URL."

            else:
                # 2. Extract owner and repository name
                parts = repo_url.rstrip("/").split("/")

                print("STEP 2 - URL parts:", parts)

                if len(parts) < 2:
                    raise ValueError("Invalid GitHub repository URL")

                owner = parts[-2]
                repo_name = parts[-1]

                full_repo_name = f"{owner}/{repo_name}"

                print("STEP 3 - Full repository name:", full_repo_name)

                # 3. Fetch repository
                repo = get_repository(full_repo_name)

                print("STEP 4 - Repository fetched successfully")

                # 4. Read repository files
                repository_text = get_repository_content(repo)

                print("STEP 5 - Repository content fetched")
                print("Repository content length:", len(repository_text))

                # 5. Send repository content for AI review
                answer = review_repository(repository_text)

                print("STEP 6 - AI review completed successfully")

        except Exception as e:
            print("\n========== ACTUAL GITHUB REVIEW ERROR ==========")
            print("Error type:", type(e).__name__)
            print("Error message:", str(e))
            print("Full error:", repr(e))
            print("================================================\n")

            answer = f"GitHub review failed: {type(e).__name__}: {str(e)}"    

    elif request.task == "Repository Q&A (RAG)":

        try:
            print("\n--- REPOSITORY Q&A STARTED ---")

            repo_url = request.repo_url.strip()

            if not repo_url:
                answer = "Error: Please provide a GitHub repository URL."

            elif not request.prompt.strip():
                answer = "Error: Please enter a question."

            else:
                print("Loading repository...")

                stats = repo_qa_agent.load_repository(repo_url)

                print(stats)

                print("Repository loaded successfully.")

                answer = repo_qa_agent.ask(request.prompt)

        except Exception as e:

            print("\n========== REPOSITORY Q&A ERROR ==========")
            print(type(e).__name__)
            print(str(e))
            print("==========================================")

            answer = f"Repository Q&A failed: {type(e).__name__}: {str(e)}"

    return {
        "response": answer
    }