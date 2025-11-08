import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { API_ENDPOINTS } from "../config";
import { Sparkles, Lightbulb, CheckCircle, BookOpen, Settings2, Target } from "lucide-react";

export default function QuestionGenerator() {
  const [grade, setGrade] = useState<number>(8);
  const [difficulty, setDifficulty] = useState<string>("medium");
  const [topic, setTopic] = useState<string>("algebra");
  const [questionType, setQuestionType] = useState<string>("open");
  const [question, setQuestion] = useState<string>("");
  const [questionId, setQuestionId] = useState<string>("");
  const [hint, setHint] = useState<string>("");
  const [solutionSteps, setSolutionSteps] = useState<string[]>([]);
  const [studentAnswer, setStudentAnswer] = useState<string>("");
  const [choices, setChoices] = useState<string[] | null>(null);
  const [selectedChoice, setSelectedChoice] = useState<string>("");
  const [attemptNumber, setAttemptNumber] = useState<number>(1);
  const [feedback, setFeedback] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [generating, setGenerating] = useState<boolean>(false);
  const [loadingHint, setLoadingHint] = useState<boolean>(false);
  const [loadingSolution, setLoadingSolution] = useState<boolean>(false);

  // Abort controller ref to cancel stale generate requests when user switches topic rapidly
  const abortRef = useRef<AbortController | null>(null);

  const handleGenerate = async () => {
    // Cancel any previous in-flight request
    if (abortRef.current) {
      abortRef.current.abort();
    }
    const controller = new AbortController();
    abortRef.current = controller;

    setGenerating(true);
    try {
      const res = await axios.post(
        API_ENDPOINTS.GENERATE_QUESTION,
        {
          grade,
          difficulty,
          topic,
          question_type: questionType,
        },
        { signal: controller.signal }
      );
      setQuestion(res.data.question);
      setQuestionId(res.data.id || "");
      setChoices(Array.isArray(res.data.choices) ? res.data.choices : null);
      setSelectedChoice("");
      setHint("");
      setSolutionSteps([]);
      setFeedback("");
      setStudentAnswer("");
      setAttemptNumber(1);
    } catch (err: unknown) {
      if (axios.isCancel(err) || (err instanceof Error && err.name === 'CanceledError')) {
        // Silently ignore canceled requests
        return;
      }
      setQuestion("Error connecting to backend. Make sure FastAPI is running.");
      console.error(err);
    } finally {
      setGenerating(false);
    }
  };

  // Clear existing question context when topic changes so the UI never shows stale question for a new topic
  useEffect(() => {
    setQuestion("");
    setQuestionId("");
    setChoices(null);
    setSelectedChoice("");
    setHint("");
    setSolutionSteps([]);
    setFeedback("");
    setStudentAnswer("");
    setAttemptNumber(1);
    // Also cancel any in-flight generation tied to old topic
    if (abortRef.current) {
      abortRef.current.abort();
    }
  }, [topic]);

  const fetchHint = async () => {
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
  };

  const fetchSolution = async () => {
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
  };

  const submitAnswer = async () => {
    if (!questionId) return;
    setLoading(true);
    try {
      const r = await axios.post(API_ENDPOINTS.SUBMIT_ANSWER, {
        question_id: questionId,
        student_answer: choices && selectedChoice ? selectedChoice : studentAnswer,
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
  };

  return (
    <div className="h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6 overflow-hidden flex flex-col">
      <h1 className="text-3xl font-bold mb-6 text-blue-700 text-center flex items-center justify-center gap-2">
        <Target className="w-8 h-8" />
        Math AI Question Generator
      </h1>

      <div className="grid grid-cols-4 gap-4 w-full max-w-6xl mx-auto flex-1 overflow-hidden">
        {/* Left: Controls */}
        <div className="bg-white border-2 border-indigo-300 shadow-lg rounded-xl p-5 col-span-1 flex flex-col overflow-auto">
          <h2 className="text-lg font-semibold text-indigo-700 mb-3 flex items-center gap-2">
            <Settings2 className="w-5 h-5" />
            Options
          </h2>
          <label className="block mb-1 font-medium text-gray-700">Grade:</label>
          <input
            type="number"
            min={1}
            max={12}
            value={grade}
            onChange={(e) => setGrade(Number(e.target.value))}
            className="border-2 border-indigo-200 p-2 w-full rounded-md mb-2 focus:border-indigo-500 focus:outline-none"
          />
          <label className="block mb-1 font-medium text-gray-700">Difficulty:</label>
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
              className="border-2 border-indigo-200 p-2 w-full rounded-md mb-2 focus:border-indigo-500 focus:outline-none"
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          <label className="block mb-1 font-medium text-gray-700">Topic:</label>
            <select
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="border-2 border-indigo-200 p-2 w-full rounded-md mb-2 focus:border-indigo-500 focus:outline-none"
            >
              <option value="algebra">Algebra</option>
              <option value="geometry">Geometry</option>
              <option value="arithmetic">Arithmetic</option>
              <option value="statistics">Statistics</option>
              <option value="probability">Probability</option>
              <option value="trigonometry">Trigonometry</option>
              <option value="number_theory">Number Theory</option>
              <option value="calculus">Calculus</option>
            </select>
          <label className="block mb-1 font-medium text-gray-700">Question Type:</label>
            <select
              value={questionType}
              onChange={(e) => setQuestionType(e.target.value)}
              className="border-2 border-indigo-200 p-2 w-full rounded-md mb-2 focus:border-indigo-500 focus:outline-none"
            >
              <option value="open">Open-ended</option>
              <option value="mcq">Multiple Choice</option>
            </select>
        </div>

        {/* Question Panel */}
        <div className="bg-white border-2 border-yellow-300 shadow-lg rounded-xl p-5 flex flex-col col-span-3 overflow-hidden">
          <h2 className="font-semibold text-yellow-700 mb-2 flex items-center gap-2">
            <BookOpen className="w-5 h-5" />
            Question
          </h2>
          <div className="mt-2 flex items-center space-x-2">
            <button
              onClick={handleGenerate}
              disabled={generating}
              className="bg-blue-600 text-white px-3 py-1.5 rounded-md hover:bg-blue-700 transition shadow-md flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
            >
              <Sparkles className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
              {generating ? "Generating..." : "Generate Question"}
            </button>
          </div>
          <div className="mt-3 overflow-auto flex-1">
            <div className="p-3 bg-yellow-50 rounded-md border-2 border-yellow-300 min-h-[100px]">
              {question ? (
                <p className="text-gray-800 text-lg whitespace-pre-wrap">{question}</p>
              ) : (
                <p className="text-gray-400">No question yet. Click "Generate Question" to begin.</p>
              )}
            </div>
          </div>
        </div>

        {/* Hint & Solution Steps Card */}
        <div className="bg-white border-2 border-purple-300 shadow-lg rounded-xl p-5 flex flex-col overflow-hidden col-span-2">
          <h3 className="text-lg font-semibold text-purple-700 mb-3 flex items-center gap-2">
            <Lightbulb className="w-5 h-5" />
            Hint & Solution
          </h3>
          <div className="mb-3 flex items-center gap-2">
            <button
              onClick={fetchHint}
              disabled={loadingHint || !questionId}
              className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md shadow-md flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
            >
              <Lightbulb className={`w-4 h-4 ${loadingHint ? 'animate-spin' : ''}`} />
              {loadingHint ? "Loading..." : "Get Hint"}
            </button>
            <button
              onClick={fetchSolution}
              disabled={loadingSolution || !questionId}
              className="px-3 py-1.5 bg-gray-800 hover:bg-gray-900 text-white rounded-md shadow-md flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
            >
              <BookOpen className={`w-4 h-4 ${loadingSolution ? 'animate-spin' : ''}`} />
              {loadingSolution ? "Loading..." : "Get Solution"}
            </button>
          </div>
          <div className="flex-1 overflow-y-auto">
            {/* Hint Section */}
            {hint && (
              <div className="mb-4">
                <h4 className="text-sm font-semibold text-indigo-700 mb-2 flex items-center gap-1">
                  <Lightbulb className="w-4 h-4" />
                  Hint:
                </h4>
                <div className="p-4 bg-indigo-50 rounded-md border-2 border-indigo-200 text-indigo-900 whitespace-pre-wrap">
                  {hint}
                </div>
              </div>
            )}

            {/* Solution Steps Section */}
            <div>
              <h4 className="text-sm font-semibold text-green-700 mb-2 flex items-center gap-1">
                <CheckCircle className="w-4 h-4" />
                Solution Steps:
              </h4>
              {solutionSteps && solutionSteps.length > 0 ? (
                <ol className="list-decimal list-inside space-y-3 bg-green-50 p-4 rounded-md border-2 border-green-300 shadow-inner">
                  {solutionSteps.map((s, i) => (
                    <li key={i} className="text-gray-800 leading-relaxed whitespace-pre-wrap">{s}</li>
                  ))}
                </ol>
              ) : (
                <div className="p-4 rounded-md border-2 border-green-200 bg-green-50 text-green-600">
                  Solution steps will appear here after clicking "Get Solution".
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Answer Submission Card */}
        <div className="bg-white border-2 border-indigo-300 shadow-lg rounded-xl p-5 flex flex-col overflow-hidden col-span-2">
          <h3 className="text-lg font-semibold text-indigo-700 mb-3 flex items-center gap-2">
            <CheckCircle className="w-5 h-5" />
            Your Answer
          </h3>
          <div className="flex-1 overflow-auto">
            <label className="block text-sm font-medium text-gray-700 mb-1">Enter your answer:</label>
            {choices && choices.length > 0 ? (
              <div className="space-y-2">
                {choices.map((choice, idx) => (
                  <label
                    key={idx}
                    className="flex items-center p-2 border-2 border-gray-300 rounded-md hover:border-green-500 cursor-pointer"
                  >
                    <input
                      type="radio"
                      name="mcq-choice"
                      value={choice}
                      checked={selectedChoice === choice}
                      onChange={(e) => setSelectedChoice(e.target.value)}
                      className="mr-3"
                    />
                    <span className="text-gray-800">{choice}</span>
                  </label>
                ))}
              </div>
            ) : (
              <input
                type="text"
                value={studentAnswer}
                onChange={(e) => setStudentAnswer(e.target.value)}
                placeholder="Enter answer (e.g. 3/8 or 0.375)"
                className="border-2 border-gray-300 focus:border-green-500 p-2 w-full rounded-md mt-1 focus:outline-none"
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    const btn = document.querySelector('#submit-answer-btn') as HTMLButtonElement | null;
                    if (btn && !btn.disabled) btn.click();
                  }
                }}
              />
            )}

            <div className="mt-3">
              <button
                onClick={submitAnswer}
                id="submit-answer-btn"
                className="px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white rounded-md shadow-md disabled:opacity-50 text-sm"
                disabled={!questionId || loading || (!studentAnswer.trim() && !selectedChoice)}
              >
                {loading ? "Checking..." : "Submit Answer"}
              </button>
            </div>

            {feedback && (
              <div className="text-sm font-medium text-gray-700 mt-3 p-3 bg-blue-50 rounded-md border-2 border-blue-200 whitespace-pre-wrap">
                {feedback}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
