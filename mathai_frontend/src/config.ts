const API_BASE = "http://127.0.0.1:8000/api";

export const API_ENDPOINTS = {
    GENERATE_QUESTION: `${API_BASE}/generate-question`,
    SUBMIT_ANSWER: `${API_BASE}/submit-answer`,
    STUDENT_PROGRESS: (studentId: string) => `${API_BASE}/student-progress/${studentId}`,
    HINT: (questionId: string) => `${API_BASE}/questions/${questionId}/hint`,
    SOLUTION: (questionId: string) => `${API_BASE}/questions/${questionId}/solution`,
    CHOICES: (questionId: string) => `${API_BASE}/questions/${questionId}/choices`,
    QUALITY_SUMMARY: `${API_BASE}/quality/summary`,
    QUALITY_PER_QUESTION: `${API_BASE}/quality/questions`,
};
