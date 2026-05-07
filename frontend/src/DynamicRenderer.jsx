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
        {/* Error display — only visible when there's a JSX parse/runtime error */}
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
        {/* The rendered component lives here */}
        <div style={{ background: "#f8fafc", minHeight: "220px" }}>
          <LivePreview />
        </div>
      </LiveProvider>
    </div>
  );
}
