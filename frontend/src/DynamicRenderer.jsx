{/*
import React from "react";
import { LiveProvider, LivePreview, LiveError } from "react-live";

// Inject Tailwind CDN once into the page so generated className styling works
let _twDone = false;
function injectTailwind() {
  if (_twDone) return;
  _twDone = true;
  if (!document.querySelector('script[src*="tailwindcss"]')) {
    const s = document.createElement("script");
    s.src = "https://cdn.tailwindcss.com";
    document.head.appendChild(s);
  }
}

// Clean AI-generated code so react-live can run it
function clean(raw) {
  let code = raw || "";

  // Remove markdown fences
  code = code.replace(/^```[\w]*\n?/gm, "").replace(/^```\s*$/gm, "");

  // Remove ALL import lines (handles multi-line imports too)
  code = code.replace(/^import[\s\S]*?from\s+['"][^'"]+['"];?\s*\n/gm, "");
  code = code.replace(/^import\s+['"][^'"]+['"];?\s*\n/gm, "");

  // Remove export
  code = code.replace(/\bexport\s+default\s+/g, "");
  code = code.replace(/\bexport\s+/g, "");

  // Fix bare hook calls → React.hookName
  // Only replace when NOT already prefixed with "React."
  const hooks = [
    "useState","useEffect","useRef","useMemo",
    "useCallback","useReducer","useContext","useLayoutEffect",
  ];
  hooks.forEach(h => {
    // Negative lookbehind: not preceded by "React." or a word char
    const re = new RegExp(`(?<!React\\.)(?<![a-zA-Z0-9_$])(${h})\\s*\\(`, "g");
    code = code.replace(re, `React.${h}(`);
  });

  // Fix class= → className=  (only in JSX attribute position)
  code = code.replace(/(\s)class=/g, "$1className=");
  code = code.replace(/^class=/gm, "className=");

  // Ensure render() at the end
  const trimmed = code.trimEnd();
  if (!trimmed.includes("render(")) {
    code = trimmed + "\n\nrender(<App />);";
  }

  return code.trim();
}

// Extra globals the LLM-generated code commonly uses
const SCOPE = {
  React,
  Math, Date, JSON,
  parseInt, parseFloat, isNaN, isFinite,
  encodeURIComponent, decodeURIComponent,
  Array, Object, String, Number, Boolean, Map, Set, RegExp,
  setTimeout, clearTimeout, setInterval, clearInterval,
  console,
};

export default function DynamicRenderer({ code }) {
  injectTailwind();
  const cleaned = clean(code);

  return (
    <div
      style={{
        borderRadius: "16px",
        overflow: "hidden",
        border: "1px solid rgba(255,255,255,0.1)",
        boxShadow: "0 20px 50px rgba(0,0,0,0.45)",
      }}
    >
      <LiveProvider code={cleaned} noInline={true} scope={SCOPE}>
       
        <LiveError
          style={{
            background: "rgba(239,68,68,0.18)",
            borderBottom: "1px solid rgba(239,68,68,0.35)",
            color: "#fca5a5",
            padding: "0.75rem 1rem",
            fontSize: "0.78rem",
            fontFamily: "monospace",
            whiteSpace: "pre-wrap",
            maxHeight: "180px",
            overflowY: "auto",
          }}
        />
        
        <div style={{ background: "#f8fafc", minHeight: "220px" }}>
          <LivePreview />
        </div>
      </LiveProvider>
    </div>
  );
}
*/}

import React from "react";
import { LiveProvider, LivePreview, LiveError } from "react-live";

// ── Inject Tailwind once so className styling works in generated components ──
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

// ── Aggressively clean LLM output so react-live can parse it ──
function cleanCode(raw) {
  if (!raw) return 'function App(){return 
No code generated
}\nrender();';

  let code = raw;

  // 1. Strip ALL markdown fences (```jsx, ```javascript, ```tsx, ```, etc.)
  code = code.replace(/```[a-zA-Z]*\n?/g, "");
  code = code.replace(/```/g, "");

  // 2. Strip every import line (single-line and multi-line destructured)
  code = code.replace(/^import\s[\s\S]*?;[ \t]*$/gm, "");

  // 3. Strip export keywords
  code = code.replace(/\bexport\s+default\s+/g, "");
  code = code.replace(/\bexport\s+/g, "");

  // 4. Fix bare React hooks → React.hookName(
  //    Only replaces when NOT already preceded by "React." or a word character
  [
    "useState","useEffect","useRef","useMemo",
    "useCallback","useReducer","useContext","useLayoutEffect",
  ].forEach(hook => {
    // Match the hook name when preceded by a non-word char (space, newline, = , ( etc.)
    // but NOT when preceded by "React."
    const re = new RegExp(`(^|[^a-zA-Z0-9_$.])${hook}\\s*\\(`, "gm");
    code = code.replace(re, (match, pre) => {
      // If the character before is ".", it's already namespaced — leave it
      if (pre === ".") return match;
      return `${pre}React.${hook}(`;
    });
  });

  // 5. class= → className=
  code = code.replace(/\bclass=/g, "className=");

  // 6. Remove any leading/trailing prose lines that aren't JSX/JS
  //    Keep only lines that look like code (heuristic: contains {, }, =, <, //, const, etc.)
  const lines = code.split("\n");
  const firstCode = lines.findIndex(l =>
    /^\s*(function|const|let|var|class |\/\/|import|export|render|return|\{|<)/.test(l)
  );
  if (firstCode > 0) code = lines.slice(firstCode).join("\n");

  // 7. Ensure there's exactly one render() call at the very end
  //    Remove any existing render() calls first, then add one clean one
  code = code.replace(/\nrender\s*\(\s*<[^>]+\s*\/?\s*>\s*\)\s*;?\s*$/g, "");
  code = code.trimEnd();
  code += "\n\nrender();";

  return code.trim();
}

// ── Scope: everything the LLM-generated code might reference globally ──
const SCOPE = {
  React,
  // Math / number utilities
  Math, Number, parseInt, parseFloat, isNaN, isFinite,
  // String / array / object
  String, Array, Object, Boolean, Map, Set, RegExp, JSON,
  // Timers
  setTimeout, clearTimeout, setInterval, clearInterval,
  // Misc
  console, encodeURIComponent, decodeURIComponent,
  Date,
};

// ── Fallback shown when LiveError fires ──
function ErrorDisplay({ error }) {
  return (
    <div style={{
      background: "#fff1f2",
      border: "1px solid #fecdd3",
      borderRadius: "12px",
      padding: "1.25rem 1.5rem",
      fontFamily: "monospace",
      fontSize: "13px",
      color: "#9f1239",
      whiteSpace: "pre-wrap",
      wordBreak: "break-word",
    }}>
      <div style={{ fontWeight: 700, marginBottom: "0.5rem", fontFamily: "sans-serif" }}>
        ⚠️ Render error — the model produced invalid JSX
      </div>
      <div style={{ opacity: 0.8 }}>{error}</div>
      <div style={{
        marginTop: "1rem", fontSize: "12px",
        fontFamily: "sans-serif", color: "#be123c",
      }}>
        Try regenerating — the model occasionally outputs malformed code.
      </div>
    </div>
  );
}

export default function DynamicRenderer({ code }) {
  injectTailwind();
  const cleaned = cleanCode(code);

  // Log cleaned code in dev so you can debug what react-live receives
  if (import.meta.env.DEV) {
    console.groupCollapsed("[DynamicRenderer] cleaned code");
    console.log(cleaned);
    console.groupEnd();
  }

  return (
    <div style={{
      borderRadius: "16px",
      overflow: "hidden",
      border: "1px solid rgba(255,255,255,0.12)",
      boxShadow: "0 20px 50px rgba(0,0,0,0.4)",
    }}>
      <LiveProvider code={cleaned} noInline={true} scope={SCOPE}>
        <LiveError
          style={{ display: "none" }} /* hide default LiveError — we use custom below */
        />
        <div style={{ background: "#f8fafc", minHeight: "240px" }}>
          <LivePreview />
        </div>
      </LiveProvider>
    </div>
  );
}
