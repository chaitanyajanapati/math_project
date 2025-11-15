import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { API_ENDPOINTS } from "../config";
import { Sparkles, Lightbulb, CheckCircle, BookOpen, Settings2, Target } from "lucide-react";
import MathRenderer from "../components/MathRenderer";
import Timer from "../components/Timer";
import GeometryVisualizer from "../components/GeometryVisualizer";
import { regenerateChoices } from "../services/api";

export default function QuestionGenerator() {
  const [grade, setGrade] = useState<number>(8);
  const [difficulty, setDifficulty] = useState<string>("medium");
  const [topic, setTopic] = useState<string>("algebra");
  const [questionType, setQuestionType] = useState<string>("open");
  const [question, setQuestion] = useState<string>("");
  const [questionId, setQuestionId] = useState<string>("");
  // Hints are tracked in allHints array (tiered)
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
  const [timedMode, setTimedMode] = useState<boolean>(false);
  // Time tracking handled internally by Timer; not persisted here
  const [hintLevel, setHintLevel] = useState<number>(0); // 0=none, 1=conceptual, 2=strategic, 3=procedural
  const [allHints, setAllHints] = useState<string[]>([]); // Store all hints received

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
      console.log("Generate response:", res.data);
      console.log("Question type was:", questionType);
      console.log("Raw choices from response:", res.data.choices);
      console.log("Is array?", Array.isArray(res.data.choices));
      
      setQuestion(res.data.question);
      setQuestionId(res.data.id || "");
      
      // Ensure choices are properly set for MCQ questions
      const receivedChoices = res.data.choices;
      if (Array.isArray(receivedChoices) && receivedChoices.length > 0) {
        console.log("Setting choices to:", receivedChoices);
        setChoices(receivedChoices);
      } else {
        console.log("No valid choices received, setting to null");
        setChoices(null);
      }
      
  setSelectedChoice("");
      setSolutionSteps([]);
      setFeedback("");
      setStudentAnswer("");
      setAttemptNumber(1);
      setHintLevel(0);
      setAllHints([]);
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
    setSolutionSteps([]);
    setFeedback("");
    setStudentAnswer("");
    setAttemptNumber(1);
    setHintLevel(0);
    setAllHints([]);
    // Also cancel any in-flight generation tied to old topic
    if (abortRef.current) {
      abortRef.current.abort();
    }
  }, [topic]);

  const fetchHint = async () => {
    if (!questionId) return;
    const nextLevel = hintLevel + 1;
    if (nextLevel > 3) return; // Max 3 hint levels

    setLoadingHint(true);
    try {
      const r = await axios.post(API_ENDPOINTS.HINT(questionId), null, {
        params: { hint_level: nextLevel }
      });
  const newHint = r.data.hint || "";
      setHintLevel(nextLevel);
      setAllHints(prev => [...prev, newHint]);
    } catch (e) {
      console.error(e);
  setAllHints(prev => [...prev, "Could not fetch hint."]);
    } finally {
      setLoadingHint(false);
    }
  };

  const fetchSolution = async () => {
    if (!questionId) {
      console.warn("Cannot fetch solution: questionId is missing");
      return;
    }
    setLoadingSolution(true);
    try {
      console.log("Fetching solution for question:", questionId);
      const r = await axios.post(API_ENDPOINTS.SOLUTION(questionId));
      console.log("Solution response:", r.data);
      
      const steps = r.data.solution_steps || [];
      if (steps.length === 0) {
        console.warn("Solution response contained no steps");
        setSolutionSteps(["No solution steps available."]);
      } else {
        console.log(`Setting ${steps.length} solution steps`);
        setSolutionSteps(steps);
      }
    } catch (e) {
      console.error("Error fetching solution:", e);
      setSolutionSteps(["Could not fetch solution. Error: " + (e instanceof Error ? e.message : String(e))]);
    } finally {
      setLoadingSolution(false);
    }
  };

  const retryChoices = async () => {
    if (!questionId) return;
    try {
      const res = await regenerateChoices(questionId);
      const opts = res.choices || [];
      if (Array.isArray(opts) && opts.length > 0) {
        setChoices(opts);
      }
    } catch (e) {
      console.error("Failed to regenerate choices", e);
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
  if (data.hint) setAllHints(prev => [...prev, data.hint]);
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
    <div className="bg-linear-to-br from-blue-50 via-indigo-50 to-purple-50 p-6 min-h-[calc(100vh-64px)] flex flex-col">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-blue-700 flex items-center gap-2">
          <Target className="w-8 h-8" />
          Question Generator
        </h1>
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={timedMode}
              onChange={(e) => setTimedMode(e.target.checked)}
              className="w-4 h-4 accent-blue-600"
            />
            <span className="text-sm font-medium text-gray-700">Timed Mode</span>
          </label>
          {timedMode && question && (
            <div data-testid="timer">
              <Timer mode="stopwatch" autoStart={true} onTimeUpdate={() => {}} />
            </div>
          )}
        </div>
      </div>

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
            data-testid="grade-input"
          />
          <label className="block mb-1 font-medium text-gray-700">Difficulty:</label>
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
              className="border-2 border-indigo-200 p-2 w-full rounded-md mb-2 focus:border-indigo-500 focus:outline-none"
              data-testid="difficulty-select"
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
              data-testid="topic-select"
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
              data-testid="question-type-select"
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
              data-testid="generate-btn"
            >
              <Sparkles className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
              {generating ? "Generating..." : "Generate Question"}
            </button>
          </div>
          <div className="mt-3 overflow-auto flex-1">
            <div className="p-3 bg-yellow-50 rounded-md border-2 border-yellow-300 min-h-[100px]" data-testid="question-panel">
              {question ? (
                <>
                  <MathRenderer content={question} className="text-gray-800 text-lg whitespace-pre-wrap mb-4" />
                  {topic === 'geometry' && <GeometryVisualizer question={question} className="mt-4" />}
                </>
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
              disabled={loadingHint || !questionId || hintLevel >= 3}
              className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md shadow-md flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              data-testid="hint-btn"
            >
              <Lightbulb className={`w-4 h-4 ${loadingHint ? 'animate-spin' : ''}`} />
              {loadingHint ? "Loading..." : hintLevel === 0 ? "Get Hint" : `Next Hint (${hintLevel}/3)`}
            </button>
            {hintLevel > 0 && (
              <span className="text-xs text-gray-600 bg-yellow-100 px-2 py-1 rounded">
                -{hintLevel * 10} pts used
              </span>
            )}
            <button
              onClick={fetchSolution}
              disabled={loadingSolution || !questionId}
              className="px-3 py-1.5 bg-gray-800 hover:bg-gray-900 text-white rounded-md shadow-md flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              data-testid="solution-btn"
            >
              <BookOpen className={`w-4 h-4 ${loadingSolution ? 'animate-spin' : ''}`} />
              {loadingSolution ? "Loading..." : "Get Solution"}
            </button>
          </div>
          <div className="flex-1 overflow-y-auto">
            {/* Hint Section */}
            {allHints.length > 0 && (
              <div className="mb-4 space-y-3" data-testid="hints-section">
                <h4 className="text-sm font-semibold text-indigo-700 mb-2 flex items-center gap-1">
                  <Lightbulb className="w-4 h-4" />
                  Hints ({allHints.length}/3):
                </h4>
                {allHints.map((h, idx) => (
                  <div key={idx} className={`p-3 rounded-md border-2 ${
                    idx === 0 ? 'bg-blue-50 border-blue-200' :
                    idx === 1 ? 'bg-indigo-50 border-indigo-200' :
                    'bg-purple-50 border-purple-200'
                  }`}>
                    <div className="flex items-start gap-2">
                      <span className="text-xs font-bold text-gray-600 mt-0.5">
                        {idx === 0 ? '💡' : idx === 1 ? '📋' : '🔧'}
                      </span>
                      <MathRenderer content={h} className="text-sm flex-1" />
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Solution Steps Section */}
            <div>
              <h4 className="text-sm font-semibold text-green-700 mb-2 flex items-center gap-1">
                <CheckCircle className="w-4 h-4" />
                Solution Steps:
              </h4>
              {solutionSteps && solutionSteps.length > 0 ? (
                <div className="space-y-3 bg-green-50 p-4 rounded-md border-2 border-green-300 shadow-inner" data-testid="solution-steps">
                  {solutionSteps.map((s, i) => (
                    <div key={i} className="text-gray-800 leading-relaxed">
                      <MathRenderer content={s} className="inline whitespace-pre-wrap" />
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-4 rounded-md border-2 border-green-200 bg-green-50 text-green-600" data-testid="solution-steps-placeholder">
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
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Enter your answer:
              {questionType === "mcq" && (
                <span className="ml-2 text-xs text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                  MCQ Mode {choices && choices.length > 0 ? `(${choices.length} options)` : '(Loading...)'}
                </span>
              )}
            </label>
            {choices && choices.length > 0 ? (
              <div className="space-y-2" data-testid="mcq-choices">
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
                    <MathRenderer content={choice} className="text-gray-800" />
                  </label>
                ))}
              </div>
            ) : questionType === "mcq" && question ? (
              <div className="p-4 bg-yellow-50 border-2 border-yellow-300 rounded-md text-yellow-700">
                <p className="text-sm font-medium">⚠️ Multiple choice options not loaded.</p>
                <p className="text-xs mt-1">Try generating a new question or check the console for errors.</p>
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
                data-testid="submit-answer-btn"
              >
                {loading ? "Checking..." : "Submit Answer"}
              </button>
            </div>

            {/* MCQ Fallback helper */}
            {questionType === "mcq" && question && (!choices || choices.length === 0) && (
              <div className="mt-3 p-3 bg-yellow-50 border-2 border-yellow-300 rounded-md">
                <div className="text-sm text-yellow-800 font-medium mb-2">Multiple choice options not loaded.</div>
                <button
                  onClick={retryChoices}
                  className="px-3 py-1.5 bg-yellow-600 hover:bg-yellow-700 text-white rounded-md shadow-sm text-sm"
                >
                  Retry options
                </button>
              </div>
            )}

            {feedback && (
              <div className="text-sm font-medium text-gray-700 mt-3 p-3 bg-blue-50 rounded-md border-2 border-blue-200">
                <MathRenderer content={feedback} className="whitespace-pre-wrap" />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
