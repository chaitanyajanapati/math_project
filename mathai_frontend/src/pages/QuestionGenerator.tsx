import { useState } from "react";
import axios from "axios";
import { API_ENDPOINTS } from "../config";
import { Sparkles, Lightbulb, CheckCircle, BookOpen, Settings2, Target } from "lucide-react";

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
  const [generating, setGenerating] = useState<boolean>(false);
  const [loadingHint, setLoadingHint] = useState<boolean>(false);
  const [loadingSolution, setLoadingSolution] = useState<boolean>(false);

  const handleGenerate = async () => {
    setGenerating(true);
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
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
      <h1 className="text-3xl font-bold mb-6 text-blue-700 text-center flex items-center justify-center gap-2">
        <Target className="w-8 h-8" />
        Math AI Question Generator
      </h1>

  <div className="grid grid-cols-4 grid-rows-2 gap-8 w-full max-w-6xl mx-auto">
  {/* Top-left: Controls */}
  <div className="bg-white border-2 border-indigo-300 shadow-lg rounded-xl p-6 col-span-1 row-span-1 min-h-[220px] flex flex-col">
    <h2 className="text-lg font-semibold text-indigo-700 mb-3 flex items-center gap-2">
      <Settings2 className="w-5 h-5" />
      Options
    </h2>
          <label className="block mb-2 font-medium text-gray-700">Grade:</label>
          <input
            type="number"
            min="1"
            max="12"
            value={grade}
            onChange={(e) => setGrade(Number(e.target.value))}
            className="border-2 border-indigo-200 p-2 w-full rounded-md mb-4 focus:border-indigo-500 focus:outline-none"
          />

          <label className="block mb-2 font-medium text-gray-700">Difficulty:</label>
          <select
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
            className="border-2 border-indigo-200 p-2 w-full rounded-md mb-4 focus:border-indigo-500 focus:outline-none"
          >
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>

          <label className="block mb-2 font-medium text-gray-700">Topic:</label>
          <select
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            className="border-2 border-indigo-200 p-2 w-full rounded-md mb-4 focus:border-indigo-500 focus:outline-none"
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
  <div className="bg-white border-2 border-yellow-300 shadow-lg rounded-xl p-6 flex flex-col col-span-3 row-span-1 min-h-[220px]">
          <h2 className="font-semibold text-yellow-700 mb-2 flex items-center gap-2">
            <BookOpen className="w-5 h-5" />
            Question
          </h2>
          <div className="mt-3 flex items-center space-x-4">
            <button
              onClick={handleGenerate}
              disabled={generating}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition shadow-md flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Sparkles className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
              {generating ? "Generating..." : "Generate Question"}
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
            <div className="min-h-[120px] p-4 bg-yellow-50 rounded-md border-2 border-yellow-300">
              {question ? (
                <p className="text-gray-800 text-lg">{question}</p>
              ) : (
                <p className="text-gray-400">No question yet. Click "Generate Question" to begin.</p>
              )}
            </div>
          </div>
        </div>

  {/* Bottom-left: Hint */}
  <div className="bg-white border-2 border-blue-300 shadow-lg rounded-xl p-6 col-span-1 row-span-1 min-h-[220px] flex flex-col">
          <h3 className="text-lg font-semibold text-blue-700 mb-2 flex items-center gap-2">
            <Lightbulb className="w-5 h-5" />
            Hint
          </h3>
          <div className="mt-3">
            <button
              onClick={async () => {
                if (!questionId) return;
                setLoadingHint(true);
                try {
                  const r = await axios.post(API_ENDPOINTS.HINT(questionId));
                  setHint(r.data.hint || "");
                } catch (e) {
                  console.error(e);
                  setHint("Could not fetch hint.");
                } finally {
                  setLoadingHint(false);
                }
              }}
              disabled={loadingHint || !questionId}
              className="px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md shadow-md flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Lightbulb className={`w-4 h-4 ${loadingHint ? 'animate-spin' : ''}`} />
              {loadingHint ? "Loading..." : "Get Hint"}
            </button>
          </div>

          <div className="mt-4 p-4 bg-blue-50 rounded-md min-h-[120px] flex-1 overflow-auto border-2 border-blue-200">
            {hint ? <p className="text-blue-900">{hint}</p> : <p className="text-gray-400">Hints will appear here.</p>}
          </div>
        </div>

  {/* Bottom-right: Solution Steps & Answer */}
  <div className="bg-white border-2 border-green-300 shadow-lg rounded-xl p-6 flex flex-col col-span-3 row-span-1 min-h-[220px]">
          <h3 className="text-lg font-semibold text-green-700 mb-2 flex items-center gap-2">
            <CheckCircle className="w-5 h-5" />
            Solution Steps & Answer
          </h3>
          <div className="mt-3">
            <button
              onClick={async () => {
                if (!questionId) return;
                setLoadingSolution(true);
                try {
                  const r = await axios.post(API_ENDPOINTS.SOLUTION(questionId));
                  setSolutionSteps(r.data.solution_steps || []);
                } catch (e) {
                  console.error(e);
                  setSolutionSteps(["Could not fetch solution."]);
                } finally {
                  setLoadingSolution(false);
                }
              }}
              disabled={loadingSolution || !questionId}
              className="px-3 py-2 bg-gray-800 hover:bg-gray-900 text-white rounded-md shadow-md flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <BookOpen className={`w-4 h-4 ${loadingSolution ? 'animate-spin' : ''}`} />
              {loadingSolution ? "Loading..." : "Get Solution"}
            </button>
          </div>

          <div className="mt-4 flex-1 overflow-auto space-y-4">
            {solutionSteps && solutionSteps.length > 0 ? (
              <ol className="list-decimal list-inside space-y-2 bg-green-50 p-3 rounded-md border-2 border-green-200">
                {solutionSteps.map((s, i) => (
                  <li key={i} className="text-gray-800">{s}</li>
                ))}
              </ol>
            ) : (
              <p className="text-gray-400">Solution steps will appear here.</p>
            )}
          </div>

          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Your Answer</label>
            <input
              type="text"
              value={studentAnswer}
              onChange={(e) => setStudentAnswer(e.target.value)}
              placeholder="Enter answer (e.g. 3/8 or 0.375)"
              className="border-2 border-gray-300 focus:border-green-500 p-2 w-full rounded-md mt-1 focus:outline-none"
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
                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md shadow-md disabled:opacity-50"
                disabled={!questionId || loading || !studentAnswer.trim()}
              >
                {loading ? "Checking..." : "Submit Answer"}
              </button>

              {feedback && (
                <div className="text-sm font-medium text-gray-700 mt-2 p-3 bg-blue-50 rounded-md border-2 border-blue-200">
                  {feedback}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
