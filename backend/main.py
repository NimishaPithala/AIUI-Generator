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
# STEP 1 — Pre-clean raw LLM output (Python-side)
# ─────────────────────────────────────────────────────────────
def pre_clean(code: str) -> str:
    """Strip all non-JSX wrapping that the LLM adds."""

    # Remove markdown fences
    code = re.sub(r"^```[a-zA-Z]*\r?\n?", "", code, flags=re.MULTILINE)
    code = re.sub(r"^```\s*$", "", code, flags=re.MULTILINE)

    # Remove import lines
    code = re.sub(
        r"^import\s[\s\S]*?from\s+['\"][^'\"]+['\"];?\s*$",
        "",
        code,
        flags=re.MULTILINE,
    )

    code = re.sub(
        r"^import\s+['\"][^'\"]+['\"];?\s*$",
        "",
        code,
        flags=re.MULTILINE,
    )

    # Remove export keywords
    code = re.sub(r"\bexport\s+default\s+", "", code)
    code = re.sub(r"\bexport\s+", "", code)

    # Fix bare hooks → React.hook
    hooks = [
        "useState",
        "useEffect",
        "useRef",
        "useMemo",
        "useCallback",
        "useReducer",
        "useContext",
        "useLayoutEffect",
    ]

    for hook in hooks:
        pattern = rf"(?<!React\.)\b{hook}\s*\("
        replacement = f"React.{hook}("
        code = re.sub(pattern, replacement, code)

    # Remove duplicate render() calls at end
    code = re.sub(
        r"\nrender\s*\(\s*(?:React\.createElement\(App\)|<\s*App\s*/?>\s*)\)\s*;?\s*$",
        "",
        code.rstrip(),
        flags=re.MULTILINE,
    )

    # Ensure exactly one render() call
    code = code.rstrip() + "\n\nrender();"

    return code.strip()


# ─────────────────────────────────────────────────────────────
# STEP 2 — Validate cleaned code, return list of problems
# ─────────────────────────────────────────────────────────────
def validate_code(code: str) -> list[str]:
    """
    Returns a list of error strings.
    Empty list = code passes all checks.
    """

    errors = []

    # Must start with function App()
    if not re.search(r"function\s+App\s*\(", code):
        errors.append(
            "MISSING: The component function must be named exactly 'App'. "
            "Start your output with: function App() {"
        )

    # Must end with render()
    if not re.search(
        r"render\s*\(\s*(?:React\.createElement\(App\)|<\s*App\s*/?>)?\s*\)\s*;?\s*$",
        code.strip(),
    ):
        errors.append(
            "MISSING: Last line must be exactly: render();"
        )

    # Must not contain imports
    if re.search(r"^import\s", code, re.MULTILINE):
        errors.append(
            "FORBIDDEN: Remove all import statements. "
            "Do not import anything — no React, no hooks, nothing."
        )

    # Must not contain export
    if re.search(r"\bexport\b", code):
        errors.append(
            "FORBIDDEN: Remove all 'export' keywords."
        )

    # Bare hooks
    bare_hooks = [
        "useState",
        "useEffect",
        "useRef",
        "useMemo",
        "useCallback",
        "useReducer",
        "useContext",
        "useLayoutEffect",
    ]

    for hook in bare_hooks:
        pattern = rf"(?<!React\.)\b{hook}\s*\("
        if re.search(pattern, code):
            errors.append(
                f"FORBIDDEN: Bare hook detected: {hook}. "
                f"Use React.{hook}() instead."
            )

    # Multiple render calls
    if len(re.findall(r"render\s*\(", code)) > 1:
        errors.append(
            "FORBIDDEN: Multiple render() calls detected."
        )

    # Duplicate App definitions
    if len(re.findall(r"function\s+App\s*\(", code)) > 1:
        errors.append(
            "FORBIDDEN: Multiple App() component definitions detected."
        )

    return errors


# ─────────────────────────────────────────────────────────────
# REPAIR SYSTEM PROMPT
# ─────────────────────────────────────────────────────────────
REPAIR_SYSTEM = """
You are a React JSX syntax repair engine.

Rules:
- Fix ONLY the listed errors.
- Keep everything else identical.
- Do not add explanations.
- Output ONLY the complete corrected JSX code.
"""


# ─────────────────────────────────────────────────────────────
# PLANNER PROMPT
# ─────────────────────────────────────────────────────────────
PLANNER_PROMPT = """
You are an expert educational UI/UX planner.

Analyse the user's request and write a precise instruction for a React/SVG engineer.

COMPONENT TYPE — choose the best fit:
  • CARD GRID
  • SVG MAP
  • SVG DIAGRAM
  • TIMELINE
  • CALCULATOR
  • QUIZ

SVG MAP rules:
  - Specify SVG path data for every region.
  - Include id, name, label positions.

SVG DIAGRAM rules:
  - Each part should define SVG shape data.

CARD GRID rules:
  - Include at least 5 fields per item.
  - Search bar required for >8 items.
  - Detail panel below grid.

Output ONLY the instruction.
"""


# ─────────────────────────────────────────────────────────────
# GENERATOR PROMPT
# ─────────────────────────────────────────────────────────────
GENERATOR_PROMPT = """
You are a React + SVG engineer.

Output ONE raw JSX component.

ABSOLUTE RULES:
1. No markdown fences.
2. No imports.
3. No exports.
4. Hooks must use React.useState / React.useEffect etc.
5. Use className= not class=
6. No external libraries.
7. Component name must be App
8. First line: function App() {
9. Last line: render();
10. Use .map() inside JSX, never .forEach()

DESIGN:
Page:
className="min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50 p-6 font-sans"

Cards:
className="bg-white rounded-2xl shadow-md border border-gray-100 p-4 cursor-pointer transition-all duration-200"

Search:
className="w-full border border-gray-200 rounded-xl px-4 py-2 mb-4 text-gray-800 outline-none focus:ring-2 focus:ring-indigo-300"

Detail:
className="bg-white rounded-2xl shadow-xl border border-indigo-100 p-6 mt-6"

Entrance animation:
const [mounted, setMounted] = React.useState(false);
React.useEffect(() => {
  const t = setTimeout(() => setMounted(true), 50);
  return () => clearTimeout(t);
}, []);

style={{
  opacity: mounted ? 1 : 0,
  transform: mounted ? 'none' : 'translateY(16px)',
  transition: 'all 0.4s ease'
}}

START with: function App() {
END with: render();
"""


# ─────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Backend running",
    }


@app.post("/generate-ui")
async def generate_ui(req: PromptRequest):
    print(f"\n{'=' * 60}\nPROMPT: {req.prompt}\n{'=' * 60}")

    try:
        # ── PLANNER ──────────────────────────────────────────
        plan_res = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": PLANNER_PROMPT,
                },
                {
                    "role": "user",
                    "content": req.prompt,
                },
            ],
            temperature=0.7,
            max_tokens=800,
        )

        plan = plan_res.choices[0].message.content.strip()

        print(f"PLAN:\n{plan[:300]}\n")

        # ── GENERATOR ─────────────────────────────────────────
        gen_res = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": GENERATOR_PROMPT,
                },
                {
                    "role": "user",
                    "content": (
                        f"{plan}\n\n"
                        "REMINDERS:\n"
                        "- First line: function App() {\n"
                        "- Last line: render();\n"
                        "- No imports, exports, or markdown fences.\n"
                        "- Hooks must use React.useState / React.useEffect\n"
                        "- Use .map() in JSX\n"
                        "- Detail panel BELOW cards\n"
                    ),
                },
            ],
            temperature=0.3,
            max_tokens=3500,
        )

        code = gen_res.choices[0].message.content.strip()

        print(f"ATTEMPT 1 — raw code ({len(code)} chars)")

        # ── VALIDATE + REPAIR LOOP ────────────────────────────
        for attempt in range(MAX_REPAIR_ATTEMPTS):

            # Pre-clean
            code = pre_clean(code)

            print(
                f"ATTEMPT {attempt + 1} — after pre_clean ({len(code)} chars)"
            )

            # Validate
            errors = validate_code(code)

            if not errors:
                print(f"✅ Code passed validation on attempt {attempt + 1}")
                break

            print(f"❌ Attempt {attempt + 1} found {len(errors)} error(s):")

            for e in errors:
                print(f"   • {e}")

            if attempt == MAX_REPAIR_ATTEMPTS - 1:
                print(
                    "⚠️ Max repair attempts reached — sending best-effort code"
                )
                break

            # Repair
            error_list = "\n".join(f"- {e}" for e in errors)

            repair_res = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": REPAIR_SYSTEM,
                    },
                    {
                        "role": "user",
                        "content": (
                            "Fix the following React JSX errors.\n\n"
                            f"ERRORS:\n{error_list}\n\n"
                            f"BROKEN CODE:\n{code}\n\n"
                            "Output ONLY the corrected complete code.\n"
                            "First line: function App() {\n"
                            "Last line: render();"
                        ),
                    },
                ],
                temperature=0.1,
                max_tokens=3500,
            )

            code = repair_res.choices[0].message.content.strip()

            print(f"REPAIR {attempt + 1} done ({len(code)} chars)")

        # Final clean
        code = pre_clean(code)

        print(f"FINAL code ({len(code)} chars)\n{code[:200]}...")

        return {
            "planner_instruction": plan,
            "generated_code": code,
        }

    except Exception as e:
        print(f"ERROR: {e}")

        return {
            "error": str(e),
        }
