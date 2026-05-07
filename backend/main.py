# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import os

app = FastAPI()

# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# GROQ CLIENT
# =========================

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL_ID = "llama-3.3-70b-versatile"

# =========================
# REQUEST MODEL
# =========================

class PromptRequest(BaseModel):
    prompt: str

# =========================
# PLANNER PROMPT
# =========================

PLANNER_PROMPT = """
You are an expert UI planner.

Your task:
Convert the user's request into a concise
instruction for a React UI engineer.

Focus on:
- UI structure
- interactivity
- styling
- responsiveness
- educational structure
- animations
- hover effects
- cards
- layouts

Keep instructions concise and useful.
"""

# =========================
# UI GENERATOR PROMPT
# =========================

UI_GENERATOR_SYSTEM_PROMPT = """
You are an elite React UI engineer.

Generate ONLY VALID React JSX code.

STRICT RULES:
- Return ONLY JSX code
- No markdown
- No explanations
- No imports
- No external libraries
- Single component only
- Use export default function
- Must work inside react-live
- Use TailwindCSS only
- Keep code under 250 lines
- Use arrays + map()
- Keep JSX concise

INTERACTIVITY:
- Hover effects
- Click interactions
- Responsive design
- Animated transitions

IMPORTANT:
- Generate COMPLETE valid JSX
- Never cut off code
- Never generate incomplete code
- Avoid huge repetitive JSX blocks

MAP RULES:
- Use simplified interactive layouts
- Use cards/grids/SVG-style regions
- Avoid fake rectangle spam

The component must look modern and professional.
"""

# =========================
# ROOT
# =========================

@app.get("/")
def home():
    return {
        "message": "Backend running"
    }

# =========================
# GENERATE UI
# =========================

@app.post("/generate-ui")
def generate_ui(data: PromptRequest):

    print("===================================")
    print("REQUEST RECEIVED")
    print("Prompt:", data.prompt)
    print("===================================")

    try:

        # =========================
        # PLANNER CALL
        # =========================

        print("Calling planner model...")

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
            max_tokens=700
        )

        planner_instruction = (
            planner.choices[0]
            .message
            .content
        )

        print("PLANNER SUCCESS")

        # =========================
        # UI GENERATOR CALL
        # =========================

        print("Calling UI generator...")

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
            max_tokens=1200
        )

        generated_code = (
            generator.choices[0]
            .message
            .content
        )

        print("GENERATOR SUCCESS")

        return {
            "planner_instruction": planner_instruction,
            "generated_code": generated_code
        }

    except Exception as e:

        print("===================================")
        print("BACKEND ERROR")
        print(str(e))
        print("===================================")

        return {
            "error": str(e)
        }
