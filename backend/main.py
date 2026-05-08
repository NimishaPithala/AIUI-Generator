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

Output ONLY the instruction. No preamble, no explanation.


GENERATOR_PROMPT = You are a React engineer. Output a SINGLE raw JSX component.

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
════════════════════════════════════════════════


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


# ─────────────────────────────────────────────────────────────
# PLANNER  — decides component type and full data spec
# ─────────────────────────────────────────────────────────────
PLANNER_PROMPT = """You are an expert educational UI/UX planner.

Analyse the user's request and write a precise instruction for a React/SVG engineer.

COMPONENT TYPE — choose the best fit:
  • CARD GRID      : lists, facts, comparison (planets, elements, countries …)
  • SVG MAP        : any geographic map (India, world, US states …)
  • SVG DIAGRAM    : body systems, cell, atom, machine parts, circuits …
  • TIMELINE       : historical events, processes in order
  • CALCULATOR     : math/science with live inputs and outputs
  • QUIZ           : questions with answers and score
  • CHART/GRAPH    : data visualisation with SVG bars/lines/pie

SVG MAP rules (use when topic is a map):
  - Specify viewBox dimensions, approximate SVG path data for every region,
    each region gets a unique id, fill colour, hover colour, label.
  - List every region with: id, name, capital, population, area, one fun fact.

SVG DIAGRAM rules (use when topic is anatomy / system / mechanism):
  - Describe each organ/part as a simple SVG shape (ellipse, rect, path, circle)
    with x,y,width,height or cx,cy,r or a simple path d="".
  - Label each part. Include a step-by-step process list the user can click
    to highlight the relevant part.

CARD GRID rules (use for everything else):
  - List every data item with ALL fields. No placeholders.
  - Include search bar (mandatory > 8 items).
  - Hover + click-to-expand detail panel.

Output ONLY the instruction. No preamble."""


# ─────────────────────────────────────────────────────────────
# GENERATOR  — strict rules that prevent every known JSX error
# ─────────────────────────────────────────────────────────────
GENERATOR_PROMPT = """You are a React + SVG engineer. Output ONE raw JSX component.

══════════════════════════════════════════════════
ABSOLUTE RULES — breaking any rule = render crash
══════════════════════════════════════════════════
1.  Output ONLY valid JS/JSX. Zero English prose,
    zero markdown, zero ``` fences.
2.  No import / require statements.
3.  No export keyword.
4.  ALL hooks MUST use React prefix:
      React.useState   React.useEffect
      React.useRef     React.useMemo
    NEVER write bare:  useState(   useEffect(
5.  className=  not  class=
6.  No external libraries. React + inline SVG only.
7.  Component name: App
8.  First line of output: function App() {
9.  Last line of output:  render();
10. Every JSX expression inside {} must be valid JS.
    No standalone statements inside JSX.
11. Never use Array methods that return undefined inside JSX
    (.forEach is banned inside JSX — use .map instead).
12. Do NOT use position:absolute for detail panels —
    use conditional rendering in a separate div below the grid.
13. Define data arrays as const INSIDE App() before return().
14. Do NOT initialise filter state as [] — initialise it as
    the full data array: React.useState(dataArray) AFTER
    defining dataArray, or filter inline inside return().

══════════════════════════════════════════════════
DESIGN
══════════════════════════════════════════════════
Page wrapper:
  className="min-h-screen bg-gradient-to-br from-slate-50
             to-indigo-50 p-6 font-sans"

Cards:
  className="bg-white rounded-2xl shadow-md border
             border-gray-100 p-4 cursor-pointer
             transition-all duration-200"

Selected card: style={{background:'#4338ca',color:'#fff'}}
Hovered card:  style={{background:'#eef2ff'}}

Search input:
  className="w-full border border-gray-200 rounded-xl
             px-4 py-2 mb-4 text-gray-800 outline-none
             focus:ring-2 focus:ring-indigo-300"

Detail panel (separate div BELOW the grid, NOT inside card):
  className="bg-white rounded-2xl shadow-xl border
             border-indigo-100 p-6 mt-6"

Entrance animation — add this pattern:
  const [mounted, setMounted] = React.useState(false);
  React.useEffect(() => {
    const t = setTimeout(() => setMounted(true), 50);
    return () => clearTimeout(t);
  }, []);
  Outer div: style={{opacity:mounted?1:0,
                     transform:mounted?'none':'translateY(16px)',
                     transition:'all 0.4s ease'}}

══════════════════════════════════════════════════
SVG MAP pattern (use for any geographic map topic)
══════════════════════════════════════════════════
const regions = [
  { id:'r1', name:'Region Name', path:'M...Z',
    fill:'#a5b4fc', capital:'X', population:'Y', fact:'Z' },
  ...
];
const [hovReg, setHovReg] = React.useState(null);
const [selReg, setSelReg] = React.useState(null);




══════════════════════════════════════════════════
SVG DIAGRAM pattern (use for anatomy / systems)
══════════════════════════════════════════════════
const parts = [
  { id:'p1', name:'Part Name', shape:'ellipse',
    cx:200, cy:150, rx:60, ry:40,
    fill:'#fda4af', desc:'What this part does' },
  ...
];
const [hovPart, setHovPart] = React.useState(null);
const [selPart, setSelPart] = React.useState(null);



══════════════════════════════════════════════════
FILTER PATTERN (no useState [] init bug)
══════════════════════════════════════════════════
// Define data first
const items = [ ...all your data... ];
// Filter inline — NO separate filteredItems state needed
const [search, setSearch] = React.useState('');
const visible = search
  ? items.filter(i => i.name.toLowerCase().includes(search.toLowerCase()))
  : items;
// Then in JSX: visible.map(...)

══════════════════════════════════════════════════
START output with:  function App() {
END   output with:  render();
══════════════════════════════════════════════════"""


@app.get("/")
def root():
    return {"status": "ok", "message": "Backend running"}


@app.post("/generate-ui")
async def generate_ui(req: PromptRequest):
    print(f"\n{'='*60}\nPROMPT: {req.prompt}\n{'='*60}")

    try:
        # Step 1 — Planner
        plan_res = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": PLANNER_PROMPT},
                {"role": "user",   "content": req.prompt},
            ],
            temperature=0.7,
            max_tokens=800,
        )
        plan = plan_res.choices[0].message.content.strip()
        print(f"PLAN:\n{plan[:400]}\n")

        # Step 2 — Generator
        gen_res = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": GENERATOR_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"{plan}\n\n"
                        "REMINDERS:\n"
                        "- First line: function App() {\n"
                        "- Last line:  render();\n"
                        "- No imports, no export, no markdown fences.\n"
                        "- Hooks: React.useState  React.useEffect  React.useRef\n"
                        "- Filter inline (const visible = search ? items.filter(...) : items)\n"
                        "- Detail panel goes BELOW the grid, not inside cards.\n"
                        "- For maps: use inline SVG  with onMouseEnter/Leave/Click.\n"
                        "- For diagrams: use inline SVG / with event handlers."
                    ),
                },
            ],
            temperature=0.3,
            max_tokens=3500,
        )
        code = gen_res.choices[0].message.content.strip()
        print(f"CODE ({len(code)} chars)")

        return {"planner_instruction": plan, "generated_code": code}

    except Exception as e:
        print(f"ERROR: {e}")
        return {"error": str(e)}
