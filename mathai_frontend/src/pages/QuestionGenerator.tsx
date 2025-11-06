import { useState } from "react";
import axios from "axios";
import { API_ENDPOINTS } from "../config";

export default function QuestionGenerator() {
  const [grade, setGrade] = useState<number>(8);
  const [difficulty, setDifficulty] = useState<string>("medium");
  const [topic, setTopic] = useState<string>("algebra");
  const [question, setQuestion] = useState<string>("");
  const [questionId, setQuestionId] = useState<string>("");
  const [hint, setHint] = useState<string>("");
  const [solutionSteps, setSolutionSteps] = useState<string[]>([]);
  const [studentAnswer, setStudentAnswer] = useState<string>("");
  const [attemptNumber, setAttemptNumber] = useState<number>(1);
  const [feedback, setFeedback] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  const handleGenerate = async () => {
    try {
      const res = await axios.post(API_ENDPOINTS.GENERATE_QUESTION, {
        grade,
        difficulty,
        topic,
      });
      setQuestion(res.data.question);
      setQuestionId(res.data.id || "");
      setHint("");
      setSolutionSteps([]);
    } catch (err) {
      setQuestion("Error connecting to backend. Make sure FastAPI is running.");
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-3xl font-bold mb-6 text-blue-600 text-center">🎯 Math AI Question Generator</h1>

  <div className="grid grid-cols-4 grid-rows-2 gap-8 w-full max-w-6xl mx-auto">
  {/* Top-left: Controls */}
  <div className="bg-indigo-50 border border-indigo-200 shadow-md rounded-xl p-6 col-span-1 row-span-1 min-h-[220px] flex flex-col">
    <h2 className="text-lg font-semibold">Options</h2>
          <label className="block mb-2 font-medium">Grade:</label>
          <input
            type="number"
            min="1"
            max="12"
            value={grade}
            onChange={(e) => setGrade(Number(e.target.value))}
            className="border p-2 w-full rounded-md mb-4"
          />

          <label className="block mb-2 font-medium">Difficulty:</label>
          <select
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
            className="border p-2 w-full rounded-md mb-4"
          >
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>

          <label className="block mb-2 font-medium">Topic:</label>
          <select
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            className="border p-2 w-full rounded-md mb-4"
          >
            <option value="algebra">Algebra</option>
            <option value="geometry">Geometry</option>
            <option value="arithmetic">Arithmetic</option>
            <option value="mensuration">Mensuration</option>
            <option value="trigonometry">Trigonometry</option>
          </select>
          {/* Generate button moved to Question panel per layout spec */}
        </div>

  {/* Top-right: Generate + Question */}
  <div className="bg-yellow-50 border border-yellow-200 shadow-md rounded-xl p-6 flex flex-col col-span-3 row-span-1 min-h-[220px]">
          <h2 className="font-semibold text-gray-800">Question</h2>
          <div className="mt-3 flex items-center space-x-4">
            <button
              onClick={handleGenerate}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition"
            >
              Generate Question
            </button>
            {questionId && (
              <div className="text-sm text-gray-500 flex items-center space-x-2">
                <div>ID: <code className="bg-gray-100 px-2 py-1 rounded">{questionId}</code></div>
                <button
                  onClick={() => {
                    navigator.clipboard?.writeText(questionId);
                  }}
                  className="text-xs px-2 py-1 bg-gray-200 rounded"
                  title="Copy question ID"
                >
                  Copy
                </button>
              </div>
            )}
          </div>

          <div className="mt-4 overflow-auto flex-1">
            <div className="min-h-[120px] p-4 bg-yellow-50 rounded-md border border-yellow-200">
              {question ? (
                <p className="text-gray-700">{question}</p>
              ) : (
                <p className="text-gray-400">No question yet. Click "Generate Question" to begin.</p>
              )}
            </div>
          </div>
        </div>

  {/* Bottom-left: Hint */}
  <div className="bg-blue-50 border border-blue-200 shadow-md rounded-xl p-6 col-span-1 row-span-1 min-h-[220px] flex flex-col">
          <h3 className="text-lg font-semibold">Hint</h3>
          <div className="mt-3">
            <button
              onClick={async () => {
                if (!questionId) return;
                try {
                  const r = await axios.post(API_ENDPOINTS.HINT(questionId));
                  setHint(r.data.hint || "");
                } catch (e) {
                  console.error(e);
                  setHint("Could not fetch hint.");
                }
              }}
              className="px-3 py-1 bg-indigo-600 text-white rounded-md"
            >
              Get Hint
            </button>
          </div>

          <div className="mt-4 p-4 bg-blue-50 rounded-md min-h-[120px] flex-1 overflow-auto">
            {hint ? <p className="text-blue-800">{hint}</p> : <p className="text-gray-400">Hints will appear here.</p>}
          </div>
        </div>

  {/* Bottom-right: Solution Steps & Answer */}
  <div className="bg-green-50 border border-green-200 shadow-md rounded-xl p-6 flex flex-col col-span-3 row-span-1 min-h-[220px]">
          <h3 className="text-lg font-semibold">Solution Steps & Answer</h3>
          <div className="mt-3">
            <button
              onClick={async () => {
                if (!questionId) return;
                try {
                  const r = await axios.post(API_ENDPOINTS.SOLUTION(questionId));
                  setSolutionSteps(r.data.solution_steps || []);
                } catch (e) {
                  console.error(e);
                  setSolutionSteps(["Could not fetch solution."]);
                }
              }}
              className="px-3 py-1 bg-gray-800 text-white rounded-md"
            >
              Get Solution
            </button>
          </div>

          <div className="mt-4 flex-1 overflow-auto space-y-4">
            {solutionSteps && solutionSteps.length > 0 ? (
              <ol className="list-decimal list-inside space-y-2">
                {solutionSteps.map((s, i) => (
                  <li key={i} className="text-gray-700">{s}</li>
                ))}
              </ol>
            ) : (
              <p className="text-gray-400">Solution steps will appear here.</p>
            )}
          </div>

          <div className="mt-4">
            <label className="block text-sm font-medium">Your Answer</label>
            <input
              type="text"
              value={studentAnswer}
              onChange={(e) => setStudentAnswer(e.target.value)}
              placeholder="Enter answer (e.g. 3/8 or 0.375)"
              className="border p-2 w-full rounded-md mt-1"
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  // trigger submit button click
                  const btn = document.querySelector('#submit-answer-btn') as HTMLButtonElement | null;
                  if (btn && !btn.disabled) btn.click();
                }
              }}
            />

            <div className="mt-3">
              <button
                onClick={async () => {
                  if (!questionId) return;
                  setLoading(true);
                  try {
                    const r = await axios.post(API_ENDPOINTS.SUBMIT_ANSWER, {
                      question_id: questionId,
                      student_answer: studentAnswer,
                      attempt_number: attemptNumber,
                    });
                    const data = r.data;
                    setFeedback(data.feedback || "");
                    if (data.is_correct) {
                      setSolutionSteps(data.solution_steps || []);
                    } else {
                      if (data.hint) setHint(data.hint);
                      setAttemptNumber((a) => a + 1);
                    }
                  } catch (e) {
                    console.error(e);
                    setFeedback("Could not submit answer. Check the backend.");
                  } finally {
                    setLoading(false);
                  }
                }}
                id="submit-answer-btn"
                className="px-4 py-2 bg-green-600 text-white rounded-md"
                disabled={!questionId || loading || !studentAnswer.trim()}
              >
                {loading ? "Checking..." : "Submit Answer"}
              </button>

              <div className="text-sm text-gray-600 mt-2">{feedback}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
