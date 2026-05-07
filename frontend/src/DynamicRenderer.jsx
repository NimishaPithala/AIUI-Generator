import React from "react";

import {
  LiveProvider,
  LivePreview,
  LiveError
} from "react-live";

export default function DynamicRenderer({
  code
}) {

  // ===================================
  // CLEAN AI GENERATED CODE
  // ===================================

  let cleanedCode = code;

  // Remove markdown

  cleanedCode = cleanedCode
    .replace(/```jsx/g, "")
    .replace(/```javascript/g, "")
    .replace(/```/g, "");

  // Remove imports

  cleanedCode = cleanedCode
    .replace(/import\s.*?from\s.*?;/g, "");

  // Remove export default

  cleanedCode = cleanedCode
    .replace(/export default/g, "");

  // Fix React hooks

  cleanedCode = cleanedCode
    .replace(/\buseState\(/g, "React.useState(");

  cleanedCode = cleanedCode
    .replace(/\buseEffect\(/g, "React.useEffect(");

  // Fix class → className

  cleanedCode = cleanedCode
    .replace(/class=/g, "className=");

  // ===================================
  // ENSURE render(<App />)
  // ===================================

  if (!cleanedCode.includes("render(")) {

    cleanedCode += "\nrender(<App />);";
  }

  console.log(cleanedCode);

  return (

    <div className="mt-8">

      <h2 className="text-2xl font-bold mb-4">

        Live UI Preview

      </h2>

      <div className="bg-white border rounded-xl p-6 shadow">

        <LiveProvider
          code={cleanedCode}
          noInline={true}
          scope={{ React }}
        >

          <LiveError
            className="text-red-500 whitespace-pre-wrap mb-4"
          />

          <LivePreview />

        </LiveProvider>

      </div>

    </div>
  );
}
