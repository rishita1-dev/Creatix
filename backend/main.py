import sys
import os

# --------------------------------------------------
# Add project root to Python path
# --------------------------------------------------

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from agents.pipeline import CreatixPipeline


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

app = FastAPI(
    title="Creatix API",
    description=(
        "Backend API for Creatix Autonomous "
        "AI Coding Assistant"
    ),
    version="1.0"
)


# --------------------------------------------------
# Initialize Pipeline
# --------------------------------------------------

pipeline = CreatixPipeline()


# --------------------------------------------------
# Request Model
# --------------------------------------------------

class PromptRequest(BaseModel):

    task: str

    prompt: str = ""

    repo_url: Optional[str] = None

    conversation_context: Optional[str] = None


# --------------------------------------------------
# Home Endpoint
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "message": "Welcome to Creatix API",
        "status": "running"
    }


# --------------------------------------------------
# Main Creatix Endpoint
# --------------------------------------------------

@app.post("/generate")
def generate(request: PromptRequest):

    try:

        print("\n========== NEW REQUEST ==========")
        print(f"Task: {request.task}")
        print(f"Prompt: {request.prompt}")
        print(f"Repository URL: {request.repo_url}")
        print("=================================\n")


        # ------------------------------------------
        # Basic validation
        # ------------------------------------------

        # ------------------------------------------
# Basic validation
# ------------------------------------------

# Prompt is required for all tasks except Repository Review
        if (
            request.task != "Review GitHub Repository"
            and not request.prompt.strip()
        ):

            return {
                "success": False,
                "error": "Please enter a prompt."
            }


        repository_tasks = [
            "Review GitHub Repository",
            "Repository Q&A (RAG)"
        ]


        if (
            request.task in repository_tasks
            and (
                not request.repo_url
                or not request.repo_url.strip()
            )
        ):

            return {
                "success": False,
                "error": (
                    "Please provide a GitHub "
                    "repository URL."
                )
            }


        # ------------------------------------------
        # Run complete multi-agent pipeline
        # ------------------------------------------

        result = pipeline.run(
            task_type=request.task,
            user_prompt=request.prompt,
            repo_url=request.repo_url,
            conversation_context=(
                request.conversation_context
                or ""
            )
        )


        # ------------------------------------------
        # Handle pipeline failure
        # ------------------------------------------

        if not result.get("success", False):

            return {
                "success": False,
                "error": result.get(
                    "error",
                    "Unknown pipeline error."
                )
            }


        # ------------------------------------------
        # Return complete pipeline result
        # ------------------------------------------

        return {
            "success": True,
            "task": result["task"],
            "selected_task": result["task"],
            "reason": result["reason"],
            "review": result["review"],
            "revised": result["revised"],
            "response": result["response"]
        }


    except Exception as e:

        print("\n========== BACKEND ERROR ==========")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")
        print("===================================\n")

        return {
            "success": False,
            "error": (
                f"{type(e).__name__}: {str(e)}"
            )
        }