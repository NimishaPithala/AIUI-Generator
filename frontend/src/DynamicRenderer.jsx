

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

  // =====================================
  // CLEAN AI CODE
  // =====================================

  let cleanedCode = code
    .replace(/```jsx/g, "")
    .replace(/```javascript/g, "")
    .replace(/```/g, "")
    .trim();

  // =====================================
  // REMOVE export default
  // =====================================

  cleanedCode = cleanedCode.replace(
    /export\s+default\s+/,
    ""
  );

  // =====================================
  // FIND COMPONENT NAME
  // =====================================

  const match = cleanedCode.match(
    /function\s+([A-Za-z0-9_]+)/
  );

  const componentName = match
    ? match[1]
    : "GeneratedComponent";

  // =====================================
  // APPEND render()
  // =====================================

  cleanedCode += `

render(<${componentName} />);
`;

  return (

    <div className="mt-8">

      <h2 className="text-2xl font-bold mb-4">

        Live UI Preview

      </h2>

      <div className="bg-white border rounded-xl p-6 shadow overflow-auto">

        <LiveProvider
          code={cleanedCode}
          noInline={true}
          scope={{
            React,
            useState,
            useEffect
          }}
        >

          <LiveError className="text-red-500 mb-4 whitespace-pre-wrap" />

          <LivePreview />

        </LiveProvider>

      </div>

    </div>
  );
}
