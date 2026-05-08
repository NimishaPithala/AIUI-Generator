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

// ── Inject Tailwind CDN once so className works in generated components ──
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

// ── FALLBACK code when raw is empty ──
// IMPORTANT: No JSX angle-bracket tags inside this string.
// Use React.createElement so Babel never sees raw JSX in a string.
const FALLBACK_CODE = [
  "function App() {",
  "  return React.createElement(",
  "    'div',",
  "    { style: { padding: '2rem', color: '#6b7280', fontFamily: 'sans-serif' } },",
  "    'Nothing generated yet.'",
  "  );",
  "}",
  "render(React.createElement(App));",
].join("\n");

// ── Strip and sanitise LLM output so react-live can parse it ──
function cleanCode(raw) {
  if (!raw || !raw.trim()) return FALLBACK_CODE;

  let code = raw;

  // 1. Strip ALL markdown fences  (```jsx, ```javascript, ```, etc.)
  code = code.replace(/^```[a-zA-Z]*\r?\n?/gm, "");
  code = code.replace(/^```\s*$/gm, "");

  // 2. Strip every import line
  //    Handles:  import X from 'y';
  //              import { X } from 'y';
  //              import 'y';
  code = code.replace(/^import[\s\S]*?from\s+['"][^'"]+['"];?\s*$/gm, "");
  code = code.replace(/^import\s+['"][^'"]+['"];?\s*$/gm, "");

  // 3. Strip export keywords
  code = code.replace(/\bexport\s+default\s+/g, "");
  code = code.replace(/\bexport\s+/g, "");

  // 4. Fix bare React hooks  (must NOT already be prefixed with "React.")
  //    Pattern: the hook name is preceded by a non-word, non-dot character
  const hooks = [
    "useState", "useEffect", "useRef", "useMemo",
    "useCallback", "useReducer", "useContext", "useLayoutEffect",
  ];
  hooks.forEach((hook) => {
    // Negative lookbehind for word chars and dot — avoids double-prefixing
    const re = new RegExp(`(?
    /^\s*(\/\/|\/\*|function |const |let |var |class |return |render\s*\(|<[A-Z])/.test(l)
  );
  if (firstCode > 0) {
    code = lines.slice(firstCode).join("\n");
  }

  // 7. Guarantee exactly one render() call at the very end
  //    Strip any existing render() call first so we don't duplicate
  code = code.replace(/\nrender\s*\(\s*(?:React\.createElement\(App\)|<\s*App\s*\/?>)\s*\)\s*;?\s*$/g, "");
  code = code.trimEnd();

  // Use React.createElement form — both work in react-live with noInline=true
  // But raw JSX form is fine too because THIS string is built at runtime, not compile time
  code += "\n\nrender();";

  return code.trim();
}

// ── Scope injected into every generated component ──
const SCOPE = {
  React,
  // Math & numbers
  Math, Number, parseInt, parseFloat, isNaN, isFinite,
  // Strings, collections
  String, Array, Object, Boolean, Map, Set, RegExp, JSON,
  // Timers
  setTimeout, clearTimeout, setInterval, clearInterval,
  // Misc
  Date, console, encodeURIComponent, decodeURIComponent,
};

// ── Main renderer component ──
export default function DynamicRenderer({ code }) {
  injectTailwind();
  const cleaned = cleanCode(code);

  // Always log so you can inspect what react-live receives
  console.groupCollapsed("[DynamicRenderer] cleaned code");
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
        {/* Error banner — visible only when react-live catches a JSX/runtime error */}
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
        {/* The live rendered component */}
        <div style={{ background: "#f8fafc", minHeight: "260px" }}>
          <LivePreview />
        </div>
      </LiveProvider>
    </div>
  );
}
