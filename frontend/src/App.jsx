import { useState } from "react";
import API from "./api";

export default function App() {

  const [prompt, setPrompt] = useState("");

  const [instruction, setInstruction] =
    useState("");

  const [generatedCode, setGeneratedCode] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const generateUI = async () => {

    setLoading(true);

    try {

      const response = await API.post(
        "/generate-ui",
        {
          prompt
        }
      );

      setInstruction(
        response.data.planner_instruction
      );

      setGeneratedCode(
        response.data.generated_code
      );

    } catch (error) {

      console.error(error);

    }

    setLoading(false);
  };

  return (

    <div className="min-h-screen bg-gray-100 p-10">

      <div className="max-w-6xl mx-auto">

        <h1 className="text-5xl font-bold mb-8">
          AI UI Generator
        </h1>

        <textarea
          className="w-full border rounded-xl p-5"
          rows={6}
          placeholder="Enter your prompt..."
          value={prompt}
          onChange={(e) =>
            setPrompt(e.target.value)
          }
        />

        <button
          onClick={generateUI}
          className="bg-black text-white px-8 py-4 rounded-xl mt-5"
        >
          {
            loading
            ? "Generating..."
            : "Generate UI"
          }
        </button>

        {/* Planner Output */}

        {
          instruction && (

            <div className="bg-white p-6 rounded-xl shadow mt-8">

              <h2 className="text-2xl font-bold mb-4">
                Planner Instruction
              </h2>

              <p className="whitespace-pre-wrap">
                {instruction}
              </p>

            </div>
          )
        }

        {/* Generated Code */}

        {
          generatedCode && (

            <div className="bg-black text-green-400 p-6 rounded-xl mt-8 overflow-auto">

              <h2 className="text-white text-2xl font-bold mb-4">
                Generated React Code
              </h2>

              <pre>
                {generatedCode}
              </pre>

            </div>
          )
        }

      </div>

    </div>
  );
}