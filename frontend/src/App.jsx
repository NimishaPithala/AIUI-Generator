import { useState, useRef, useEffect } from "react";
import API from "./api";
import DynamicRenderer from "./DynamicRenderer";

const EXAMPLES = [
  "Show me all Indian states with capitals and facts",
  "Explain the Solar System with planet details",
  "Show chemical equations for common reactions",
  "3D Shape calculator with volume and surface area",
  "Periodic table of elements - first 20 elements",
  "World War II timeline with key events",
];

export default function App() {
  const [prompt, setPrompt] = useState("");
  const [instruction, setInstruction] = useState("");
  const [generatedCode, setGeneratedCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [showInstruction, setShowInstruction] = useState(false);
  const [showCode, setShowCode] = useState(false);
  const [error, setError] = useState("");
  const [dots, setDots] = useState("");
  const resultRef = useRef(null);

  // Animated loading dots
  useEffect(() => {
    if (!loading) return;
    const interval = setInterval(() => {
      setDots((d) => (d.length >= 3 ? "" : d + "."));
    }, 400);
    return () => clearInterval(interval);
  }, [loading]);

  const generateUI = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setError("");
    setGeneratedCode("");
    setInstruction("");

    try {
      const response = await API.post("/generate-ui", { prompt });

      if (response.data.error) {
        setError(response.data.error);
      } else {
        setInstruction(response.data.planner_instruction);
        setGeneratedCode(response.data.generated_code);
        setTimeout(() => {
          resultRef.current?.scrollIntoView({ behavior: "smooth" });
        }, 100);
      }
    } catch (err) {
      console.error(err);
      setError("Failed to connect to the backend. Is it running?");
    }

    setLoading(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      generateUI();
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #0f0c29, #302b63, #24243e)",
        fontFamily: "'Segoe UI', system-ui, sans-serif",
        color: "#fff",
      }}
    >
      {/* ─── HEADER ─── */}
      <header
        style={{
          padding: "2rem 2rem 0",
          textAlign: "center",
          position: "relative",
        }}
      >
        {/* Glow orbs */}
        <div
          style={{
            position: "absolute",
            top: "-60px",
            left: "50%",
            transform: "translateX(-50%)",
            width: "600px",
            height: "300px",
            background: "radial-gradient(ellipse, rgba(139,92,246,0.25) 0%, transparent 70%)",
            pointerEvents: "none",
          }}
        />

        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "0.5rem",
            background: "rgba(139,92,246,0.15)",
            border: "1px solid rgba(139,92,246,0.4)",
            borderRadius: "999px",
            padding: "0.4rem 1rem",
            fontSize: "0.8rem",
            color: "#c4b5fd",
            marginBottom: "1.2rem",
            letterSpacing: "0.05em",
            textTransform: "uppercase",
          }}
        >
          <span style={{ fontSize: "0.6rem" }}>⚡</span>
          Powered by Groq LLaMA 3.3 70B
        </div>

        <h1
          style={{
            fontSize: "clamp(2rem, 5vw, 3.5rem)",
            fontWeight: 900,
            margin: "0 0 0.5rem",
            background: "linear-gradient(90deg, #a78bfa, #60a5fa, #34d399)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            letterSpacing: "-0.02em",
          }}
        >
          AI UI Generator
        </h1>

        <p
          style={{
            color: "rgba(255,255,255,0.55)",
            fontSize: "1.05rem",
            margin: "0 auto 2.5rem",
            maxWidth: "480px",
          }}
        >
          Describe anything — get a live, interactive UI instantly
        </p>
      </header>

      {/* ─── MAIN CARD ─── */}
      <main
        style={{
          maxWidth: "860px",
          margin: "0 auto",
          padding: "0 1.5rem 4rem",
        }}
      >
        <div
          style={{
            background: "rgba(255,255,255,0.06)",
            border: "1px solid rgba(255,255,255,0.12)",
            borderRadius: "20px",
            padding: "2rem",
            backdropFilter: "blur(12px)",
            boxShadow: "0 25px 60px rgba(0,0,0,0.4)",
          }}
        >
          {/* Examples */}
          <p
            style={{
              fontSize: "0.78rem",
              color: "rgba(255,255,255,0.4)",
              marginBottom: "0.6rem",
              textTransform: "uppercase",
              letterSpacing: "0.08em",
            }}
          >
            Try an example
          </p>
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: "0.5rem",
              marginBottom: "1.4rem",
            }}
          >
            {EXAMPLES.map((ex) => (
              <button
                key={ex}
                onClick={() => setPrompt(ex)}
                style={{
                  background: "rgba(139,92,246,0.12)",
                  border: "1px solid rgba(139,92,246,0.3)",
                  borderRadius: "999px",
                  padding: "0.3rem 0.85rem",
                  fontSize: "0.78rem",
                  color: "#c4b5fd",
                  cursor: "pointer",
                  transition: "all 0.15s",
                  whiteSpace: "nowrap",
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = "rgba(139,92,246,0.28)";
                  e.target.style.borderColor = "rgba(139,92,246,0.7)";
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = "rgba(139,92,246,0.12)";
                  e.target.style.borderColor = "rgba(139,92,246,0.3)";
                }}
              >
                {ex}
              </button>
            ))}
          </div>

          {/* Textarea */}
          <div style={{ position: "relative" }}>
            <textarea
              rows={4}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="e.g. Show me all Indian states with their capitals, population and interesting facts..."
              style={{
                width: "100%",
                background: "rgba(0,0,0,0.3)",
                border: "1px solid rgba(255,255,255,0.15)",
                borderRadius: "14px",
                padding: "1rem 1.2rem",
                fontSize: "0.97rem",
                color: "#fff",
                resize: "vertical",
                outline: "none",
                boxSizing: "border-box",
                fontFamily: "inherit",
                lineHeight: 1.6,
                transition: "border-color 0.2s",
              }}
              onFocus={(e) => {
                e.target.style.borderColor = "rgba(139,92,246,0.6)";
              }}
              onBlur={(e) => {
                e.target.style.borderColor = "rgba(255,255,255,0.15)";
              }}
            />
            <span
              style={{
                position: "absolute",
                bottom: "0.7rem",
                right: "1rem",
                fontSize: "0.7rem",
                color: "rgba(255,255,255,0.25)",
              }}
            >
              Ctrl+Enter to generate
            </span>
          </div>

          {/* Generate Button */}
          <button
            onClick={generateUI}
            disabled={loading || !prompt.trim()}
            style={{
              marginTop: "1rem",
              width: "100%",
              padding: "0.9rem",
              background: loading
                ? "rgba(139,92,246,0.4)"
                : "linear-gradient(135deg, #7c3aed, #4f46e5)",
              border: "none",
              borderRadius: "12px",
              color: "#fff",
              fontSize: "1rem",
              fontWeight: 700,
              cursor: loading ? "not-allowed" : "pointer",
              transition: "all 0.2s",
              letterSpacing: "0.02em",
              boxShadow: loading ? "none" : "0 4px 20px rgba(124,58,237,0.4)",
            }}
            onMouseEnter={(e) => {
              if (!loading) {
                e.target.style.transform = "translateY(-1px)";
                e.target.style.boxShadow = "0 8px 28px rgba(124,58,237,0.55)";
              }
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = "translateY(0)";
              e.target.style.boxShadow = "0 4px 20px rgba(124,58,237,0.4)";
            }}
          >
            {loading ? `✨ Generating${dots}` : "✨ Generate UI"}
          </button>
        </div>

        {/* ─── ERROR ─── */}
        {error && (
          <div
            style={{
              marginTop: "1.5rem",
              background: "rgba(239,68,68,0.1)",
              border: "1px solid rgba(239,68,68,0.3)",
              borderRadius: "12px",
              padding: "1rem 1.2rem",
              color: "#fca5a5",
              fontSize: "0.9rem",
            }}
          >
            ⚠️ {error}
          </div>
        )}

        {/* ─── RESULTS ─── */}
        {generatedCode && (
          <div ref={resultRef} style={{ marginTop: "2.5rem" }}>
            {/* Collapsibles row */}
            <div
              style={{
                display: "flex",
                gap: "0.75rem",
                marginBottom: "1.5rem",
                flexWrap: "wrap",
              }}
            >
              {instruction && (
                <button
                  onClick={() => setShowInstruction((v) => !v)}
                  style={{
                    background: "rgba(96,165,250,0.12)",
                    border: "1px solid rgba(96,165,250,0.3)",
                    borderRadius: "999px",
                    padding: "0.4rem 1rem",
                    fontSize: "0.82rem",
                    color: "#93c5fd",
                    cursor: "pointer",
                  }}
                >
                  {showInstruction ? "▼" : "▶"} Planner Instruction
                </button>
              )}
              <button
                onClick={() => setShowCode((v) => !v)}
                style={{
                  background: "rgba(52,211,153,0.1)",
                  border: "1px solid rgba(52,211,153,0.3)",
                  borderRadius: "999px",
                  padding: "0.4rem 1rem",
                  fontSize: "0.82rem",
                  color: "#6ee7b7",
                  cursor: "pointer",
                }}
              >
                {showCode ? "▼" : "▶"} Generated Code
              </button>
            </div>

            {showInstruction && instruction && (
              <div
                style={{
                  background: "rgba(96,165,250,0.07)",
                  border: "1px solid rgba(96,165,250,0.2)",
                  borderRadius: "14px",
                  padding: "1.2rem 1.5rem",
                  marginBottom: "1rem",
                  color: "rgba(255,255,255,0.8)",
                  fontSize: "0.88rem",
                  lineHeight: 1.7,
                  whiteSpace: "pre-wrap",
                }}
              >
                {instruction}
              </div>
            )}

            {showCode && (
              <div
                style={{
                  background: "rgba(0,0,0,0.5)",
                  border: "1px solid rgba(52,211,153,0.2)",
                  borderRadius: "14px",
                  padding: "1.2rem 1.5rem",
                  marginBottom: "1rem",
                  color: "#6ee7b7",
                  fontSize: "0.8rem",
                  overflow: "auto",
                  maxHeight: "350px",
                  fontFamily: "'Fira Code', 'Cascadia Code', monospace",
                  lineHeight: 1.6,
                  whiteSpace: "pre-wrap",
                }}
              >
                {generatedCode}
              </div>
            )}

            {/* Live Preview */}
            <div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "0.6rem",
                  marginBottom: "0.8rem",
                }}
              >
                <span
                  style={{
                    width: "8px",
                    height: "8px",
                    borderRadius: "50%",
                    background: "#34d399",
                    display: "inline-block",
                    animation: "pulse 2s infinite",
                  }}
                />
                <span
                  style={{
                    fontSize: "0.85rem",
                    color: "rgba(255,255,255,0.5)",
                    textTransform: "uppercase",
                    letterSpacing: "0.08em",
                  }}
                >
                  Live Preview
                </span>
              </div>
              <DynamicRenderer code={generatedCode} />
            </div>
          </div>
        )}
      </main>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
        * { box-sizing: border-box; }
        textarea::placeholder { color: rgba(255,255,255,0.25); }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.4); border-radius: 3px; }
      `}</style>
    </div>
  );
}
