import {
  LiveProvider,
  LivePreview,
  LiveError
} from "react-live";

export default function DynamicRenderer({ code }) {

  // Remove markdown if AI accidentally adds it

  const cleanedCode = code
    .replace(/```jsx/g, "")
    .replace(/```javascript/g, "")
    .replace(/```/g, "");

  return (

    <div className="mt-8">

      <h2 className="text-2xl font-bold mb-4">
        Live UI Preview
      </h2>

      <div className="border rounded-xl p-6 bg-white shadow">

        <LiveProvider code={cleanedCode} noInline>

          <LiveError className="text-red-500 mb-4" />

          <LivePreview />

        </LiveProvider>

      </div>

    </div>
  );
}
