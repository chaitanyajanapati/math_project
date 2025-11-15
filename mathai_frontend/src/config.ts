const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const API_VERSION = "v1"; // API version

export const API_ENDPOINTS = {
    // Authentication
    REGISTER: `${API_BASE}/api/${API_VERSION}/auth/register`,
    LOGIN: `${API_BASE}/api/${API_VERSION}/auth/login`,
    LOGOUT: `${API_BASE}/api/${API_VERSION}/auth/logout`,
    ME: `${API_BASE}/api/${API_VERSION}/auth/me`,
    
    // Questions
    GENERATE_QUESTION: `${API_BASE}/api/${API_VERSION}/generate-question`,
    SUBMIT_ANSWER: `${API_BASE}/api/${API_VERSION}/submit-answer`,
    STUDENT_PROGRESS: (studentId: string) => `${API_BASE}/api/${API_VERSION}/student-progress/${studentId}`,
    HINT: (questionId: string) => `${API_BASE}/api/${API_VERSION}/questions/${questionId}/hint`,
    SOLUTION: (questionId: string) => `${API_BASE}/api/${API_VERSION}/questions/${questionId}/solution`,
    CHOICES: (questionId: string) => `${API_BASE}/api/${API_VERSION}/questions/${questionId}/choices`,
    QUALITY_SUMMARY: `${API_BASE}/api/${API_VERSION}/quality/summary`,
    QUALITY_PER_QUESTION: `${API_BASE}/api/${API_VERSION}/quality/questions`,
};
