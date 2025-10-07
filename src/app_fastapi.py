from fastapi import FastAPI
from pydantic import BaseModel
from chat import respond
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

class ChatIn(BaseModel):
    message: str

class ChatOut(BaseModel):
    reply: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatOut)
def chat(inp: ChatIn):
    return ChatOut(reply=respond(inp.message))