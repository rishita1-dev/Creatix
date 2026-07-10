from fastapi import FastAPI
from pydantic import BaseModel

from agents.code_generator import generate_code
from agents.code_explainer import explain_code
from agents.code_debugger import debug_code

app = FastAPI(
    title="Creatix API",
    description="Backend API for Creatix Autonomous Coding Assistant",
    version="1.0"
)


class PromptRequest(BaseModel):
    task: str
    prompt: str


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

    else:
        answer = "Feature coming soon."

    return {
        "response": answer
    }