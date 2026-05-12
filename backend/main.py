import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────
# NVIDIA CLIENT  —  DeepSeek via NVIDIA API
# Set env var:  NVIDIA_API_KEY=nvapi-xxxx
# Model options (all available on build.nvidia.com free tier):
#   deepseek-ai/deepseek-r1          (reasoning, best quality)
#   deepseek-ai/deepseek-coder-6.7b-instruct  (fast, code-focused)
#   meta/llama-3.3-70b-instruct      (fallback)
# ─────────────────────────────────────────────────────────────
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.environ.get("NVIDIA_API_KEY"),
)

GENERATOR_MODEL = "deepseek-ai/deepseek-r1"
REPAIR_MODEL    = "deepseek-ai/deepseek-r1"

MAX_REPAIR_ATTEMPTS = 3


class PromptRequest(BaseModel):
    prompt: str


# ─────────────────────────────────────────────────────────────
# NVIDIA STREAMING HELPER
# ─────────────────────────────────────────────────────────────
def call_model(
    messages: list,
    model: str,
    temperature: float = 0.3,
    max_tokens: int = 4000,
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
# OUTPUT TYPE DETECTION
# Figures out whether the LLM returned HTML or JSX
# ─────────────────────────────────────────────────────────────
def detect_type(code: str) -> str:
    """Returns 'html' or 'jsx'"""
    c = code.strip().lower()
    if c.startswith("<!doctype") or c.startswith("<html"):
        return "html"
    if "<html" in c and "</html>" in c:
        return "html"
    if "function app()" in c or "function app (" in c:
        return "jsx"
    if "render(<app" in c:
        return "jsx"
    # Has full HTML structure but no doctype
    if "<body" in c and "</body>" in c:
        return "html"
    return "jsx"  # safe default


# ─────────────────────────────────────────────────────────────
# HTML PIPELINE
# ─────────────────────────────────────────────────────────────
def pre_clean_html(code: str) -> str:
    """Strip markdown fences from HTML output."""
    code = re.sub(r"^```[a-zA-Z]*\r?\n?", "", code, flags=re.MULTILINE)
    code = re.sub(r"^```\s*$", "", code, flags=re.MULTILINE)
    # Drop any leading prose before <!DOCTYPE or <html
    match = re.search(r"(<!DOCTYPE|<html)", code, re.IGNORECASE)
    if match:
        code = code[match.start():]
    return code.strip()


def validate_html(code: str) -> list:
    errors = []
    lower = code.lower()
    if "</html>" not in lower and "</body>" not in lower:
        errors.append(
            "HTML INCOMPLETE: Missing closing </body> or </html>. "
            "Output was truncated. Regenerate the COMPLETE HTML document."
        )
    if "<script" in lower and "</script>" not in lower:
        errors.append(
            "HTML INCOMPLETE: Unclosed <script> tag. "
            "Close every <script> block with </script>."
        )
    if "<style" in lower and "</style>" not in lower:
        errors.append(
            "HTML INCOMPLETE: Unclosed <style> tag. "
            "Close every <style> block with </style>."
        )
    return errors


# ─────────────────────────────────────────────────────────────
# JSX PIPELINE
# ─────────────────────────────────────────────────────────────
def pre_clean_jsx(code: str) -> str:
    """Strip everything the LLM wraps around the JSX."""
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

    # Drop leading prose before first JS line
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


def validate_jsx(code: str) -> list:
    errors = []

    if not re.search(r"function\s+App\s*\(", code):
        errors.append(
            "MISSING: Component must be named App. "
            "Start output with: function App() {"
        )

    if not re.search(r"render\s*\(\s*<\s*App\s*/?\s*>\s*\)\s*;?\s*$", code.strip()):
        errors.append(
            "TRUNCATED OR MISSING: Last line must be: render(<App />); "
            "Output was cut off. Regenerate the COMPLETE component."
        )

    if re.search(r"^import\s", code, re.MULTILINE):
        errors.append("FORBIDDEN: Remove ALL import statements.")

    if re.search(r"\bexport\b", code):
        errors.append("FORBIDDEN: Remove all export keywords.")

    bare_hooks = ["useState", "useEffect", "useRef", "useMemo",
                  "useCallback", "useReducer", "useContext"]
    for hook in bare_hooks:
        if re.search(rf"(?<![.\w]){hook}\s*\(", code):
            errors.append(
                f"FORBIDDEN: bare '{hook}(' — must be 'React.{hook}('"
            )

    if re.search(r"(\s)class=", code):
        errors.append("FORBIDDEN: 'class=' found — use 'className='")

    if re.search(r"\.forEach\s*\(", code):
        errors.append("FORBIDDEN: .forEach() in JSX — use .map()")

    if re.search(r"ReactDOM\s*\.", code):
        errors.append("FORBIDDEN: ReactDOM not available. Use render(<App />) only.")

    if re.search(r"=\s*\{/\*", code):
        errors.append("FORBIDDEN: {/* comment */} as prop value. Use a real value.")

    if code.count("`") % 2 != 0:
        errors.append("SYNTAX: Odd backtick count — unclosed template literal.")

    if "```" in code:
        errors.append("FORBIDDEN: ``` fences found. Remove them.")

    open_b, close_b = code.count("{"), code.count("}")
    if open_b != close_b:
        errors.append(
            f"SYNTAX: Unbalanced braces — {open_b} '{{' vs {close_b} '}}'. "
            "Output truncated. Regenerate COMPLETE component."
        )

    open_p, close_p = code.count("("), code.count(")")
    if open_p != close_p:
        errors.append(
            f"SYNTAX: Unbalanced parens — {open_p} '(' vs {close_p} ')'. "
            "Output truncated. Close every expression."
        )

    # JSX tag balance
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
        opens -= self_c
        if opens != closes:
            tag_errors.append(f"<{tag}> opened {opens}x closed {closes}x")
    if tag_errors:
        errors.append(
            "UNCLOSED TAGS: " + "; ".join(tag_errors[:5]) +
            ". Regenerate the COMPLETE component with all tags closed."
        )

    # Placeholder detection
    for pattern, label in [
        (r"x-coordinate", "x-coordinate"), (r"y-coordinate", "y-coordinate"),
        (r"path\s+data", "path data"),     (r"\bTODO\b", "TODO"),
        (r"\bFIXME\b", "FIXME"),
    ]:
        if re.search(pattern, code, re.IGNORECASE):
            errors.append(
                f"FORBIDDEN: Placeholder '{label}' found. Replace with real value."
            )

    return errors


# ─────────────────────────────────────────────────────────────
# GENERATOR PROMPT
# Single prompt — LLM chooses JSX or HTML, produces complete component
# ─────────────────────────────────────────────────────────────
GENERATOR_PROMPT = """You are an expert UI engineer. The user wants an interactive educational UI component.

Choose the best output format:
  - JSX  : for interactive components with state (maps, diagrams, calculators, quizzes, card grids)
  - HTML : for simpler visualisations or when SVG/CSS animations are sufficient

══════════════════════════════════════
IF YOU CHOOSE JSX — follow these rules
══════════════════════════════════════

OUTPUT RULES (JSX):
1.  Raw JSX/JS ONLY. Zero markdown, zero ``` fences, zero English prose.
2.  NO import or require statements of any kind.
3.  NO export keyword.
4.  ALL hooks MUST use React prefix: React.useState  React.useEffect  React.useRef  React.useMemo
5.  Use className= not class=
6.  No external libraries — pure React + inline SVG only.
7.  Component name: App
8.  First line: function App() {
9.  Last line:  render(<App />);  — exactly once, no ReactDOM.render()
10. No .forEach() in JSX — use .map()
11. Detail panel is a SEPARATE div BELOW the list/grid — never inside a card
12. ALL data arrays defined as const INSIDE App() BEFORE return()
13. Filter inline: const visible = search ? items.filter(...) : items
14. No JSX comments as prop values: NEVER <path d={/* data */} /> — use real values
15. OUTPUT MUST BE 100% COMPLETE:
    - Every { has a matching }
    - Every ( has a matching )
    - Every <div> has </div>
    - Every SVG path d="..." ends with Z
    - Write until render(<App />); — do NOT stop early

DESIGN (JSX):
  Page:    className="min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50 p-6 font-sans"
  Cards:   className="bg-white rounded-2xl shadow-md border border-gray-100 p-4 cursor-pointer transition-all duration-200"
  Selected: style={{background:'#4338ca',color:'#fff'}}
  Hovered:  style={{background:'#eef2ff'}}
  Search:  className="w-full border border-gray-200 rounded-xl px-4 py-2 mb-4 text-gray-800 outline-none focus:ring-2 focus:ring-indigo-300"
  Detail:  className="bg-white rounded-2xl shadow-xl border border-indigo-100 p-6 mt-6"
  Entrance animation:
    const [mounted, setMounted] = React.useState(false);
    React.useEffect(() => { const t = setTimeout(()=>setMounted(true),50); return ()=>clearTimeout(t); }, []);
    style={{opacity:mounted?1:0,transform:mounted?'none':'translateY(16px)',transition:'all 0.4s ease'}}

SVG MAP pattern (use for any geographic map):
  const regions = [
    { id:'ap', name:'Andhra Pradesh', lx:420, ly:580, fill:'#a5b4fc',
      path:'M390,520 L450,510 L470,560 L440,610 L400,600 Z',
      capital:'Amaravati', population:'49M', area:'162975 km2', fact:'...' },
  ];
  const [hovReg, setHovReg] = React.useState(null);
  const [selReg, setSelReg] = React.useState(null);
  <svg viewBox="0 0 700 800" style={{width:'100%',height:'auto',display:'block'}}>
    {regions.map(r => (
      <path key={r.id} d={r.path}
        fill={selReg===r.id?'#4338ca':hovReg===r.id?'#818cf8':r.fill}
        stroke="#fff" strokeWidth="1.5" style={{cursor:'pointer',transition:'fill 0.2s'}}
        onMouseEnter={()=>setHovReg(r.id)} onMouseLeave={()=>setHovReg(null)}
        onClick={()=>setSelReg(selReg===r.id?null:r.id)} />
    ))}
    {regions.map(r => (
      <text key={r.id+'_l'} x={r.lx} y={r.ly} textAnchor="middle" fontSize="8"
        fill="#1e1b4b" style={{pointerEvents:'none',fontWeight:600}}>{r.name}</text>
    ))}
  </svg>

SVG DIAGRAM pattern (use for anatomy, body systems, mechanisms):
  const parts = [
    { id:'stomach', name:'Stomach', shape:'ellipse', cx:250, cy:280, rx:70, ry:50,
      fill:'#fda4af', desc:'Breaks down food using acid and enzymes.' },
    { id:'liver', name:'Liver', shape:'rect', x:310, y:200, w:80, h:60,
      fill:'#fb923c', desc:'Produces bile and detoxifies blood.' },
  ];
  const [hovPart, setHovPart] = React.useState(null);
  const [selPart, setSelPart] = React.useState(null);
  <svg viewBox="0 0 500 600" style={{width:'100%',maxWidth:'420px',height:'auto'}}>
    {parts.map(p => p.shape==='ellipse' ? (
      <ellipse key={p.id} cx={p.cx} cy={p.cy} rx={p.rx} ry={p.ry}
        fill={selPart===p.id?'#6366f1':hovPart===p.id?'#a5b4fc':p.fill}
        stroke="#fff" strokeWidth="2" style={{cursor:'pointer',transition:'fill 0.2s'}}
        onMouseEnter={()=>setHovPart(p.id)} onMouseLeave={()=>setHovPart(null)}
        onClick={()=>setSelPart(selPart===p.id?null:p.id)} />
    ) : (
      <rect key={p.id} x={p.x} y={p.y} width={p.w} height={p.h} rx="8"
        fill={selPart===p.id?'#6366f1':hovPart===p.id?'#a5b4fc':p.fill}
        stroke="#fff" strokeWidth="2" style={{cursor:'pointer',transition:'fill 0.2s'}}
        onMouseEnter={()=>setHovPart(p.id)} onMouseLeave={()=>setHovPart(null)}
        onClick={()=>setSelPart(selPart===p.id?null:p.id)} />
    ))}
    {parts.map(p => (
      <text key={p.id+'_l'}
        x={p.cx!==undefined?p.cx:p.x+p.w/2} y={(p.cy!==undefined?p.cy:p.y+p.h/2)+4}
        textAnchor="middle" fontSize="10" fill="#fff"
        style={{pointerEvents:'none',fontWeight:700}}>{p.name}</text>
    ))}
  </svg>

═══════════════════════════════════════
IF YOU CHOOSE HTML — follow these rules
═══════════════════════════════════════

OUTPUT RULES (HTML):
1.  A complete, self-contained HTML file — DOCTYPE through </html>
2.  All CSS in a <style> block in <head>
3.  All JavaScript in a <script> block before </body>
4.  No external dependencies except Tailwind CDN if needed:
    <script src="https://cdn.tailwindcss.com"></script>
5.  Must be fully interactive using vanilla JS
6.  OUTPUT MUST BE COMPLETE — closing </body></html> required
7.  Zero markdown fences. Raw HTML only.

DESIGN (HTML):
  Use modern CSS: gradients, border-radius, box-shadow, transitions
  Hover effects via :hover CSS or JS mouseover/mouseout
  Clean sans-serif fonts, indigo/blue accent colours
  Mobile-responsive with CSS flexbox/grid

══════════════════════════════════════
COMPONENT QUALITY REQUIREMENTS
══════════════════════════════════════
- Include ALL real data (all 28+ Indian states, all 8 planets, etc.)
- Every item must be hoverable and clickable with a detail panel
- Search/filter bar mandatory when more than 8 items
- Rich detail panel showing ALL fields when item is clicked
- Smooth transitions and entrance animations
- Polished, production-quality appearance"""


REPAIR_JSX_SYSTEM = """You are a JSX repair specialist.
Fix the broken React component below based on the listed errors.
Output the COMPLETE FIXED code — nothing omitted.

RULES:
- Raw JSX only. No markdown. No ```.
- No import/export. No ReactDOM.
- All hooks: React.useState  React.useEffect  React.useRef
- className= not class=. No .forEach(). No placeholder props.
- Every { closed. Every ( closed. Every <div> has </div>.
- First line: function App() {
- Last line:  render(<App />);
Output complete fixed code only."""


REPAIR_HTML_SYSTEM = """You are an HTML repair specialist.
Fix the broken HTML below based on the listed errors.
Output the COMPLETE FIXED HTML — nothing omitted.

RULES:
- Complete self-contained HTML from <!DOCTYPE html> to </html>
- All CSS in <style>, all JS in <script>
- No markdown fences. No external dependencies except CDN links already present.
- OUTPUT MUST END WITH </body></html>
Output complete fixed HTML only."""


# ─────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok", "message": "Backend running — DeepSeek via NVIDIA"}


@app.post("/generate-ui")
async def generate_ui(req: PromptRequest):
    print(f"\n{'='*60}\nPROMPT: {req.prompt}\n{'='*60}")

    try:
        # ── Single call: user prompt → generator ─────────────
        user_message = (
            f"Create an interactive UI component for this request:\n\n"
            f"{req.prompt}\n\n"
            f"Choose JSX or HTML based on what best fits the request.\n"
            f"For maps, diagrams, calculators with state → use JSX.\n"
            f"For simpler visuals → use HTML.\n\n"
            f"CRITICAL:\n"
            f"- Output must be 100% complete — no truncation.\n"
            f"- JSX: first line 'function App() {{', last line 'render(<App />);'\n"
            f"- HTML: complete from <!DOCTYPE html> to </html>\n"
            f"- All data must be real and complete (e.g. all Indian states).\n"
            f"- Every item must be interactive (hover + click + detail panel)."
        )

        code = call_model(
            messages=[
                {"role": "system", "content": GENERATOR_PROMPT},
                {"role": "user",   "content": user_message},
            ],
            model=GENERATOR_MODEL,
            temperature=0.3,
            max_tokens=4000,
        )
        print(f"GEN attempt 1: {len(code)} chars")

        # ── Detect output type ────────────────────────────────
        output_type = detect_type(code)
        print(f"Detected type: {output_type}")

        # ── Validate + Repair loop ────────────────────────────
        for attempt in range(MAX_REPAIR_ATTEMPTS):

            if output_type == "html":
                code = pre_clean_html(code)
                errors = validate_html(code)
            else:
                code = pre_clean_jsx(code)
                errors = validate_jsx(code)

            if not errors:
                print(f"PASSED on attempt {attempt + 1}")
                break

            print(f"Attempt {attempt + 1} — {len(errors)} error(s):")
            for e in errors:
                print(f"  * {e}")

            if attempt == MAX_REPAIR_ATTEMPTS - 1:
                print("Max repair attempts reached — sending best-effort code")
                break

            error_list = "\n".join(f"- {e}" for e in errors)

            if output_type == "html":
                repair_system = REPAIR_HTML_SYSTEM
                repair_user = (
                    f"Fix these errors:\n{error_list}\n\n"
                    f"BROKEN HTML:\n{code}\n\n"
                    f"Output the complete fixed HTML ending with </body></html>"
                )
            else:
                repair_system = REPAIR_JSX_SYSTEM
                repair_user = (
                    f"Fix these errors:\n{error_list}\n\n"
                    f"BROKEN CODE:\n{code}\n\n"
                    f"Output the complete fixed component.\n"
                    f"First line: function App() {{\n"
                    f"Last line:  render(<App />);"
                )

            code = call_model(
                messages=[
                    {"role": "system", "content": repair_system},
                    {"role": "user",   "content": repair_user},
                ],
                model=REPAIR_MODEL,
                temperature=0.1,
                max_tokens=4000,
            )
            print(f"Repair {attempt + 1}: {len(code)} chars")

        # ── Final clean pass ──────────────────────────────────
        if output_type == "html":
            code = pre_clean_html(code)
        else:
            code = pre_clean_jsx(code)

        print(f"FINAL ({output_type}): {len(code)} chars\n{code[:150]}")

        return {
            "output_type": output_type,   # 'jsx' or 'html'
            "generated_code": code,
        }

    except Exception as e:
        print(f"ERROR: {e}")
        return {"error": str(e)}
