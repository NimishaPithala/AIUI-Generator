{/*
import { useState, useRef, useEffect } from "react";
import API from "./api";
import DynamicRenderer from "./DynamicRenderer";

const EXAMPLES = [
  "Show all Indian states with capital, population, area and language",
  "Interactive Solar System — all 8 planets with facts",
  "Periodic table — first 20 elements, clickable with details",
  "3D Shape calculator: volume & surface area with live inputs",
  "Chemical equations visualiser for common reactions",
  "World War II timeline — key events 1939–1945",
];

export default function App() {
  const [prompt,        setPrompt]        = useState("");
  const [instruction,   setInstruction]   = useState("");
  const [generatedCode, setGeneratedCode] = useState("");
  const [loading,       setLoading]       = useState(false);
  const [error,         setError]         = useState("");
  const [showPlan,      setShowPlan]      = useState(false);
  const [showCode,      setShowCode]      = useState(false);
  const [dots,          setDots]          = useState("");
  const resultRef = useRef(null);

  // Animated loading dots
  useEffect(() => {
    if (!loading) { setDots(""); return; }
    const id = setInterval(
      () => setDots(d => (d.length >= 3 ? "" : d + ".")),
      450
    );
    return () => clearInterval(id);
  }, [loading]);

  const generate = async () => {
    if (!prompt.trim() || loading) return;
    setLoading(true);
    setError("");
    setGeneratedCode("");
    setInstruction("");
    try {
      const { data } = await API.post("/generate-ui", { prompt });
      if (data.error) {
        setError(data.error);
      } else {
        setInstruction(data.planner_instruction || "");
        setGeneratedCode(data.generated_code || "");
        setTimeout(
          () => resultRef.current?.scrollIntoView({ behavior: "smooth" }),
          200
        );
      }
    } catch (e) {
      console.error(e);
      setError(
        e.code === "ECONNABORTED"
          ? "Request timed out — backend may be waking up on Render free tier. Try again."
          : `Could not reach backend: ${e.message}`
      );
    }
    setLoading(false);
  };

  const S = {
    page: {
      minHeight: "100vh",
      background: "linear-gradient(135deg,#0f0c29 0%,#302b63 55%,#24243e 100%)",
      fontFamily: "'Segoe UI',system-ui,sans-serif",
      color: "#fff",
      paddingBottom: "5rem",
    },
    header: { textAlign: "center", padding: "3rem 1.5rem 0" },
    badge: {
      display: "inline-block", marginBottom: "1rem",
      background: "rgba(139,92,246,.15)",
      border: "1px solid rgba(139,92,246,.4)",
      borderRadius: "999px", padding: "0.3rem 1rem",
      fontSize: "0.72rem", color: "#c4b5fd",
      letterSpacing: "0.08em", textTransform: "uppercase",
    },
    h1: {
      fontSize: "clamp(1.9rem,5vw,3rem)", fontWeight: 900,
      margin: "0 0 0.5rem",
      background: "linear-gradient(90deg,#a78bfa,#60a5fa,#34d399)",
      WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
    },
    sub: {
      color: "rgba(255,255,255,.5)", fontSize: "1rem",
      maxWidth: "440px", margin: "0 auto 2.5rem",
    },
    card: {
      background: "rgba(255,255,255,.07)",
      border: "1px solid rgba(255,255,255,.12)",
      borderRadius: "20px", padding: "1.75rem",
      backdropFilter: "blur(10px)",
    },
    chipLabel: {
      fontSize: "0.7rem", color: "rgba(255,255,255,.35)",
      textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "0.5rem",
    },
    chipRow: { display: "flex", flexWrap: "wrap", gap: "0.4rem", marginBottom: "1.2rem" },
    chip: {
      background: "rgba(139,92,246,.12)",
      border: "1px solid rgba(139,92,246,.3)",
      borderRadius: "999px", padding: "0.25rem 0.75rem",
      fontSize: "0.73rem", color: "#c4b5fd", cursor: "pointer", whiteSpace: "nowrap",
    },
    textarea: {
      width: "100%",
      background: "rgba(0,0,0,.35)",
      border: "1px solid rgba(255,255,255,.15)",
      borderRadius: "12px", padding: "0.9rem 1.1rem",
      fontSize: "0.95rem", color: "#fff",
      resize: "vertical", outline: "none",
      fontFamily: "inherit", lineHeight: 1.6, boxSizing: "border-box",
    },
    btn: {
      marginTop: "0.85rem", width: "100%", padding: "0.85rem",
      background: "linear-gradient(135deg,#7c3aed,#4f46e5)",
      border: "none", borderRadius: "11px",
      color: "#fff", fontSize: "0.98rem", fontWeight: 700,
      cursor: "pointer", boxShadow: "0 4px 18px rgba(124,58,237,.4)",
      transition: "opacity .2s",
    },
    btnDisabled: {
      marginTop: "0.85rem", width: "100%", padding: "0.85rem",
      background: "rgba(139,92,246,.35)",
      border: "none", borderRadius: "11px",
      color: "#fff", fontSize: "0.98rem", fontWeight: 700,
      cursor: "not-allowed",
    },
    error: {
      marginTop: "1.25rem",
      background: "rgba(239,68,68,.12)",
      border: "1px solid rgba(239,68,68,.3)",
      borderRadius: "12px", padding: "0.9rem 1.1rem",
      color: "#fca5a5", fontSize: "0.88rem",
    },
    toggleBtn: (color) => ({
      background: `rgba(${color},.1)`,
      border: `1px solid rgba(${color},.3)`,
      borderRadius: "999px", padding: "0.35rem 0.9rem",
      fontSize: "0.78rem", color: `rgba(${color},1)`, cursor: "pointer",
    }),
    planBox: {
      background: "rgba(96,165,250,.07)",
      border: "1px solid rgba(96,165,250,.2)",
      borderRadius: "12px", padding: "1.1rem 1.3rem",
      marginBottom: "1rem", fontSize: "0.85rem",
      color: "rgba(255,255,255,.8)", lineHeight: 1.7, whiteSpace: "pre-wrap",
    },
    codeBox: {
      background: "rgba(0,0,0,.55)",
      border: "1px solid rgba(52,211,153,.2)",
      borderRadius: "12px", padding: "1.1rem 1.3rem",
      marginBottom: "1rem", fontSize: "0.75rem",
      color: "#6ee7b7", overflow: "auto", maxHeight: "300px",
      fontFamily: "'Fira Code',monospace", whiteSpace: "pre-wrap",
    },
    liveDot: {
      width: "8px", height: "8px", borderRadius: "50%",
      background: "#34d399", display: "inline-block",
      animation: "pulse 2s infinite",
    },
    liveLabel: {
      fontSize: "0.78rem", color: "rgba(255,255,255,.4)",
      textTransform: "uppercase", letterSpacing: "0.08em",
    },
  };

  return (
    <div style={S.page}>
      
      <header style={S.header}>
        <div style={S.badge}>⚡ Groq · LLaMA 3.1 8B</div>
        <h1 style={S.h1}>AI UI Generator</h1>
        <p style={S.sub}>
          Describe any topic — get a live interactive UI instantly
        </p>
      </header>

      
      <main style={{ maxWidth: "820px", margin: "0 auto", padding: "0 1.25rem" }}>
        <div style={S.card}>
          <p style={S.chipLabel}>Try an example</p>
          <div style={S.chipRow}>
            {EXAMPLES.map(ex => (
              <button key={ex} onClick={() => setPrompt(ex)} style={S.chip}>
                {ex}
              </button>
            ))}
          </div>

          <textarea
            rows={4}
            value={prompt}
            onChange={e => setPrompt(e.target.value)}
            onKeyDown={e => {
              if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) generate();
            }}
            placeholder="e.g. Show all Indian states with capital, population and key facts…"
            style={S.textarea}
          />

          <button
            onClick={generate}
            disabled={loading || !prompt.trim()}
            style={loading || !prompt.trim() ? S.btnDisabled : S.btn}
          >
            {loading ? `✨ Generating${dots}` : "✨ Generate UI"}
          </button>
        </div>

        
        {error && <div style={S.error}>⚠️ {error}</div>}

        
        {generatedCode && (
          <div ref={resultRef} style={{ marginTop: "2.5rem" }}>
            
            <div style={{ display:"flex", gap:"0.6rem", flexWrap:"wrap", marginBottom:"1.25rem" }}>
              {instruction && (
                <button
                  onClick={() => setShowPlan(v => !v)}
                  style={S.toggleBtn("96,165,250")}
                >
                  {showPlan ? "▼" : "▶"} Planner instruction
                </button>
              )}
              <button
                onClick={() => setShowCode(v => !v)}
                style={S.toggleBtn("52,211,153")}
              >
                {showCode ? "▼" : "▶"} Generated code
              </button>
            </div>

            {showPlan && instruction && (
              <div style={S.planBox}>{instruction}</div>
            )}
            {showCode && (
              <div style={S.codeBox}>{generatedCode}</div>
            )}

            
            <div style={{ display:"flex", alignItems:"center", gap:"0.5rem", marginBottom:"0.7rem" }}>
              <span style={S.liveDot} />
              <span style={S.liveLabel}>Live preview</span>
            </div>

            <DynamicRenderer code={generatedCode} />
          </div>
        )}
      </main>

      <style>{`
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.25} }
        textarea::placeholder { color:rgba(255,255,255,.22); }
        ::-webkit-scrollbar { width:5px; height:5px; }
        ::-webkit-scrollbar-thumb { background:rgba(139,92,246,.45); border-radius:3px; }
      `}</style>
    </div>
  );
}
*/}

import { useState, useRef, useEffect } from "react";
import API from "./api";
import DynamicRenderer from "./DynamicRenderer";

const EXAMPLES = [
  "Show me a map of India with all states — hover to see state name, click for details",
  "Explain the human digestive system with an interactive diagram",
  "Show all Indian states with capital, population, area and language",
  "Interactive Solar System — all 8 planets with facts",
  "Periodic table — first 20 elements, clickable with details",
  "Human heart diagram — label each chamber, hover to highlight",
  "World War II timeline — key events 1939–1945",
  "3D Shape calculator: volume and surface area with live inputs",
];

export default function App() {
  const [prompt,        setPrompt]        = useState("");
  const [instruction,   setInstruction]   = useState("");
  const [generatedCode, setGeneratedCode] = useState("");
  const [loading,       setLoading]       = useState(false);
  const [error,         setError]         = useState("");
  const [showPlan,      setShowPlan]      = useState(false);
  const [showCode,      setShowCode]      = useState(false);
  const [dots,          setDots]          = useState("");
  const resultRef = useRef(null);

  // Animated loading dots
  useEffect(() => {
    if (!loading) { setDots(""); return; }
    const id = setInterval(
      () => setDots((d) => (d.length >= 3 ? "" : d + ".")),
      450
    );
    return () => clearInterval(id);
  }, [loading]);

  const generate = async () => {
    if (!prompt.trim() || loading) return;
    setLoading(true);
    setError("");
    setGeneratedCode("");
    setInstruction("");

    try {
      const { data } = await API.post("/generate-ui", { prompt });
      if (data.error) {
        setError(data.error);
      } else {
        setInstruction(data.planner_instruction || "");
        setGeneratedCode(data.generated_code || "");
        setTimeout(
          () => resultRef.current?.scrollIntoView({ behavior: "smooth" }),
          200
        );
      }
    } catch (e) {
      console.error(e);
      if (e.code === "ECONNABORTED") {
        setError(
          "Request timed out. The backend on Render free tier sleeps after " +
          "inactivity — wait 30 seconds for it to wake up, then try again."
        );
      } else {
        setError(`Could not reach backend: ${e.message}`);
      }
    }
    setLoading(false);
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "linear-gradient(135deg,#0f0c29 0%,#302b63 55%,#24243e 100%)",
        fontFamily: "'Segoe UI',system-ui,sans-serif",
        color: "#fff",
        paddingBottom: "5rem",
      }}
    >
      {/* ── HEADER ── */}
      <header style={{ textAlign: "center", padding: "3rem 1.5rem 0" }}>
        <div
          style={{
            display: "inline-block", marginBottom: "1rem",
            background: "rgba(139,92,246,.15)",
            border: "1px solid rgba(139,92,246,.4)",
            borderRadius: "999px", padding: "0.3rem 1rem",
            fontSize: "0.72rem", color: "#c4b5fd",
            letterSpacing: "0.08em", textTransform: "uppercase",
          }}
        >
          ⚡ Groq · LLaMA 3.1 8B · SVG-powered
        </div>
        <h1
          style={{
            fontSize: "clamp(1.9rem,5vw,3rem)", fontWeight: 900,
            margin: "0 0 0.5rem",
            background: "linear-gradient(90deg,#a78bfa,#60a5fa,#34d399)",
            WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
          }}
        >
          AI UI Generator
        </h1>
        <p
          style={{
            color: "rgba(255,255,255,.5)", fontSize: "1rem",
            maxWidth: "480px", margin: "0 auto 2.5rem",
          }}
        >
          Describe any topic — get a live interactive UI: maps, diagrams, cards, calculators
        </p>
      </header>

      {/* ── INPUT CARD ── */}
      <main style={{ maxWidth: "840px", margin: "0 auto", padding: "0 1.25rem" }}>
        <div
          style={{
            background: "rgba(255,255,255,.07)",
            border: "1px solid rgba(255,255,255,.12)",
            borderRadius: "20px", padding: "1.75rem",
            backdropFilter: "blur(10px)",
          }}
        >
          {/* Example chips */}
          <p
            style={{
              fontSize: "0.7rem", color: "rgba(255,255,255,.35)",
              textTransform: "uppercase", letterSpacing: "0.08em",
              marginBottom: "0.5rem",
            }}
          >
            Try an example
          </p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", marginBottom: "1.2rem" }}>
            {EXAMPLES.map((ex) => (
              <button
                key={ex}
                onClick={() => setPrompt(ex)}
                style={{
                  background: "rgba(139,92,246,.12)",
                  border: "1px solid rgba(139,92,246,.3)",
                  borderRadius: "999px", padding: "0.25rem 0.75rem",
                  fontSize: "0.72rem", color: "#c4b5fd",
                  cursor: "pointer", whiteSpace: "nowrap",
                }}
              >
                {ex}
              </button>
            ))}
          </div>

          {/* Textarea */}
          <textarea
            rows={4}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) generate();
            }}
            placeholder="e.g. Show me a map of India with all states, hover to see state name…"
            style={{
              width: "100%", background: "rgba(0,0,0,.35)",
              border: "1px solid rgba(255,255,255,.15)",
              borderRadius: "12px", padding: "0.9rem 1.1rem",
              fontSize: "0.95rem", color: "#fff",
              resize: "vertical", outline: "none",
              fontFamily: "inherit", lineHeight: 1.6, boxSizing: "border-box",
            }}
          />

          {/* Generate button */}
          <button
            onClick={generate}
            disabled={loading || !prompt.trim()}
            style={{
              marginTop: "0.85rem", width: "100%", padding: "0.85rem",
              background:
                loading || !prompt.trim()
                  ? "rgba(139,92,246,.35)"
                  : "linear-gradient(135deg,#7c3aed,#4f46e5)",
              border: "none", borderRadius: "11px",
              color: "#fff", fontSize: "0.98rem", fontWeight: 700,
              cursor: loading || !prompt.trim() ? "not-allowed" : "pointer",
              boxShadow: loading ? "none" : "0 4px 18px rgba(124,58,237,.4)",
              transition: "all 0.2s",
            }}
          >
            {loading ? `✨ Generating${dots}` : "✨ Generate UI"}
          </button>
        </div>

        {/* Error */}
        {error && (
          <div
            style={{
              marginTop: "1.25rem",
              background: "rgba(239,68,68,.12)",
              border: "1px solid rgba(239,68,68,.3)",
              borderRadius: "12px", padding: "0.9rem 1.1rem",
              color: "#fca5a5", fontSize: "0.88rem", lineHeight: 1.6,
            }}
          >
            ⚠️ {error}
          </div>
        )}

        {/* Results */}
        {generatedCode && (
          <div ref={resultRef} style={{ marginTop: "2.5rem" }}>
            {/* Toggle buttons */}
            <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap", marginBottom: "1.25rem" }}>
              {instruction && (
                <button
                  onClick={() => setShowPlan((v) => !v)}
                  style={{
                    background: "rgba(96,165,250,.1)",
                    border: "1px solid rgba(96,165,250,.3)",
                    borderRadius: "999px", padding: "0.35rem 0.9rem",
                    fontSize: "0.78rem", color: "#93c5fd", cursor: "pointer",
                  }}
                >
                  {showPlan ? "▼" : "▶"} Planner instruction
                </button>
              )}
              <button
                onClick={() => setShowCode((v) => !v)}
                style={{
                  background: "rgba(52,211,153,.08)",
                  border: "1px solid rgba(52,211,153,.3)",
                  borderRadius: "999px", padding: "0.35rem 0.9rem",
                  fontSize: "0.78rem", color: "#6ee7b7", cursor: "pointer",
                }}
              >
                {showCode ? "▼" : "▶"} Generated code
              </button>
            </div>

            {showPlan && instruction && (
              <div
                style={{
                  background: "rgba(96,165,250,.07)",
                  border: "1px solid rgba(96,165,250,.2)",
                  borderRadius: "12px", padding: "1.1rem 1.3rem",
                  marginBottom: "1rem", fontSize: "0.85rem",
                  color: "rgba(255,255,255,.8)", lineHeight: 1.7, whiteSpace: "pre-wrap",
                }}
              >
                {instruction}
              </div>
            )}

            {showCode && (
              <div
                style={{
                  background: "rgba(0,0,0,.55)",
                  border: "1px solid rgba(52,211,153,.2)",
                  borderRadius: "12px", padding: "1.1rem 1.3rem",
                  marginBottom: "1rem", fontSize: "0.75rem",
                  color: "#6ee7b7", overflow: "auto", maxHeight: "300px",
                  fontFamily: "'Fira Code',monospace", whiteSpace: "pre-wrap",
                }}
              >
                {generatedCode}
              </div>
            )}

            {/* Live preview */}
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.7rem" }}>
              <span
                style={{
                  width: "8px", height: "8px", borderRadius: "50%",
                  background: "#34d399", display: "inline-block",
                  animation: "pulse 2s infinite",
                }}
              />
              <span
                style={{
                  fontSize: "0.78rem", color: "rgba(255,255,255,.4)",
                  textTransform: "uppercase", letterSpacing: "0.08em",
                }}
              >
                Live preview
              </span>
            </div>

            <DynamicRenderer code={generatedCode} />
          </div>
        )}
      </main>

      <style>{`
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.25} }
        textarea::placeholder { color:rgba(255,255,255,.22); }
        ::-webkit-scrollbar { width:5px; height:5px; }
        ::-webkit-scrollbar-thumb { background:rgba(139,92,246,.45); border-radius:3px; }
      `}</style>
    </div>
  );
}
