import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────
# NVIDIA CLIENT
# Get your key from https://build.nvidia.com
# Set env var:  NVIDIA_API_KEY=nvapi-xxxx
# ─────────────────────────────────────────────────────────────
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.environ.get("NVIDIA_API_KEY"),
)

# Best free models on NVIDIA build — change if you have credits for larger ones
PLANNER_MODEL   = "meta/llama-3.3-70b-instruct"
GENERATOR_MODEL = "deepseek-ai/deepseek-v4-pro"
#GENERATOR_MODEL = "qwen/qwen2.5-coder-7b-instruct"
#"meta/llama-3.3-70b-instruct"
REPAIR_MODEL    = "meta/llama-3.1-8b-instruct"

MAX_REPAIR_ATTEMPTS =0


class PromptRequest(BaseModel):
    prompt: str


# ─────────────────────────────────────────────────────────────
# NVIDIA STREAMING HELPER
# Collects all streamed chunks into one string
# ─────────────────────────────────────────────────────────────
def call_model(
    messages: list,
    model: str,
    temperature: float = 0.3,
    max_tokens: int = 1200, 
    #3500,
) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        top_p=0.7,
        max_tokens=max_tokens,
        stream=True,
    )
    result = ""
    for chunk in response:
        delta = chunk.choices[0].delta.content
        if delta:
            result += delta
    return result.strip()


# ─────────────────────────────────────────────────────────────
# STEP 1 — PRE-CLEAN
# Strip everything the LLM wraps around the JSX
# ─────────────────────────────────────────────────────────────
def pre_clean(code: str) -> str:
    # Strip markdown fences
    code = re.sub(r"^```[a-zA-Z]*\r?\n?", "", code, flags=re.MULTILINE)
    code = re.sub(r"^```\s*$", "", code, flags=re.MULTILINE)

    # Strip import lines
    code = re.sub(
        r"^import\s[\s\S]*?from\s+['\"][^'\"]+['\"];?\s*$",
        "", code, flags=re.MULTILINE
    )
    code = re.sub(
        r"^import\s+['\"][^'\"]+['\"];?\s*$",
        "", code, flags=re.MULTILINE
    )

    # Strip export keywords
    code = re.sub(r"\bexport\s+default\s+", "", code)
    code = re.sub(r"\bexport\s+", "", code)

    # Fix bare hooks → React.hook
    hooks = [
        "useState", "useEffect", "useRef", "useMemo",
        "useCallback", "useReducer", "useContext", "useLayoutEffect",
    ]
    for hook in hooks:
        code = re.sub(rf"(?<![.\w]){hook}(?=\s*\()", f"React.{hook}", code)

    # Fix class= → className=
    code = re.sub(r"(\s)class=", r"\1className=", code)
    code = re.sub(r"^class=", "className=", code, flags=re.MULTILINE)

    # Remove ALL render() / ReactDOM.render() variants
    code = re.sub(r"ReactDOM\.render\s*\([\s\S]*?\)\s*;?", "", code)
    code = re.sub(r"\nrender\s*\(\s*\)\s*;?", "", code)
    code = re.sub(r"\nrender\s*\(<\s*App\s*/?\s*>[^)]*\)\s*;?", "", code)

    # Drop leading prose lines before first JS/JSX line
    lines = code.split("\n")
    first_code = next(
        (i for i, l in enumerate(lines)
         if re.match(r"^\s*(\/\/|\/\*|function |const |let |var |render\s*\()", l)),
        0
    )
    code = "\n".join(lines[first_code:])

    # Add exactly ONE clean render call at end
    code = code.rstrip() + "\n\nrender(<App />);"
    return code.strip()


# ─────────────────────────────────────────────────────────────
# STEP 2 — VALIDATE
# Returns list of human-readable error strings.
# Empty list = safe to send to the frontend.
# ─────────────────────────────────────────────────────────────
def validate_code(code: str) -> list:
    errors = []

    # ── Basic structure ─────────────────────────────────────

    if not re.search(r"function\s+App\s*\(", code):
        errors.append(
            "MISSING: Component must be named App. "
            "Start output with: function App() {"
        )

    if not re.search(r"render\s*\(\s*<\s*App\s*/?\s*>\s*\)\s*;?\s*$", code.strip()):
        errors.append(
            "TRUNCATED OR MISSING: Last line must be exactly: render(<App />); "
            "Your output was cut off. Regenerate the COMPLETE component "
            "and end with render(<App />);"
        )

    # ── Forbidden patterns ───────────────────────────────────

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
            "FORBIDDEN: .forEach() returns undefined in JSX. "
            "Replace with .map()"
        )

    if re.search(r"ReactDOM\s*\.", code):
        errors.append(
            "FORBIDDEN: ReactDOM is not available. "
            "Do NOT use ReactDOM.render(). Last line must be: render(<App />);"
        )

    if re.search(r"=\s*\{/\*", code):
        errors.append(
            "FORBIDDEN: {/* comment */} used as a prop value. "
            "Replace every {/* ... */} prop with a real string value."
        )

    # ── Syntax: balanced delimiters ─────────────────────────

    if code.count("`") % 2 != 0:
        errors.append(
            "SYNTAX: Odd number of backticks — unclosed template literal. "
            "Find and close it."
        )

    if "```" in code:
        errors.append("FORBIDDEN: ``` markdown fences in output. Remove them.")

    open_b  = code.count("{")
    close_b = code.count("}")
    if open_b != close_b:
        errors.append(
            f"SYNTAX: Unbalanced curly braces — "
            f"{open_b} opening '{{' vs {close_b} closing '}}'. "
            "Your output was truncated. Regenerate the COMPLETE component — "
            "every opened {{ must have a matching }}."
        )

    open_p  = code.count("(")
    close_p = code.count(")")
    if open_p != close_p:
        errors.append(
            f"SYNTAX: Unbalanced parentheses — "
            f"{open_p} '(' vs {close_p} ')'. "
            "Your output was truncated. Close every opened expression."
        )

    # ── JSX tag balance ──────────────────────────────────────
    # Only check structural container tags (not self-closing SVG/HTML elements)
    structural_tags = [
        "div", "span", "p", "h1", "h2", "h3", "h4", "h5", "h6",
        "ul", "ol", "li", "table", "tr", "td", "th", "thead", "tbody",
        "svg", "g", "section", "article", "main", "header", "footer",
        "nav", "aside", "form", "label", "select", "textarea",
        "button", "a", "strong", "em", "small",
    ]
    tag_errors = []
    for tag in structural_tags:
        opens  = len(re.findall(rf"<{tag}(?:\s[^>]*)?>", code))
        closes = len(re.findall(rf"</{tag}>", code))
        self_c = len(re.findall(rf"<{tag}\s*/>", code))
        opens -= self_c   # self-closing don't need a closing tag
        if opens != closes:
            tag_errors.append(f"<{tag}> opened {opens}x but closed {closes}x")
    if tag_errors:
        errors.append(
            "UNCLOSED JSX TAGS — fix ALL of these: " +
            "; ".join(tag_errors[:6]) +
            ". Every opened tag MUST have a matching closing tag. "
            "Output was likely truncated — regenerate the COMPLETE component."
        )

    # ── Placeholder detection ────────────────────────────────
    placeholder_patterns = [
        (r"x-coordinate",       "x-coordinate"),
        (r"y-coordinate",       "y-coordinate"),
        (r"path\s+data",        "path data"),
        (r"insert\s+here",      "insert here"),
        (r"\bTODO\b",           "TODO"),
        (r"\bFIXME\b",          "FIXME"),
        (r"your\s+text\s+here", "your text here"),
    ]
    for pattern, label in placeholder_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            errors.append(
                f"FORBIDDEN: Placeholder text '{label}' found in output. "
                "Replace every placeholder with a real value."
            )

    return errors


# ─────────────────────────────────────────────────────────────
# REPAIR SYSTEM PROMPT
# ─────────────────────────────────────────────────────────────
REPAIR_SYSTEM = """You are a JSX syntax repair specialist.

You receive a broken React component and a list of exact errors.
Output the FULLY FIXED and COMPLETE component — nothing omitted or truncated.

STRICT RULES:
- Raw JSX only. Zero markdown. Zero ``` fences.
- No import or require statements of any kind.
- No export keyword anywhere.
- ALL hooks: React.useState  React.useEffect  React.useRef  React.useMemo
- className= not class=
- No .forEach() in JSX — use .map()
- No ReactDOM — last line must be exactly: render(<App />);
- No {/* comment */} as prop values — replace with real values
- Component name: App
- First line: function App() {
- Last line:  render(<App />);

CRITICAL — every opened tag/brace/paren MUST be closed:
- Every { must have a matching }
- Every ( must have a matching )
- Every <div> must have a </div>
- Every <span> must have a </span>
- The component MUST be COMPLETE — do not stop early.

Fix ONLY what the error list says. Keep all data and logic identical.
Output the complete fixed code and NOTHING else."""


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

SVG MAP rules (topic involves a geographic map):
  Specify viewBox dimensions.
  For each region provide: id, name, approximate SVG path d="M...Z",
  label position lx/ly, fill colour, capital, population, area, fun fact.
  Include ALL regions (all 28 states + 8 UTs for India).
  Paths must be COMPLETE closed shapes ending with Z.

SVG DIAGRAM rules (anatomy, body systems, mechanisms):
  Each part = one SVG shape (ellipse, rect, circle) with real coordinates.
  Include cx/cy/rx/ry for ellipse, x/y/w/h for rect.
  Label every part. Include clickable numbered step list.

CARD GRID rules (default):
  List every data item with at least 5 real fields.
  Mandatory search/filter bar when more than 8 items.
  Hover highlight + click opens detail panel BELOW the grid.

Output ONLY the instruction. No preamble."""


# ─────────────────────────────────────────────────────────────
# GENERATOR PROMPT
# ─────────────────────────────────────────────────────────────
GENERATOR_PROMPT = """You are a React + SVG engineer. Output ONE complete raw JSX component.

╔══════════════════════════════════════════════════════════╗
║  ABSOLUTE RULES — break any = fatal render crash         ║
╚══════════════════════════════════════════════════════════╝

1.  Output RAW JSX/JS ONLY.
    Zero English sentences. Zero markdown. Zero ``` fences.

2.  NO import or require statements. Not even: import React from 'react'

3.  NO export keyword anywhere.

4.  ALL React hooks MUST have the React. prefix:
      React.useState  React.useEffect  React.useRef  React.useMemo
    NEVER write bare:  useState(  useEffect(

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

13. FILTER PATTERN:
      const [search, setSearch] = React.useState('');
      const visible = search
        ? items.filter(i => i.name.toLowerCase().includes(search.toLowerCase()))
        : items;
      Render: visible.map(...)

14. NEVER use JSX comments as prop values.
    WRONG:  <path d={/* path data */} />
    RIGHT:  <path d="M100,200 L300,400 Z" />

15. NEVER write placeholder text. Every field must be a real value.

16. COMPLETE OUTPUT REQUIREMENT — this is critical:
    Your output MUST be 100% complete.
    Every { must have a matching }.
    Every ( must have a matching ).
    Every <div> must have a </div>.
    Every <span> must have a </span>.
    Every SVG <path d="..."> must end with Z inside the quotes.
    Do NOT stop generating mid-way. Write until render(<App />); is output.
    If the component is long, keep going — do not truncate.

╔══════════════════════════════════════════════════════════╗
║  DESIGN                                                  ║
╚══════════════════════════════════════════════════════════╝
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
    Outer div: style={{opacity:mounted?1:0,transform:mounted?'none':'translateY(16px)',transition:'all 0.4s ease'}}

╔══════════════════════════════════════════════════════════╗
║  SVG MAP PATTERN                                         ║
╚══════════════════════════════════════════════════════════╝
  const regions = [
    { id:'ap', name:'Andhra Pradesh', lx:420, ly:580,
      fill:'#a5b4fc',
      path:'M390,520 L450,510 L470,560 L440,610 L400,600 Z',
      capital:'Amaravati', population:'49M', area:'162975 km2',
      fact:'Known for spicy cuisine and classical dance' },
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

╔══════════════════════════════════════════════════════════╗
║  SVG DIAGRAM PATTERN                                     ║
╚══════════════════════════════════════════════════════════╝
  const parts = [
    { id:'stomach', name:'Stomach', shape:'ellipse',
      cx:250, cy:280, rx:70, ry:50,
      fill:'#fda4af', desc:'Breaks down food using acid.' },
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

╔══════════════════════════════════════════════════════════╗
║  START:  function App() {                                ║
║  END:    render(<App />);   ← REQUIRED FINAL LINE        ║
╚══════════════════════════════════════════════════════════╝"""


# ─────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok", "message": "Backend running — NVIDIA API"}


@app.post("/generate-ui")
async def generate_ui(req: PromptRequest):
    start_total = time.time()

    print(f"\n{'='*60}")
    print(f"PROMPT: {req.prompt}")
    print(f"{'='*60}")

    try:
        # STEP 1
        t1 = time.time()

        print("Starting planner...")

        plan = call_model(
            messages=[
                {"role": "system", "content": PLANNER_PROMPT},
                {"role": "user", "content": req.prompt},
            ],
            model=PLANNER_MODEL,
            temperature=0.7,
            max_tokens=800,
        )

        print(f"Planner completed in {time.time() - t1:.2f}s")

        # STEP 2
        t2 = time.time()

        print("Starting generator...")

        code = call_model(
            messages=[
                {"role": "system", "content": GENERATOR_PROMPT},
                {"role": "user", "content": plan},
            ],
            model=GENERATOR_MODEL,
            temperature=0.3,
            max_tokens=1200,
        )

        print(f"Generator completed in {time.time() - t2:.2f}s")

        # STEP 3
        t3 = time.time()

        code = pre_clean(code)
        errors = validate_code(code)

        print(f"Validation completed in {time.time() - t3:.2f}s")
        print(f"Errors found: {len(errors)}")

        print(f"TOTAL TIME: {time.time() - start_total:.2f}s")

        return {
            "planner_instruction": plan,
            "generated_code": code,
            "errors": errors
        }

    except Exception as e:
        print(f"ERROR: {e}")
        return {"error": str(e)}
