from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq

import os

app = FastAPI()

# IMPORTANT
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL_ID = "llama-3.3-70b-versatile"

class PromptRequest(BaseModel):
    prompt: str

PLANNER_PROMPT = """
You are an expert UI planner.

Convert the user request into instructions
for a React UI engineer.
"""

UI_GENERATOR_SYSTEM_PROMPT = """
You are an elite React UI engineer.

Generate ONLY VALID React JSX code.

STRICT RULES:
- Return ONLY code
- No markdown
- No explanations
- No imports
- Single component only
- Use export default function
- Must work in react-live
- Use TailwindCSS only
- No external libraries
- Keep code concise
"""

@app.get("/")
def home():
    return {
        "message": "Backend running"
    }

@app.post("/generate-ui")
def generate_ui(data: PromptRequest):

    # =========================
    # PLANNER
    # =========================

    planner = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {
                "role": "system",
                "content": PLANNER_PROMPT
            },
            {
                "role": "user",
                "content": data.prompt
            }
        ],
        temperature=0.7,
        max_tokens=1000
    )

    planner_instruction = (
        planner.choices[0]
        .message
        .content
    )

    # =========================
    # UI GENERATOR
    # =========================

    generator = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {
                "role": "system",
                "content": UI_GENERATOR_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": planner_instruction
            }
        ],
        temperature=0.7,
        max_tokens=2000
    )

    generated_code = (
        generator.choices[0]
        .message
        .content
    )

    return {
        "planner_instruction": planner_instruction,
        "generated_code": generated_code
    }
