from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
import os


# ============================================
# LOAD ENV VARIABLES
# ============================================

load_dotenv()

# ============================================
# GROQ CLIENT
# ============================================

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# ============================================
# MODELS
# ============================================

MODEL_ID = "llama-3.3-70b-versatile"

VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

WHISPER_MODEL = "whisper-large-v3-turbo"

# ============================================
# SYSTEM PROMPTS
# ============================================

PLANNER_SYSTEM_PROMPT = """
You are an AI UI Planning Agent.

Your task:
1. Understand the user request
2. Decide best UI structure
3. Decide best components
4. Decide best interactions
5. Decide styling
6. Generate detailed instructions
   for another AI model.

The second AI model generates React UI.

IMPORTANT:
- Mention cards
- Mention sections
- Mention responsiveness
- Mention TailwindCSS
- Mention animations
- Mention interactivity
- Mention hover effects
- Mention educational structure
- Mention charts/tables if useful

ONLY RETURN THE INSTRUCTION.
"""

"""
UI_GENERATOR_SYSTEM_PROMPT = 
You are an expert React UI engineer.

Generate:
- ONLY React component code
- TailwindCSS styling
- Functional components
- Interactive UI
- Modern dashboard design
- Beautiful educational UI

STRICT RULES:
- Return ONLY code
- No markdown
- No explanations
- Use export default function
- Make component complete
- Use inline sample data
"""

UI_GENERATOR_SYSTEM_PROMPT = """
You are an elite React UI engineer.

Your task:
Generate a BEAUTIFUL and FULLY INTERACTIVE React component.

STRICT RULES:
- Return ONLY React JSX code
- No markdown
- No explanations
- No imports
- No external libraries
- Single component only
- Must work inside react-live
- Use functional component
- Use export default function
- Use inline data only

IMPORTANT UI REQUIREMENTS:
- Use modern TailwindCSS styling
- Use gradients
- Use hover effects
- Use transitions
- Use shadows
- Use rounded cards
- Use responsive layouts
- Use animations with Tailwind classes
- Use flex/grid layouts
- Use attractive colors
- Make UI look professional

INTERACTIVITY REQUIREMENTS:
- Clicking items should update detailed information
- Add hover animations
- Add active states
- Add filtering/search if useful
- Add interactive cards

VERY IMPORTANT:
DO NOT generate fake SVG rectangles.

Instead:
- Create visually meaningful layouts
- Use styled cards/buttons/grids
- Simulate map interactions using positioned UI blocks
- Focus on beautiful UX

MAP REQUIREMENTS:
If user asks for a map:
- Create a visually structured India map layout
- Use clickable state blocks/cards
- Arrange them approximately geographically
- Add hover glow effects
- Add selection animations

The final component MUST look like a polished frontend application.
"""
# ============================================
# FASTAPI APP
# ============================================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# REQUEST MODEL
# ============================================

class UserRequest(BaseModel):
    prompt: str

# ============================================
# HOME ROUTE
# ============================================

@app.get("/")
def home():
    return {
        "message": "AI UI Generator Running"
    }

# ============================================
# LLM #1 → PLANNER
# ============================================

def generate_ui_instruction(user_prompt):

    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {
                "role": "system",
                "content": PLANNER_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0.7,
        max_tokens=1000
    )

    return response.choices[0].message.content

# ============================================
# LLM #2 → UI GENERATOR
# ============================================

def generate_ui_code(instruction):

    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {
                "role": "system",
                "content": UI_GENERATOR_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": instruction
            }
        ],
        temperature=0.5,
        max_tokens=3000
    )

    return response.choices[0].message.content

# ============================================
# MAIN API
# ============================================

@app.post("/generate-ui")
def generate_ui(req: UserRequest):

    # STEP 1 → PLANNER AI

    planner_instruction = generate_ui_instruction(
        req.prompt
    )

    # STEP 2 → UI GENERATOR AI

    generated_code = generate_ui_code(
        planner_instruction
    )

    return {
        "user_prompt": req.prompt,
        "planner_instruction": planner_instruction,
        "generated_code": generated_code
    }
