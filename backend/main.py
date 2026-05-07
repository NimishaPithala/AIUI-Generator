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

PLANNER_MODEL = "llama-3.1-8b-instant"
GENERATOR_MODEL = "llama-3.1-8b-instant"

# =========================
# REQUEST MODEL
# =========================

class PromptRequest(BaseModel):
    prompt: str

# =========================
# PLANNER PROMPT
# =========================

PLANNER_PROMPT = """
You are an expert educational UI/UX planner and instructional designer.

Your job is to analyze the user's request and produce a DETAILED, SPECIFIC instruction
for a React engineer to build a highly interactive, visually rich educational UI component.

Your instruction MUST include:

1. TOPIC ANALYSIS - What exactly the user wants to learn/explore
2. COMPONENT TYPE - What kind of UI best suits this (map with hover states, flashcards, 
   calculator with live results, timeline, quiz, diagram, chart, table with filters, etc.)
3. DATA - List ALL the actual real data to include (e.g., all 28 Indian states with capitals,
   all elements in periodic table, actual chemical formulas, real historical dates, etc.)
4. INTERACTIONS - Specific hover, click, filter, animate behaviors
5. VISUAL DESIGN - Color scheme, layout, cards, icons using only inline styles + Tailwind
6. SECTIONS - What distinct sections/panels the component should have

Be VERY specific with real data. If the topic is Indian states, list all states.
If it's planets, list all planets with real facts. Always include real, accurate data.

Output ONLY the instruction text, no preamble.
"""

# =========================
# UI GENERATOR PROMPT
# =========================

UI_GENERATOR_SYSTEM_PROMPT = """
You are an expert React engineer who creates STUNNING, HIGHLY INTERACTIVE educational UI components.

You MUST follow these STRICT technical rules:
- Return ONLY raw JSX code — NO markdown fences, NO ```jsx, NO explanations
- NO import statements of any kind
- NO export default
- Use React.useState, React.useEffect, React.useRef, React.useMemo
- Use className (NOT class)
- Inline styles are allowed and encouraged for dynamic values
- NO external libraries — pure React + inline styles + Tailwind classes only
- Component name MUST be App
- End with exactly: render(<App />);

DESIGN RULES — make it look PREMIUM like a real product:
- Use a soft light background: bg-gradient-to-br from-slate-50 to-blue-50
- Cards with white background, rounded-2xl, shadow-lg, border border-gray-100
- Hover effects using React.useState for hovered item tracking
- Active/selected states with vivid color (blue-500, purple-500, etc.)
- Smooth transitions: transition-all duration-200
- Typography: font-bold for headings, text-gray-600 for secondary text
- Use emoji icons naturally (🗺️ 🧪 🔬 📊 etc.) — no icon libraries needed
- Grid layouts: grid grid-cols-2 gap-4 or grid grid-cols-3 gap-3
- All data MUST be hardcoded as const arrays/objects inside the component

INTERACTION RULES:
- Every item must be clickable and show a detail panel or expand
- Hover states must change background color
- Selected states must show vivid highlight
- If it's a map topic → render an SVG-based visual or rich grid of states with click-to-expand
- If it's calculations → show live updating results
- If it's chemistry → show molecules/equations visually
- Always include a search/filter bar if there are more than 8 items
- Include at least one animated element (pulse, bounce, fade-in)

The component must be COMPLETE and FULLY FUNCTIONAL with all real data embedded.
It must look like a polished app, not a demo.

End with:
render(<App />);
"""

# =========================
# ROOT
# =========================

@app.get("/")
def home():
    return {"message": "Backend running"}

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
            model=PLANNER_MODEL,
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
            temperature=0.6,
            max_tokens=1200
        )

        planner_instruction = (
            planner.choices[0]
            .message
            .content
        )

        print("PLANNER SUCCESS")
        print("Instruction:", planner_instruction[:300])

        # =========================
        # UI GENERATOR CALL
        # =========================

        print("Calling UI generator...")

        generator = client.chat.completions.create(
            model=GENERATOR_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": UI_GENERATOR_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": f"""
Build a complete, stunning React component based on this plan:

{planner_instruction}

CRITICAL REQUIREMENTS:
- Include ALL the real data mentioned
- Make every single item interactive (hover + click)
- Add a search/filter bar if there are many items
- Show a detail/info panel when an item is clicked
- Use beautiful card-based layouts
- Add smooth hover color transitions
- The component must be visually polished and complete
- End with render(<App />);
"""
                }
            ],
            temperature=0.5,
            max_tokens=4000
        )

        generated_code = (
            generator.choices[0]
            .message
            .content
        )

        print("GENERATOR SUCCESS")
        print("Code length:", len(generated_code))

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
