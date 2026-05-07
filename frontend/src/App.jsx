{/*
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
  */}

// frontend/src/App.jsx

import React, {
  useState
} from "react";

import API from "./api";

import DynamicRenderer from "./DynamicRenderer";

export default function App() {

  const [prompt, setPrompt] = useState("");

  const [instruction, setInstruction] = useState("");

  const [generatedCode, setGeneratedCode] = useState("");

  const [loading, setLoading] = useState(false);

  const generateUI = async () => {

    console.log("BUTTON CLICKED");

    if (!prompt.trim()) {
      alert("Please enter a prompt");
      return;
    }

    setLoading(true);

    try {

      console.log("Sending request...");

      const response = await API.post(
        "/generate-ui",
        {
          prompt
        }
      );

      console.log("FULL RESPONSE:", response.data);

      if (response.data.error) {

        alert(response.data.error);

      } else {

        setInstruction(
          response.data.planner_instruction || ""
        );

        setGeneratedCode(
          response.data.generated_code || ""
        );
      }

    } catch (error) {

      console.error("FRONTEND ERROR:", error);

      if (error.response) {

        alert(
          JSON.stringify(
            error.response.data,
            null,
            2
          )
        );

      } else {

        alert(error.message);
      }
    }

    setLoading(false);
  };

  return (

    <div className="min-h-screen bg-gray-100 p-8">

      <div className="max-w-7xl mx-auto">

        <h1 className="text-5xl font-bold mb-8 text-center">

          AI UI Generator

        </h1>

        <div className="bg-white rounded-2xl shadow-xl p-6">

          <textarea
            className="w-full border border-gray-300 rounded-xl p-4 h-40 text-lg"
            placeholder="Enter your UI idea..."
            value={prompt}
            onChange={(e) =>
              setPrompt(e.target.value)
            }
          />

          <button
            onClick={generateUI}
            className="mt-5 bg-black text-white px-8 py-4 rounded-xl text-lg hover:opacity-90 transition"
          >

            {
              loading
                ? "Generating..."
                : "Generate UI"
            }

          </button>

        </div>

        {
          instruction && (
            <div className="bg-white rounded-2xl shadow-xl p-6 mt-10">

              <h2 className="text-3xl font-bold mb-5">

                Planner Instruction

              </h2>

              <pre className="whitespace-pre-wrap text-sm overflow-auto">
                {instruction}
              </pre>

            </div>
          )
        }

        {
          generatedCode && (
            <div className="bg-white rounded-2xl shadow-xl p-6 mt-10">

              <h2 className="text-3xl font-bold mb-5">

                Generated React Code

              </h2>

              <pre className="whitespace-pre-wrap text-sm overflow-auto">
                {generatedCode}
              </pre>

            </div>
          )
        }

        <DynamicRenderer code={generatedCode} />

      </div>

    </div>
  );
}
