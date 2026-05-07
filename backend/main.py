"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL = "llama-3.1-8b-instant"


class PromptRequest(BaseModel):
    prompt: str


PLANNER_PROMPT = You are an expert educational UI/UX planner.

Analyse the user request and write a DETAILED, SPECIFIC instruction for a React engineer
to build one self-contained interactive educational UI component.

Your instruction MUST include:

1. COMPONENT TYPE - the best UI for the topic:
   e.g. searchable card grid, interactive timeline, calculator with live output,
   periodic table grid, chemical equation viewer, clickable map grid, quiz, etc.

2. ALL REAL DATA - list every single data item to embed.
   Examples:
   - Indian states: all 36 states/UTs with capital, region, area, language, population
   - Planets: all 8 with distance, diameter, moons, gravity, fun fact
   - Elements: first 20 with symbol, atomic no., category, mass
   Never use placeholders. The engineer hard-codes every item.

3. INTERACTIONS:
   - Hover effect (background colour change)
   - Click → detail panel showing ALL fields for that item
   - Search/filter bar (mandatory when more than 8 items)
   - At least one animated entrance (fade + slide up)

4. VISUAL STYLE (Tailwind only, no external icon libs):
   - White card backgrounds, rounded-2xl, shadow-md
   - Selected item: bg-indigo-600 text-white
   - Unselected hover: hover:bg-indigo-50
   - Page background: bg-gradient-to-br from-slate-50 to-indigo-50
   - Heading: text-2xl font-bold text-gray-800

Output ONLY the instruction. No preamble.


GENERATOR_PROMPT = You are an expert React engineer. Generate ONE complete, self-contained,
interactive React component.

HARD RULES - breaking any of these causes a render error:
1. Output RAW JSX ONLY - absolutely no markdown, no ``` fences, no explanations
2. NO import or require statements of any kind
3. NO export keyword
4. Hooks MUST use React prefix: React.useState React.useEffect React.useRef React.useMemo
5. Use className not class
6. Tailwind utility classes for all styling
7. Inline style={{}} only for truly dynamic values
8. No external libraries
9. Component name must be exactly: App
10. Very last line must be exactly: render();

DESIGN - make it look like a real product:
- Outer div: className="min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50 p-6 font-sans"
- Cards: className="bg-white rounded-2xl shadow-md border border-gray-100 p-4 cursor-pointer transition-all duration-200"
- Selected card: style={{background:'#4338ca',color:'#fff'}}
- Hovered card: track with React.useState(null) for hoveredId, apply bg-indigo-50
- Detail panel: fixed right panel or bottom panel showing ALL fields
- Search bar: 
- Entrance animation: use React.useEffect to set a mounted state, then style={{opacity:mounted?1:0,transform:mounted?'none':'translateY(16px)',transition:'all 0.4s'}}

DATA RULES:
- Hard-code ALL real data as const arrays inside App
- Every item needs at least 5 fields for a rich detail panel
- Never use lorem ipsum or placeholder data

The component must be 100% complete and functional with all data embedded.
End with exactly: render();


@app.get("/")
def root():
    return {"status": "ok", "message": "AI UI Generator backend running"}


@app.post("/generate-ui")
async def generate_ui(req: PromptRequest):
    print(f"\n{'='*60}")
    print(f"PROMPT: {req.prompt}")
    print(f"{'='*60}")

    try:
        # Step 1: Planner
        print("Running planner...")
        plan_res = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": PLANNER_PROMPT},
                {"role": "user", "content": req.prompt},
            ],
            temperature=0.7,
            max_tokens=800,
        )
        plan = plan_res.choices[0].message.content.strip()
        print(f"PLAN ({len(plan)} chars):\n{plan[:300]}...\n")

        # Step 2: Generator
        print("Running generator...")
        gen_res = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": GENERATOR_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Build this component:\n\n{plan}\n\n"
                        "CRITICAL REMINDERS:\n"
                        "- Include every single data item listed above\n"
                        "- Search bar filters in real time\n"
                        "- Click any item to show a full detail panel\n"
                        "- Hover changes background colour\n"
                        "- Use React.useState / React.useEffect (never bare useState)\n"
                        "- No imports, no export, raw JSX only\n"
                        "- Last line: render();"
                    ),
                },
            ],
            temperature=0.4,
            max_tokens=3000,
        )
        code = gen_res.choices[0].message.content.strip()
        print(f"CODE ({len(code)} chars)")

        return {"planner_instruction": plan, "generated_code": code}

    except Exception as e:
        print(f"ERROR: {e}")
        return {"error": str(e)}
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"


class PromptRequest(BaseModel):
    prompt: str


PLANNER_PROMPT = """You are an expert educational UI/UX planner.

Analyse the user request and write a DETAILED instruction for a React engineer
to build one self-contained interactive educational UI component.

Include:
1. COMPONENT TYPE - best UI for the topic (searchable card grid, timeline, calculator,
   periodic table grid, equation viewer, clickable state grid, quiz, etc.)
2. ALL REAL DATA - list every data item to embed with all fields. Never use placeholders.
3. INTERACTIONS - hover colour change, click to open detail panel, search/filter bar
   (mandatory when more than 8 items), entrance animation.
4. VISUAL STYLE - Tailwind only. White cards, rounded-2xl, shadow-md.
   Selected: bg-indigo-600 text-white. Page: bg-gradient-to-br from-slate-50 to-indigo-50.

Output ONLY the instruction. No preamble, no explanation."""


GENERATOR_PROMPT = """You are a React engineer. Output a SINGLE raw JSX component.

═══════════════════════════════════════════════
ABSOLUTE OUTPUT RULES — violating any rule
causes a fatal render crash:
═══════════════════════════════════════════════
1. Your ENTIRE response must be valid JSX/JS code.
   Do NOT write any English sentences, explanations,
   comments like "Here is the code:", or markdown.
2. Do NOT use any ``` fences or markdown at all.
3. Do NOT write any import or require statements.
4. Do NOT use the export keyword anywhere.
5. ALL hooks MUST use React prefix:
     React.useState   React.useEffect
     React.useRef     React.useMemo
   NEVER write bare: useState(  useEffect(
6. Write className=  never  class=
7. No external libraries. Pure React + Tailwind only.
8. Component name must be exactly:  App
9. Your response must start with:   function App() {
10. Do not end with render();
10. Do not give syntax errors. Recheck if there are any syntax errors. - This is a must.

═══════════════════════════════════════════════
DESIGN RULES:
═══════════════════════════════════════════════
Outer wrapper:
  className="min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50 p-6 font-sans"

Cards (each data item):
  className="bg-white rounded-2xl shadow-md border border-gray-100 p-4
             cursor-pointer transition-all duration-200"

Selected card override (inline style):
  style={{background:'#4338ca', color:'#fff'}}

Hover tracking:
  const [hoveredId, setHoveredId] = React.useState(null);
  On each card:  onMouseEnter={() => setHoveredId(item.id)}
                 onMouseLeave={() => setHoveredId(null)}
  When hovered and not selected apply: style={{background:'#eef2ff'}}

Search bar (mandatory when > 8 items):
  className="w-full border border-gray-200 rounded-xl px-4 py-2 mb-4
             text-gray-800 outline-none focus:ring-2 focus:ring-indigo-300"

Detail panel: right-side panel or bottom panel.
  Show ALL fields for the clicked item with labels.
  Include a close button.

Entrance animation:
  const [mounted, setMounted] = React.useState(false);
  React.useEffect(() => { setTimeout(()=>setMounted(true), 50); }, []);
  Outer div: style={{opacity: mounted ? 1 : 0,
                     transform: mounted ? 'none' : 'translateY(16px)',
                     transition: 'all 0.4s ease'}}

═══════════════════════════════════════════════
DATA RULES:
═══════════════════════════════════════════════
- Hard-code ALL data as a const array inside App().
- Every item needs an id field + at least 5 other fields.
- Use real, accurate data. No lorem ipsum.

════════════════════════════════════════════════
START your response with:  function App() {
END   your response with:  render();
════════════════════════════════════════════════"""


@app.get("/")
def root():
    return {"status": "ok", "message": "AI UI Generator backend running"}


@app.post("/generate-ui")
async def generate_ui(req: PromptRequest):
    print(f"\n{'='*60}\nPROMPT: {req.prompt}\n{'='*60}")

    try:
        # ── Step 1: Planner ──
        plan_res = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": PLANNER_PROMPT},
                {"role": "user",   "content": req.prompt},
            ],
            temperature=0.7,
            max_tokens=700,
        )
        plan = plan_res.choices[0].message.content.strip()
        print(f"PLAN:\n{plan[:300]}\n")

        # ── Step 2: Generator ──
        gen_res = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": GENERATOR_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"{plan}\n\n"
                        "REMEMBER:\n"
                        "- Start your response with:  function App() {\n"
                        "- End your response with:    render();\n"
                        "- No imports, no export, no markdown, no explanations.\n"
                        "- All hooks must use React.useState / React.useEffect etc."
                    ),
                },
            ],
            temperature=0.3,
            max_tokens=3000,
        )
        code = gen_res.choices[0].message.content.strip()
        print(f"CODE ({len(code)} chars)")

        return {"planner_instruction": plan, "generated_code": code}

    except Exception as e:
        print(f"ERROR: {e}")
        return {"error": str(e)}
