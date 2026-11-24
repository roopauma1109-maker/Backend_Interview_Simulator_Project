
import axios from 'axios';

/**
 * Centralised Axios client.
 * Every endpoint mirrors Backend/main.py.
 */

export class ApiError extends Error {
  constructor(message, { status = 0, data = null, code = '' } = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
    this.code = code;
  }
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  timeout: 15000,
});

function detailToMessage(detail) {
  if (!detail) return null;

  if (typeof detail === 'string') return detail;

  if (Array.isArray(detail)) {
    return detail.map((d) => d.msg || JSON.stringify(d)).join('; ');
  }

  return JSON.stringify(detail);
}

// ---- Response Interceptor ----

api.interceptors.response.use(
  (res) => {
    if (
      res.data &&
      res.data.status === 'error' &&
      !res.data.verdict
    ) {
      throw new ApiError(
        res.data.message || 'The server reported an error.',
        {
          status: res.status,
          data: res.data,
        }
      );
    }

    return res.data;
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response;

      throw new ApiError(
        detailToMessage(data?.detail) ||
          data?.message ||
          `Request failed (${status}).`,
        { status, data }
      );
    }

    if (error.code === 'ECONNABORTED') {
      throw new ApiError(
        'The request timed out. Please try again.',
        { code: 'timeout' }
      );
    }

    throw new ApiError(
      'Cannot reach the server. Check that the backend is running and VITE_API_BASE_URL is correct.',
      { code: 'network' }
    );
  }
);

// ---- Auth ----

export const registerUser = (username, password) =>
  api.post('/register', { username, password });

export const loginUser = (username, password) =>
  api.post('/login', { username, password });

// ---- Question Bank / Basic Topics ----

export const fetchHealth = () =>
  api.get('/');

export const fetchTopics = () =>
  api.get('/topics');

// ---- Intermediate Question Bank ----

export const fetchIntermediateTopics = () =>
  api.get('/intermediate/topics');

export const fetchIntermediateQuestions = (topic) =>
  api.get(`/intermediate/questions/${encodeURIComponent(topic)}`);

// ---- Topic Interview ----

export const startInterview = ({
  topic,
  difficulty,
  numQuestions,
  userId,
  questionLevel = 'basic',
}) =>
  api.get('/interview/start', {
    params: {
      topic,
      difficulty,
      num_questions: numQuestions,
      user_id: userId,
      question_level: questionLevel,
    },
  });

export const nextQuestion = (sessionId) =>
  api.get(`/interview/next/${encodeURIComponent(sessionId)}`);

export const submitAnswer = (sessionId, answer) =>
  api.post(
    `/interview/answer/${encodeURIComponent(sessionId)}`,
    { answer }
  );

export const fetchResult = (sessionId) =>
  api.get(`/interview/result/${encodeURIComponent(sessionId)}`);

// ---- Resume ----

export const uploadResume = (userId, file, onProgress) => {
  const form = new FormData();

  form.append('file', file);

  return api.post('/resume/upload', form, {
    params: { user_id: userId },
    timeout: 60000,
    onUploadProgress: (e) => {
      if (e.total && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    },
  });
};

export const generateResumeQuestions = ({
  userId,
  resumeId,
  numQuestions,
}) =>
  api.post('/resume/questions', {
    user_id: userId,
    resume_id: resumeId,
    num_questions: numQuestions,
  });

// ---- Coding Arena ----

export const runCode = (
  language,
  code,
  input = '',
  expectedOutput = null,
  testCases = [],
  userId = null
) =>
  api.post(
    '/coding/run',
    {
      user_id: userId,
      language,
      code,
      input,
      expected_output: expectedOutput,
      test_cases: testCases,
    },
    {
      timeout: 60000,
    }
  );

// ---- AI Coach ----

export const coachChat = (message, history) =>
  api.post(
    '/coach/chat',
    { message, history },
    { timeout: 45000 }
  );

export default api;
