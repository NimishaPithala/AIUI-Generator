import React from "react";

import {
  LiveProvider,
  LivePreview,
  LiveError
} from "react-live";

export default function DynamicRenderer({
  code
}) {

  // Clean markdown

  const cleanedCode = code
    .replace(/```jsx/g, "")
    .replace(/```javascript/g, "")
    .replace(/```/g, "");

  return (

    <div className="mt-8">

      <h2 className="text-2xl font-bold mb-4">

        Live UI Preview

      </h2>

      <div className="bg-white p-6 rounded-xl shadow border">

        <LiveProvider
          code={cleanedCode}
          noInline={true}
          scope={{ React }}
        >

          <LiveError
            className="text-red-500 mb-4"
          />

          <LivePreview />

        </LiveProvider>

      </div>

    </div>
  );
}
