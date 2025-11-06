import { useState } from "react";
import { API_ENDPOINTS } from "./config";

function App() {
  const [grade, setGrade] = useState(8);
  const [topic, setTopic] = useState("algebra");
  const [difficulty, setDifficulty] = useState("medium");
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  const generateQuestion = async () => {
    setLoading(true);
    setQuestion("");
    try {
  const response = await fetch(API_ENDPOINTS.GENERATE_QUESTION, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ grade, topic, difficulty }),
      });
      const data = await response.json();
      setQuestion(data.question || "No question received");
    } catch (error) {
      console.error(error);
      setQuestion("⚠️ Error connecting to backend");
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 via-blue-100 to-indigo-200 p-6">
      <div className="bg-white shadow-2xl rounded-3xl p-10 w-full max-w-2xl">
        <h1 className="text-4xl font-extrabold text-center text-indigo-700 mb-8">
          MathAI – Smart Question Generator
        </h1>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-8">
          <div>
            <label className="block text-gray-600 mb-1 font-semibold">
              Grade
            </label>
            <select
              className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-indigo-400"
              value={grade}
              onChange={(e) => setGrade(Number(e.target.value))}
            >
              {[6, 7, 8, 9, 10].map((g) => (
                <option key={g} value={g}>
                  {g}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-gray-600 mb-1 font-semibold">
              Topic
            </label>
            <select
              className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-indigo-400"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
            >
              <option value="algebra">Algebra</option>
              <option value="geometry">Geometry</option>
              <option value="arithmetic">Arithmetic</option>
              <option value="mensuration">Mensuration</option>
              <option value="trigonometry">Trigonometry</option>
            </select>
          </div>

          <div>
            <label className="block text-gray-600 mb-1 font-semibold">
              Difficulty
            </label>
            <select
              className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-indigo-400"
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
        </div>

        <div className="flex justify-center mb-6">
          <button
            onClick={generateQuestion}
            className="px-8 py-3 bg-indigo-600 text-white text-lg font-semibold rounded-xl shadow hover:bg-indigo-700 transition-transform transform hover:scale-105"
            disabled={loading}
          >
            {loading ? "Generating..." : "Generate Question"}
          </button>
        </div>

        {question && (
          <div className="mt-4 bg-indigo-50 border-l-4 border-indigo-600 text-gray-800 p-6 rounded-xl shadow-inner">
            <h2 className="text-xl font-semibold mb-2 text-indigo-700">
              Generated Question:
            </h2>
            <p className="text-lg">{question}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
