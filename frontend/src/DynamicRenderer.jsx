import React from "react";
import { LiveProvider, LivePreview, LiveError } from "react-live";

// ─────────────────────────────────────────────
// Tailwind CDN injector (runs once)
// ─────────────────────────────────────────────
let tailwindInjected = false;
function ensureTailwind() {
  if (tailwindInjected) return;
  tailwindInjected = true;
  if (!document.querySelector('script[src*="tailwindcss"]')) {
    const s = document.createElement("script");
    s.src = "https://cdn.tailwindcss.com";
    document.head.appendChild(s);
  }
}

// ─────────────────────────────────────────────
// Code cleaner
// ─────────────────────────────────────────────
function cleanCode(raw) {
  let code = raw;

  // Strip markdown fences
  code = code.replace(/^```[\w]*\n?/gm, "").replace(/^```\s*$/gm, "");

  // Strip all import lines
  code = code.replace(/^import\s+.*?;?\s*$/gm, "");

  // Strip export default
  code = code.replace(/export\s+default\s+/g, "");

  // Fix React hooks: useState( → React.useState(  (only bare calls)
  code = code.replace(/(?<!\.)(?<!\w)(useState)\s*\(/g, "React.useState(");
  code = code.replace(/(?<!\.)(?<!\w)(useEffect)\s*\(/g, "React.useEffect(");
  code = code.replace(/(?<!\.)(?<!\w)(useRef)\s*\(/g, "React.useRef(");
  code = code.replace(/(?<!\.)(?<!\w)(useMemo)\s*\(/g, "React.useMemo(");
  code = code.replace(/(?<!\.)(?<!\w)(useCallback)\s*\(/g, "React.useCallback(");
  code = code.replace(/(?<!\.)(?<!\w)(useReducer)\s*\(/g, "React.useReducer(");

  // Fix class= → className=
  code = code.replace(/\bclass=/g, "className=");

  // Fix for...of / for...in in JSX (common mistake that breaks react-live)
  // Leave as-is, react-live supports these

  // Ensure render(<App />) at end
  const trimmed = code.trimEnd();
  if (!trimmed.includes("render(")) {
    code = trimmed + "\n\nrender(<App />);";
  }

  return code.trim();
}

// ─────────────────────────────────────────────
// Scope injected into react-live
// ─────────────────────────────────────────────
const LIVE_SCOPE = {
  React,
  // Common things LLMs might reference
  console,
  Math,
  Date,
  JSON,
  parseInt,
  parseFloat,
  isNaN,
  Array,
  Object,
  String,
  Number,
  Boolean,
  Map,
  Set,
};

// ─────────────────────────────────────────────
// DynamicRenderer
// ─────────────────────────────────────────────
export default function DynamicRenderer({ code }) {
  ensureTailwind();
  const cleanedCode = cleanCode(code);

  return (
    <div
      style={{
        borderRadius: "16px",
        overflow: "hidden",
        border: "1px solid rgba(255,255,255,0.1)",
        boxShadow: "0 20px 60px rgba(0,0,0,0.5)",
      }}
    >
      <LiveProvider
        code={cleanedCode}
        noInline={true}
        scope={LIVE_SCOPE}
      >
        {/* Error display */}
        <LiveError
          style={{
            background: "rgba(239,68,68,0.15)",
            borderBottom: "1px solid rgba(239,68,68,0.3)",
            color: "#fca5a5",
            padding: "0.75rem 1rem",
            fontSize: "0.8rem",
            fontFamily: "monospace",
            whiteSpace: "pre-wrap",
            maxHeight: "160px",
            overflowY: "auto",
          }}
        />
        {/* Live preview */}
        <div
          style={{
            background: "#f8fafc",
            minHeight: "200px",
          }}
        >
          <LivePreview />
        </div>
      </LiveProvider>
    </div>
  );
}
