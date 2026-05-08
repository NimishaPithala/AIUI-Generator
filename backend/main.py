import re
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
MAX_REPAIR_ATTEMPTS = 3


class PromptRequest(BaseModel):
    prompt: str


# ─────────────────────────────────────────────────────────────
# PRE-CLEAN
# ─────────────────────────────────────────────────────────────
def pre_clean(code: str) -> str:
    # 1. Strip markdown fences
    code = re.sub(r"^```[a-zA-Z]*\r?\n?", "", code, flags=re.MULTILINE)
    code = re.sub(r"^```\s*$", "", code, flags=re.MULTILINE)

    # 2. Strip import lines
    code = re.sub(
        r"^import\s[\s\S]*?from\s+['\"][^'\"]+['\"];?\s*$",
        "", code, flags=re.MULTILINE
    )
    code = re.sub(
        r"^import\s+['\"][^'\"]+['\"];?\s*$",
        "", code, flags=re.MULTILINE
    )

    # 3. Strip export
    code = re.sub(r"\bexport\s+default\s+", "", code)
    code = re.sub(r"\bexport\s+", "", code)

    # 4. Fix bare hooks -> React.hook
    hooks = [
        "useState", "useEffect", "useRef", "useMemo",
        "useCallback", "useReducer", "useContext", "useLayoutEffect",
    ]
    for hook in hooks:
        code = re.sub(rf"(?<![.\w]){hook}(?=\s*\()", f"React.{hook}", code)

    # 5. Fix class= -> className=
    code = re.sub(r"(\s)class=", r"\1className=", code)
    code = re.sub(r"^class=", "className=", code, flags=re.MULTILINE)

    # 6. Remove ALL render() / ReactDOM.render() calls
    #    LLM often outputs multiple render calls in different forms
    code = re.sub(r"ReactDOM\.render\s*\([\s\S]*?\)\s*;?", "", code)
    code = re.sub(r"\nrender\s*\(\s*\)\s*;?", "", code)
    code = re.sub(r"\nrender\s*\(<\s*App\s*/?\s*>[^)]*\)\s*;?", "", code)

    # 7. Drop leading prose lines before first JS/JSX line
    lines = code.split("\n")
    first_code = next(
        (i for i, l in enumerate(lines)
         if re.match(r"^\s*(\/\/|\/\*|function |const |let |var |render\s*\()", l)),
        0
    )
    code = "\n".join(lines[first_code:])

    # 8. Add exactly ONE clean render call at end
    code = code.rstrip() + "\n\nrender(<App />);"
    return code.strip()


# ─────────────────────────────────────────────────────────────
# VALIDATE
# ─────────────────────────────────────────────────────────────
def validate_code(code: str):
    errors = []

    if not re.search(r"function\s+App\s*\(", code):
        errors.append(
            "MISSING: Component must be named App. "
            "Start output with: function App() {"
        )

    if not re.search(r"render\s*\(\s*<\s*App\s*/?\s*>\s*\)\s*;?\s*$", code.strip()):
        errors.append(
            "MISSING: Last line must be exactly: render(<App />);"
        )

    if re.search(r"^import\s", code, re.MULTILINE):
        errors.append(
            "FORBIDDEN: Remove ALL import statements. "
            "Do not import React, hooks, or anything."
        )

    if re.search(r"\bexport\b", code):
        errors.append("FORBIDDEN: Remove all export keywords.")

    bare_hooks = [
        "useState", "useEffect", "useRef", "useMemo",
        "useCallback", "useReducer", "useContext",
    ]
    for hook in bare_hooks:
        if re.search(rf"(?<![.\w]){hook}\s*\(", code):
            errors.append(
                f"FORBIDDEN: bare '{hook}(' found. "
                f"Must be 'React.{hook}(' — never the bare form."
            )

    if re.search(r"(\s)class=", code):
        errors.append("FORBIDDEN: 'class=' found — use 'className=' in JSX.")

    if re.search(r"\.forEach\s*\(", code):
        errors.append(
            "FORBIDDEN: '.forEach()' inside JSX returns undefined. "
            "Replace with '.map()'."
        )

    if code.count("`") % 2 != 0:
        errors.append(
            "SYNTAX: Odd number of backticks — unclosed template literal. Fix it."
        )

    if "```" in code:
        errors.append("FORBIDDEN: ``` markdown fences in output. Remove them.")

    if re.search(r"ReactDOM\s*\.", code):
        errors.append(
            "FORBIDDEN: ReactDOM is not available. "
            "Do NOT use ReactDOM.render(). Last line must be: render(<App />);"
        )

    if re.search(r"\{/\*[\s\S]*?\*/\}", code):
        errors.append(
            "FORBIDDEN: JSX comment {/* ... */} used as a prop value. "
            "Replace every {/* ... */} prop with a real string value."
        )

    return errors


# ─────────────────────────────────────────────────────────────
# REPAIR PROMPT
# ─────────────────────────────────────────────────────────────
REPAIR_SYSTEM = """You are a JSX syntax repair specialist.

You receive broken React component code and a list of exact errors.
Output the FULLY FIXED and COMPLETE code — nothing omitted.

STRICT RULES:
- Raw JSX only. Zero markdown. Zero ``` fences.
- No import or require statements of any kind.
- No export keyword anywhere.
- ALL hooks MUST use React prefix: React.useState  React.useEffect  React.useRef
- Use className= not class=
- No .forEach() inside JSX — use .map()
- No ReactDOM — last line must be exactly: render(<App />);
- No JSX comments {/* */} as prop values — replace with real values or empty string ""
- Component name: App
- First line: function App() {
- Last line:  render(<App />);

Fix ONLY what the error list says. Keep all data and logic identical.
Output the complete fixed code and nothing else."""


# ─────────────────────────────────────────────────────────────
# PLANNER PROMPT
# ─────────────────────────────────────────────────────────────
PLANNER_PROMPT = """You are an expert educational UI/UX planner.

Analyse the user request and write a precise instruction for a React/SVG engineer
to build one self-contained interactive educational UI component.

COMPONENT TYPE — pick the best fit:
  CARD GRID   : facts, lists, comparisons (planets, elements, countries, states)
  SVG MAP     : any geographic map (India, world, US states, continents)
  SVG DIAGRAM : body systems, anatomy, atom, circuits, mechanisms
  TIMELINE    : historical events, ordered processes
  CALCULATOR  : math/science with live inputs and computed outputs
  QUIZ        : questions, answer choices, score tracking

SVG MAP rules (use when topic involves a geographic map):
  Specify viewBox dimensions.
  For each region provide: id, name, approximate SVG path d="M...Z",
  label position lx/ly, fill colour, capital, population, area, fun fact.
  Include ALL regions (all 28 states + 8 UTs for India).

SVG DIAGRAM rules (anatomy, body systems, mechanisms):
  Each part = one SVG shape (ellipse, rect, circle) with real coordinates.
  Include cx/cy/rx/ry for ellipse, x/y/w/h for rect.
  Label every part. Include clickable numbered step list to highlight parts.

CARD GRID rules (default):
  List every data item with at least 5 real fields.
  Mandatory search/filter bar when more than 8 items.
  Hover highlight + click opens detail panel BELOW the grid.

Output ONLY the instruction. No preamble."""


# ─────────────────────────────────────────────────────────────
# GENERATOR PROMPT
# ─────────────────────────────────────────────────────────────
GENERATOR_PROMPT = """You are a React + SVG engineer. Output ONE raw JSX component.

ABSOLUTE RULES — break any = fatal render crash:

1.  Output RAW JSX/JS ONLY.
    Zero English sentences. Zero markdown. Zero ``` fences.

2.  NO import or require statements. Not even: import React from 'react'

3.  NO export keyword anywhere.

4.  ALL React hooks MUST have the React. prefix:
      React.useState    React.useEffect    React.useRef    React.useMemo
    NEVER write bare:   useState(          useEffect(

5.  Write className= never class=

6.  No external libraries. Pure React + inline SVG only.

7.  Component name must be exactly: App

8.  First line of output: function App() {

9.  Last line of output:  render(<App />);
    Do NOT write ReactDOM.render(). Do NOT write bare render().
    Do NOT write render(<App />) more than ONCE.

10. NEVER use .forEach() inside JSX — use .map() only.

11. Detail panel is a SEPARATE <div> BELOW the grid, shown conditionally.
    NEVER nest it inside a card.

12. Define ALL data arrays as const INSIDE App() BEFORE the return().

13. FILTER PATTERN — never initialise a filtered state as []:
      const [search, setSearch] = React.useState('');
      const visible = search
        ? items.filter(i => i.name.toLowerCase().includes(search.toLowerCase()))
        : items;
      Render: visible.map(...)

14. NEVER use JSX comments as prop values.
    WRONG:  <path d={/* path data */} />
    RIGHT:  <path d="M100,200 L300,400 Z" />
    Every prop must have a REAL value — no placeholders, no comments.

15. NEVER write placeholder comments inside data arrays.
    Every field must be a real string or number.

DESIGN:
  Page:     className="min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50 p-6 font-sans"
  Cards:    className="bg-white rounded-2xl shadow-md border border-gray-100 p-4 cursor-pointer transition-all duration-200"
  Selected: style={{background:'#4338ca',color:'#fff'}}
  Hovered:  style={{background:'#eef2ff'}}
  Search:   className="w-full border border-gray-200 rounded-xl px-4 py-2 mb-4 text-gray-800 outline-none focus:ring-2 focus:ring-indigo-300"
  Detail:   className="bg-white rounded-2xl shadow-xl border border-indigo-100 p-6 mt-6"

  Entrance animation:
    const [mounted, setMounted] = React.useState(false);
    React.useEffect(() => {
      const t = setTimeout(() => setMounted(true), 50);
      return () => clearTimeout(t);
    }, []);
    Outer div style: {{opacity:mounted?1:0, transform:mounted?'none':'translateY(16px)', transition:'all 0.4s ease'}}

SVG MAP PATTERN:
  const regions = [
    { id:'ap', name:'Andhra Pradesh', lx:420, ly:580,
      fill:'#a5b4fc',
      path:'M390,520 L450,510 L470,560 L440,610 L400,600 Z',
      capital:'Amaravati', population:'49M', area:'162975 km2',
      fact:'Known for spicy cuisine and classical dance Kuchipudi' },
  ];
  const [hovReg, setHovReg] = React.useState(null);
  const [selReg, setSelReg] = React.useState(null);

  <svg viewBox="0 0 700 800" style={{width:'100%',height:'auto',display:'block'}}>
    {regions.map(r => (
      <path key={r.id} d={r.path}
        fill={selReg===r.id?'#4338ca':hovReg===r.id?'#818cf8':r.fill}
        stroke="#fff" strokeWidth="1.5"
        style={{cursor:'pointer',transition:'fill 0.2s'}}
        onMouseEnter={()=>setHovReg(r.id)}
        onMouseLeave={()=>setHovReg(null)}
        onClick={()=>setSelReg(selReg===r.id?null:r.id)}
      />
    ))}
    {regions.map(r => (
      <text key={r.id+'_lbl'} x={r.lx} y={r.ly}
        textAnchor="middle" fontSize="8" fill="#1e1b4b"
        style={{pointerEvents:'none',fontWeight:600}}>
        {r.name}
      </text>
    ))}
  </svg>

SVG DIAGRAM PATTERN:
  const parts = [
    { id:'stomach', name:'Stomach', shape:'ellipse',
      cx:250, cy:280, rx:70, ry:50,
      fill:'#fda4af', desc:'Breaks down food using acid and enzymes.' },
    { id:'liver', name:'Liver', shape:'rect',
      x:310, y:200, w:80, h:60,
      fill:'#fb923c', desc:'Produces bile and detoxifies blood.' },
  ];
  const [hovPart, setHovPart] = React.useState(null);
  const [selPart, setSelPart] = React.useState(null);

  <svg viewBox="0 0 500 600" style={{width:'100%',maxWidth:'420px',height:'auto'}}>
    {parts.map(p => p.shape==='ellipse' ? (
      <ellipse key={p.id} cx={p.cx} cy={p.cy} rx={p.rx} ry={p.ry}
        fill={selPart===p.id?'#6366f1':hovPart===p.id?'#a5b4fc':p.fill}
        stroke="#fff" strokeWidth="2"
        style={{cursor:'pointer',transition:'fill 0.2s'}}
        onMouseEnter={()=>setHovPart(p.id)}
        onMouseLeave={()=>setHovPart(null)}
        onClick={()=>setSelPart(selPart===p.id?null:p.id)}
      />
    ) : (
      <rect key={p.id} x={p.x} y={p.y} width={p.w} height={p.h} rx="8"
        fill={selPart===p.id?'#6366f1':hovPart===p.id?'#a5b4fc':p.fill}
        stroke="#fff" strokeWidth="2"
        style={{cursor:'pointer',transition:'fill 0.2s'}}
        onMouseEnter={()=>setHovPart(p.id)}
        onMouseLeave={()=>setHovPart(null)}
        onClick={()=>setSelPart(selPart===p.id?null:p.id)}
      />
    ))}
    {parts.map(p => (
      <text key={p.id+'_lbl'}
        x={p.cx !== undefined ? p.cx : p.x + p.w/2}
        y={(p.cy !== undefined ? p.cy : p.y + p.h/2) + 4}
        textAnchor="middle" fontSize="10" fill="#fff"
        style={{pointerEvents:'none',fontWeight:700}}>
        {p.name}
      </text>
    ))}
  </svg>

START output with: function App() {
END   output with: render(<App />);"""


# ─────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok", "message": "Backend running"}


@app.post("/generate-ui")
async def generate_ui(req: PromptRequest):
    print(f"\n{'='*60}\nPROMPT: {req.prompt}\n{'='*60}")

    try:
        # Step 1: Planner
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
        print(f"PLAN ({len(plan)} chars):\n{plan[:300]}\n")

        # Step 2: Generator
        gen_res = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": GENERATOR_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"{plan}\n\n"
                        "CRITICAL REMINDERS:\n"
                        "- First line: function App() {\n"
                        "- Last line:  render(<App />);\n"
                        "- No imports, no export, no markdown fences.\n"
                        "- Hooks: React.useState  React.useEffect  React.useRef\n"
                        "- No ReactDOM — write render(<App />) once at the end only.\n"
                        "- No {/* comment */} as prop values — use real string values.\n"
                        "- Filter inline: const visible = search ? items.filter(...) : items\n"
                        "- Detail panel is a separate div BELOW the grid."
                    ),
                },
            ],
            temperature=0.3,
            max_tokens=3500,
        )
        code = gen_res.choices[0].message.content.strip()
        print(f"GEN attempt 1: {len(code)} chars")

        # Step 3: Validate + Repair loop
        for attempt in range(MAX_REPAIR_ATTEMPTS):
            code = pre_clean(code)
            errors = validate_code(code)

            if not errors:
                print(f"PASSED validation on attempt {attempt + 1}")
                break

            print(f"Attempt {attempt + 1} — {len(errors)} error(s):")
            for e in errors:
                print(f"  * {e}")

            if attempt == MAX_REPAIR_ATTEMPTS - 1:
                print("Max repair attempts reached — sending best-effort code")
                break

            error_list = "\n".join(f"- {e}" for e in errors)
            repair_res = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": REPAIR_SYSTEM},
                    {
                        "role": "user",
                        "content": (
                            f"Fix these errors in the React component below.\n\n"
                            f"ERRORS:\n{error_list}\n\n"
                            f"BROKEN CODE:\n{code}\n\n"
                            f"Output the complete fixed code only.\n"
                            f"First line: function App() {{\n"
                            f"Last line:  render(<App />);"
                        ),
                    },
                ],
                temperature=0.1,
                max_tokens=3500,
            )
            code = repair_res.choices[0].message.content.strip()
            print(f"Repair {attempt + 1}: {len(code)} chars")

        # Final clean pass
        code = pre_clean(code)
        print(f"FINAL: {len(code)} chars\n{code[:200]}")

        return {"planner_instruction": plan, "generated_code": code}

    except Exception as e:
        print(f"ERROR: {e}")
        return {"error": str(e)}
