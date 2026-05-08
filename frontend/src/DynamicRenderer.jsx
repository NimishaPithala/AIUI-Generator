{/*

import React from "react";
import {
  LiveProvider,
  LivePreview,
  LiveError,
} from "react-live";

// Inject Tailwind CDN once
let _twDone = false;

function injectTailwind() {
  if (_twDone) return;

  _twDone = true;

  if (
    !document.querySelector(
      'script[src*="tailwindcss"]'
    )
  ) {
    const s = document.createElement("script");

    s.src =
      "https://cdn.tailwindcss.com";

    document.head.appendChild(s);
  }
}

// ========================================
// CLEAN AI GENERATED CODE
// ========================================

function clean(raw) {

  let code = raw || "";

  // ------------------------------------
  // Remove markdown
  // ------------------------------------

  code = code
    .replace(/^```[\w]*\n?/gm, "")
    .replace(/^```\s*$/gm, "");

  // ------------------------------------
  // Remove imports
  // ------------------------------------

  code = code.replace(
    /^import[\s\S]*?from\s+['"][^'"]+['"];?\s*\n/gm,
    ""
  );

  code = code.replace(
    /^import\s+['"][^'"]+['"];?\s*\n/gm,
    ""
  );

  // ------------------------------------
  // Remove exports
  // ------------------------------------

  code = code.replace(
    /\bexport\s+default\s+/g,
    ""
  );

  code = code.replace(
    /\bexport\s+/g,
    ""
  );

  // ------------------------------------
  // Remove render(<App />)
  // IMPORTANT FIX
  // ------------------------------------

  code = code.replace(
    /render\s*\(\s*<App\s*\/>\s*\)\s*;?/g,
    ""
  );

  // ------------------------------------
  // Replace hooks
  // ------------------------------------

  const hooks = [
    "useState",
    "useEffect",
    "useRef",
    "useMemo",
    "useCallback",
    "useReducer",
    "useContext",
    "useLayoutEffect",
  ];

  hooks.forEach((h) => {

    const re = new RegExp(
      `(?<!React\\.)(?<![a-zA-Z0-9_$])(${h})\\s*\\(`,
      "g"
    );

    code = code.replace(
      re,
      `React.${h}(`
    );
  });

  // ------------------------------------
  // class → className
  // ------------------------------------

  code = code.replace(
    /(\s)class=/g,
    "$1className="
  );

  code = code.replace(
    /^class=/gm,
    "className="
  );

  // ------------------------------------
  // IMPORTANT:
  // Return App component
  // ------------------------------------

  if (!code.includes("return <App")) {

    code += `

<App />
`;
  }

  return code.trim();
}

// ========================================
// GLOBAL SCOPE
// ========================================

const SCOPE = {
  React,
  Math,
  Date,
  JSON,
  parseInt,
  parseFloat,
  isNaN,
  isFinite,
  encodeURIComponent,
  decodeURIComponent,
  Array,
  Object,
  String,
  Number,
  Boolean,
  Map,
  Set,
  RegExp,
  setTimeout,
  clearTimeout,
  setInterval,
  clearInterval,
  console,
};

// ========================================
// COMPONENT
// ========================================

export default function DynamicRenderer({
  code,
}) {

  injectTailwind();

  const cleaned = clean(code);

  console.log("CLEANED CODE:");
  console.log(cleaned);

  return (

    <div
      style={{
        borderRadius: "16px",
        overflow: "hidden",
        border:
          "1px solid rgba(255,255,255,0.1)",
        boxShadow:
          "0 20px 50px rgba(0,0,0,0.45)",
      }}
    >

      <LiveProvider
        code={cleaned}
        scope={SCOPE}
      >

        <LiveError
          style={{
            background:
              "rgba(239,68,68,0.18)",

            borderBottom:
              "1px solid rgba(239,68,68,0.35)",

            color: "#fca5a5",

            padding: "0.75rem 1rem",

            fontSize: "0.78rem",

            fontFamily: "monospace",

            whiteSpace: "pre-wrap",

            maxHeight: "180px",

            overflowY: "auto",
          }}
        />

        <div
          style={{
            background: "#f8fafc",
            minHeight: "220px",
            padding: "20px",
          }}
        >

          <LivePreview />

        </div>

      </LiveProvider>

    </div>
  );
}
*/}

import React from "react";
import { LiveProvider, LivePreview, LiveError } from "react-live";

// Inject Tailwind once
let _tw = false;
function injectTailwind() {
  if (_tw) return;
  _tw = true;
  if (!document.querySelector('script[src*="tailwindcss"]')) {
    const s = document.createElement("script");
    s.src = "https://cdn.tailwindcss.com";
    document.head.appendChild(s);
  }
}

function cleanCode(raw) {
  if (!raw) return 'function App(){return <div>Nothing generated yet.</div>;}';

  let code = raw;

  // 1. Strip markdown fences  (``` with any language tag)
  code = code.replace(/^```[a-zA-Z]*\r?\n?/gm, "");
  code = code.replace(/^```\s*$/gm, "");

  // 2. Strip import lines (handles multi-line destructured imports)
  code = code.replace(/^import\s[\s\S]*?from\s+['"][^'"]+['"];?\s*$/gm, "");
  code = code.replace(/^import\s+['"][^'"]+['"];?\s*$/gm, "");

  // 3. Strip export
  code = code.replace(/\bexport\s+default\s+/g, "");
  code = code.replace(/\bexport\s+/g, "");

  // 4. Fix bare hooks → React.hook
  //    Regex: preceded by non-word/non-dot character (start, space, =, (, comma …)
  const hooks = [
    "useState","useEffect","useRef","useMemo",
    "useCallback","useReducer","useContext","useLayoutEffect",
  ];
  hooks.forEach(h => {
    // Replace only when not already preceded by "React."
    const re = new RegExp(`(?
    /^\s*(\/\/|function |const |let |var |class |return |render\(|<)/.test(l)
  );
  if (firstCodeLine > 0) code = lines.slice(firstCodeLine).join("\n");

  // 7. Ensure exactly ONE render() call at the very end
  //    Strip any existing render() call first
  code = code.replace(/\nrender\s*\(\s*<\s*App\s*\/?\s*>\s*\)\s*;?\s*$/g, "");
  code = code.trimEnd();
  code += "\n\nrender();";

  return code.trim();
}

// Full scope — every global the LLM might reference
const SCOPE = {
  React,
  Math, Date, JSON,
  parseInt, parseFloat, isNaN, isFinite,
  encodeURIComponent, decodeURIComponent,
  Array, Object, String, Number, Boolean, Map, Set, RegExp,
  setTimeout, clearTimeout, setInterval, clearInterval,
  console,
};

// Friendly error card shown below the preview when react-live reports an error
function ErrorCard({ message }) {
  return (
    <div style={{
      background:"#fff1f2", border:"1px solid #fecdd3",
      borderRadius:"12px", padding:"1.25rem 1.5rem",
      fontFamily:"monospace", fontSize:"13px",
      color:"#9f1239", whiteSpace:"pre-wrap", wordBreak:"break-word",
    }}>
      <div style={{fontWeight:700,marginBottom:"0.5rem",
                   fontFamily:"sans-serif",fontSize:"14px"}}>
        ⚠️ JSX render error — model produced invalid syntax
      </div>
      <div style={{opacity:0.8,fontSize:"12px"}}>{message}</div>
      <div style={{marginTop:"1rem",fontSize:"12px",
                   fontFamily:"sans-serif",color:"#be123c"}}>
        Try regenerating — occasionally the model outputs malformed code.
        Check the browser console for the cleaned code that was sent to react-live.
      </div>
    </div>
  );
}

export default function DynamicRenderer({ code }) {
  injectTailwind();
  const cleaned = cleanCode(code);

  // Always log in dev so you can inspect exactly what react-live receives
  console.groupCollapsed("[DynamicRenderer] cleaned code sent to react-live");
  console.log(cleaned);
  console.groupEnd();

  return (
    <div style={{
      borderRadius:"16px", overflow:"hidden",
      border:"1px solid rgba(255,255,255,0.12)",
      boxShadow:"0 20px 50px rgba(0,0,0,0.4)",
    }}>
      <LiveProvider code={cleaned} noInline={true} scope={SCOPE}>
        {/* Show error above preview so both are visible */}
        <LiveError
          style={{
            background:"rgba(239,68,68,0.16)",
            borderBottom:"1px solid rgba(239,68,68,0.3)",
            color:"#fca5a5", padding:"0.75rem 1rem",
            fontSize:"0.77rem", fontFamily:"monospace",
            whiteSpace:"pre-wrap", maxHeight:"200px", overflowY:"auto",
          }}
        />
        <div style={{background:"#f8fafc", minHeight:"260px"}}>
          <LivePreview />
        </div>
      </LiveProvider>
    </div>
  );
}
