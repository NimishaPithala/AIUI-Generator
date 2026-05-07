// frontend/src/DynamicRenderer.jsx

import React, {
  useState,
  useEffect
} from "react";

import {
  LiveProvider,
  LivePreview,
  LiveError
} from "react-live";

export default function DynamicRenderer({ code }) {

  if (!code) return null;

  // =========================
  // CLEAN CODE
  // =========================

  let cleanedCode = code
    .replace(/```jsx/g, "")
    .replace(/```javascript/g, "")
    .replace(/```/g, "")
    .trim();

  // =========================
  // REMOVE EXPORT DEFAULT
  // =========================

  cleanedCode = cleanedCode.replace(
    /export\s+default\s+/,
    ""
  );

  // =========================
  // FIND COMPONENT NAME
  // =========================

  const match = cleanedCode.match(
    /function\s+([A-Za-z0-9_]+)/
  );

  const componentName = match
    ? match[1]
    : null;

  // =========================
  // VALIDATION
  // =========================

  const isValid =
    componentName &&
    cleanedCode.includes("return") &&
    cleanedCode.includes("{") &&
    cleanedCode.includes("}");

  if (!isValid) {

    return (
      <div className="bg-red-50 border border-red-300 rounded-xl p-6 mt-8">

        <h2 className="text-red-600 text-2xl font-bold mb-3">
          Invalid AI Generated Code
        </h2>

        <pre className="whitespace-pre-wrap text-sm overflow-auto">
          {cleanedCode}
        </pre>

      </div>
    );
  }

  // =========================
  // APPEND RENDER
  // =========================

  cleanedCode += `

render(<${componentName} />);
`;

  return (

    <div className="mt-10">

      <h2 className="text-3xl font-bold mb-5">
        Live UI Preview
      </h2>

      <div className="bg-white rounded-2xl shadow-2xl border p-6 overflow-auto min-h-[500px]">

        <LiveProvider
          code={cleanedCode}
          noInline
          scope={{
            React,
            useState,
            useEffect
          }}
        >

          <LiveError className="text-red-500 whitespace-pre-wrap mb-4 bg-red-50 p-4 rounded-xl" />

          <LivePreview />

        </LiveProvider>

      </div>

    </div>
  );
}
