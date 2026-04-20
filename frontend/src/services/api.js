/* API service — Axios instance with JWT interceptor */

import axios from 'axios';

const API = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to every request
API.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ─── Auth ─────────────────────────────────────────────────────────

export const register = (data) => API.post('/auth/register', data);
export const login = (data) => API.post('/auth/login', data);

// ─── Admin ────────────────────────────────────────────────────────

export const uploadPDF = (files) => {
  const formData = new FormData();
  files.forEach((file) => formData.append('files', file));
  return API.post('/admin/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const createExam = (data) => API.post('/admin/create-exam', data);
export const listExams = () => API.get('/admin/exams');
export const getExamDetails = (examId) => API.get(`/admin/exam/${examId}`);

// ─── Exam ─────────────────────────────────────────────────────────

export const fetchExam = (code) => API.get(`/exam/${code}`);
export const startExam = (code) => API.post(`/exam/${code}/start`);
export const submitExam = (code, answers) => API.post(`/exam/${code}/submit`, { answers });
export const reportAntiCheat = (code, events) => API.post(`/exam/${code}/anti-cheat`, { events });
export const getResult = (code) => API.get(`/exam/${code}/result`);
export const listStudentSubmissions = () => API.get('/exam/student/submissions');

// ─── Analytics ────────────────────────────────────────────────────

export const getAnalytics = (examId) => API.get(`/analytics/${examId}`);

export default API;
