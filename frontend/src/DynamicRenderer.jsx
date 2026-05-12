{/*

import React from "react";
import { LiveProvider, LivePreview, LiveError } from "react-live";

// ─────────────────────────────────────────────────────────────
// FALLBACK — built with React.createElement so Babel never sees
// raw JSX angle-brackets inside a string literal (which causes
// "SyntaxError: Unexpected token" at compile time).
// ─────────────────────────────────────────────────────────────
const FALLBACK = [
  "function App() {",
  "  return React.createElement(",
  "    'div',",
  "    { style: { padding: '2rem', color: '#6b7280',",
  "               fontFamily: 'sans-serif', fontSize: '1rem' } },",
  "    'Nothing generated yet.'",
  "  );",
  "}",
  "render(React.createElement(App));",
].join("\n");

// ─────────────────────────────────────────────────────────────
// CLEANER — last safety net after Python pre_clean
// ─────────────────────────────────────────────────────────────
function cleanCode(raw) {
  if (!raw || !raw.trim()) return FALLBACK;

  let code = raw;

  // Strip markdown fences
  code = code.replace(/^```[a-zA-Z]*\r?\n?/gm, "");
  code = code.replace(/^```\s*$/gm, "");

  // Strip import lines
  code = code.replace(/^import[\s\S]*?from\s+['"][^'"]+['"];?\s*$/gm, "");
  code = code.replace(/^import\s+['"][^'"]+['"];?\s*$/gm, "");

  // Strip export
  code = code.replace(/\bexport\s+default\s+/g, "");
  code = code.replace(/\bexport\s+/g, "");

  // Fix bare hooks
  const hooks = [
    "useState", "useEffect", "useRef", "useMemo",
    "useCallback", "useReducer", "useContext", "useLayoutEffect",
  ];
  hooks.forEach((h) => {
    const re = new RegExp(`(?<![.\\w])${h}(?=\\s*\\()`, "g");
    code = code.replace(re, `React.${h}`);
  });

  // Fix class= -> className=
  code = code.replace(/(\s)class=/g, "$1className=");
  code = code.replace(/^class=/gm, "className=");

  // Remove ALL render() / ReactDOM.render() variants
  code = code.replace(/ReactDOM\.render\s*\([\s\S]*?\)\s*;?/g, "");
  code = code.replace(/\nrender\s*\(\s*\)\s*;?/g, "");
  code = code.replace(/\nrender\s*\(<\s*App\s*\/?[^)]*\)\s*;?/g, "");

  // Drop leading prose lines
  const lines = code.split("\n");
  const first = lines.findIndex((l) =>
    /^\s*(\/\/|\/\*|function |const |let |var |render\s*\()/.test(l)
  );
  if (first > 0) code = lines.slice(first).join("\n");

  // Add exactly one render call at end
  code = code.trimEnd() + "\n\nrender(<App />);";

  return code.trim();
}

// ─────────────────────────────────────────────────────────────
// SCOPE — every global the LLM-generated code might reference
// ─────────────────────────────────────────────────────────────
const SCOPE = {
  React,
  Math, Date, JSON,
  parseInt, parseFloat, isNaN, isFinite,
  encodeURIComponent, decodeURIComponent,
  Array, Object, String, Number, Boolean, Map, Set, RegExp,
  setTimeout, clearTimeout, setInterval, clearInterval,
  console,
};

// ─────────────────────────────────────────────────────────────
// RENDERER
// ─────────────────────────────────────────────────────────────
export default function DynamicRenderer({ code }) {
  const cleaned = cleanCode(code);

  // Log in browser console so you can inspect exactly what react-live gets
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
*/}

import React from "react";
import { LiveProvider, LivePreview, LiveError } from "react-live";

// ─────────────────────────────────────────────────────────────
// FALLBACK — no JSX angle-brackets inside strings (Babel would choke)
// ─────────────────────────────────────────────────────────────
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

// ─────────────────────────────────────────────────────────────
// JSX CLEANER — final safety net after Python pre_clean
// ─────────────────────────────────────────────────────────────
function cleanJSX(raw) {
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
    const re = new RegExp(`(?<![.\\w])${h}(?=\\s*\\()`, "g");
    code = code.replace(re, `React.${h}`);
  });

  // Fix class= → className=
  code = code.replace(/(\s)class=/g, "$1className=");
  code = code.replace(/^class=/gm, "className=");

  // Remove all render() / ReactDOM.render() variants
  code = code.replace(/ReactDOM\.render\s*\([\s\S]*?\)\s*;?/g, "");
  code = code.replace(/\nrender\s*\(\s*\)\s*;?/g, "");
  code = code.replace(/\nrender\s*\(<\s*App\s*\/?[^)]*\)\s*;?/g, "");

  // Drop leading prose
  const lines = code.split("\n");
  const first = lines.findIndex((l) =>
    /^\s*(\/\/|\/\*|function |const |let |var |render\s*\()/.test(l)
  );
  if (first > 0) code = lines.slice(first).join("\n");

  // One clean render at end
  code = code.trimEnd() + "\n\nrender(<App />);";
  return code.trim();
}

// ─────────────────────────────────────────────────────────────
// HTML CLEANER
// ─────────────────────────────────────────────────────────────
function cleanHTML(raw) {
  if (!raw || !raw.trim()) return "<html><body><p>Nothing generated yet.</p></body></html>";
  let code = raw;
  code = code.replace(/^```[a-zA-Z]*\r?\n?/gm, "");
  code = code.replace(/^```\s*$/gm, "");
  // Find start of actual HTML
  const match = code.match(/(<!DOCTYPE|<html)/i);
  if (match) code = code.slice(code.indexOf(match[0]));
  return code.trim();
}

// ─────────────────────────────────────────────────────────────
// SCOPE for react-live
// ─────────────────────────────────────────────────────────────
const SCOPE = {
  React,
  Math, Date, JSON,
  parseInt, parseFloat, isNaN, isFinite,
  encodeURIComponent, decodeURIComponent,
  Array, Object, String, Number, Boolean, Map, Set, RegExp,
  setTimeout, clearTimeout, setInterval, clearInterval,
  console,
};

// ─────────────────────────────────────────────────────────────
// HTML RENDERER — renders via srcdoc iframe (fully isolated)
// ─────────────────────────────────────────────────────────────
function HTMLRenderer({ code }) {
  const cleaned = cleanHTML(code);
  const iframeRef = React.useRef(null);
  const [height, setHeight] = React.useState(500);

  // Auto-resize iframe to content height
  React.useEffect(() => {
    const iframe = iframeRef.current;
    if (!iframe) return;
    const onLoad = () => {
      try {
        const h = iframe.contentDocument?.body?.scrollHeight;
        if (h && h > 100) setHeight(Math.min(h + 32, 1200));
      } catch (e) { /* cross-origin */ }
    };
    iframe.addEventListener("load", onLoad);
    return () => iframe.removeEventListener("load", onLoad);
  }, [cleaned]);

  return (
    <iframe
      ref={iframeRef}
      srcDoc={cleaned}
      style={{
        width: "100%",
        height: `${height}px`,
        border: "none",
        display: "block",
        background: "#f8fafc",
      }}
      sandbox="allow-scripts allow-same-origin"
      title="Generated UI"
    />
  );
}

// ─────────────────────────────────────────────────────────────
// JSX RENDERER — renders via react-live
// ─────────────────────────────────────────────────────────────
function JSXRenderer({ code }) {
  const cleaned = cleanJSX(code);

  console.groupCollapsed("[DynamicRenderer] JSX → react-live");
  console.log(cleaned);
  console.groupEnd();

  return (
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
  );
}

// ─────────────────────────────────────────────────────────────
// MAIN EXPORT — routes to JSX or HTML renderer based on type
// ─────────────────────────────────────────────────────────────
export default function DynamicRenderer({ code, outputType }) {
  // outputType comes from the backend ('jsx' or 'html')
  // If not provided, auto-detect from code
  const type = outputType || autoDetect(code);

  return (
    <div
      style={{
        borderRadius: "16px",
        overflow: "hidden",
        border: "1px solid rgba(255,255,255,0.12)",
        boxShadow: "0 20px 50px rgba(0,0,0,0.4)",
      }}
    >
      {type === "html"
        ? <HTMLRenderer code={code} />
        : <JSXRenderer  code={code} />
      }
    </div>
  );
}

function autoDetect(code) {
  if (!code) return "jsx";
  const c = code.trim().toLowerCase();
  if (c.startsWith("<!doctype") || c.startsWith("<html")) return "html";
  if (c.includes("<html") && c.includes("</html>")) return "html";
  return "jsx";
}
