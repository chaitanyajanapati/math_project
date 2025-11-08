import { API_ENDPOINTS } from "../config";

export async function testBackendConnection() {
  const response = await fetch("http://127.0.0.1:8000/");
  if (!response.ok) throw new Error("Connection failed");
  return response.json();
}

export type QualitySummary = {
  counts: { total: number; by_topic: Record<string, number> };
  quality: {
    clarity: number;
    difficulty_calibration: number;
    educational_value: number;
    engagement: number;
    overall: number;
  };
  complexity: { avg_score: number; by_level: Record<string, number> };
  issues: { top: { issue: string; count: number }[] };
  samples: Array<{
    id: string;
    question: string;
    topic: string;
    grade: number;
    difficulty: string;
    complexity: { score: number; level: string; normalized: number };
    quality: Record<string, number>;
    issues: string[];
  }>;
};

export type QualityQuestionItem = {
  id: string;
  question: string;
  topic: string;
  grade: number;
  difficulty: string;
  complexity: {
    score: number;
    level: string;
    breakdown: Record<string, number>;
    normalized: number;
  };
  quality: Record<string, number>;
  issues: string[];
};

export async function fetchQualitySummary(): Promise<QualitySummary> {
  const r = await fetch(API_ENDPOINTS.QUALITY_SUMMARY);
  if (!r.ok) throw new Error("Failed to fetch quality summary");
  return r.json();
}

export async function fetchQualityPerQuestion(): Promise<QualityQuestionItem[]> {
  const r = await fetch(API_ENDPOINTS.QUALITY_PER_QUESTION);
  if (!r.ok) throw new Error("Failed to fetch per-question quality");
  return r.json();
}

export async function regenerateChoices(questionId: string): Promise<{ choices: string[] }>{
  const r = await fetch(API_ENDPOINTS.CHOICES(questionId), { method: 'POST' });
  if (!r.ok) throw new Error('Failed to regenerate choices');
  return r.json();
}
