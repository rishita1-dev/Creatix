from fastapi import FastAPI
from pydantic import BaseModel

from llm.gemini import ask_gemini

app = FastAPI(
    title="Creatix API",
    description="Backend API for Creatix Autonomous Coding Assistant",
    version="1.0"
)


class PromptRequest(BaseModel):
    prompt: str


@app.get("/")
def home():
    return {
        "message": "Welcome to Creatix API"
    }


@app.post("/generate")
def generate_code(request: PromptRequest):

    answer = ask_gemini(request.prompt)

    return {
        "response": answer
    }