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

// Inject Tailwind once so className works in generated components
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

// ── FALLBACK — NO JSX angle brackets in this string (Babel would choke) ──
const FALLBACK = [
  "function App() {",
  "  return React.createElement(",
  "    'div',",
  "    { style: { padding: '2rem', color: '#6b7280', fontFamily: 'sans-serif' } },",
  "    'Nothing generated yet.'",
  "  );",
  "}",
  "render(React.createElement(App));",
].join("\n");

// ── Frontend cleaner — last line of defence after Python pre_clean ──
function cleanCode(raw) {
  if (!raw || !raw.trim()) return FALLBACK;

  let code = raw;

  // Strip markdown fences
  code = code.replace(/^```[a-zA-Z]*\r?\n?/gm, "");
  code = code.replace(/^```\s*$/gm, "");

  // Strip imports
  code = code.replace(/^import[\s\S]*?from\s+['"][^'"]+['"];?\s*$/gm, "");
  code = code.replace(/^import\s+['"][^'"]+['"];?\s*$/gm, "");

  // Strip export
  code = code.replace(/\bexport\s+default\s+/g, "");
  code = code.replace(/\bexport\s+/g, "");

  // Fix bare hooks
  const hooks = [
    "useState","useEffect","useRef","useMemo",
    "useCallback","useReducer","useContext","useLayoutEffect",
  ];
  hooks.forEach((h) => {
    const re = new RegExp(`(?
    /^\s*(\/\/|\/\*|function |const |let |var |render\s*\()/.test(l)
  );
  if (first > 0) code = lines.slice(first).join("\n");

  // Ensure one render() at end
  code = code.replace(
    /\nrender\s*\(\s*(?:React\.createElement\(App\)|<\s*App\s*\/?>\s*)\)\s*;?\s*$/g,
    ""
  );
  code = code.trimEnd() + "\n\nrender();";

  return code.trim();
}

// Scope passed into every generated component
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
  const cleaned = cleanCode(code);

  console.groupCollapsed("[DynamicRenderer] cleaned code → react-live");
  console.log(cleaned);
  console.groupEnd();

  return (
    <div
      style={{
        borderRadius: "16px",
        overflow: "hidden",
        border: "1px solid rgba(255,255,255,0.12)",
        boxShadow: "0 20px 50px rgba(0,0,0,0.4)",
      }}
    >
      <LiveProvider code={cleaned} noInline={true} scope={SCOPE}>
        <LiveError
          style={{
            background: "rgba(239,68,68,0.16)",
            borderBottom: "1px solid rgba(239,68,68,0.3)",
            color: "#fca5a5",
            padding: "0.75rem 1rem",
            fontSize: "0.77rem",
            fontFamily: "monospace",
            whiteSpace: "pre-wrap",
            maxHeight: "200px",
            overflowY: "auto",
          }}
        />
        <div style={{ background: "#f8fafc", minHeight: "260px" }}>
          <LivePreview />
        </div>
      </LiveProvider>
    </div>
  );
}
