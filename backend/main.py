from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.models import (
    ChatRequest,
    ChatResponse
)

from backend.agent import HealthcareAgent


app = FastAPI(
    title="CareConnect AI Healthcare Agent",
     version="1.0.0"
)


app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


agent = HealthcareAgent()


@app.get("/")
def home():

    return {

        "message":
            "CareConnect AI Healthcare Agent API is running"
    }


@app.get("/health")
def health():

    return {

        "status": "healthy"
    }


@app.post(
    "/chat",
    response_model=ChatResponse
)
def chat(
    request: ChatRequest
):

    result = agent.chat(

        session_id=request.session_id,

        message=request.message
    )

    return result