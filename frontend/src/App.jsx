import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import AdminDashboard from './pages/AdminDashboard';
import CreateExam from './pages/CreateExam';
import StudentDashboard from './pages/StudentDashboard';
import ExamPortal from './pages/ExamPortal';
import Results from './pages/Results';
import Analytics from './pages/Analytics';
import ProtectedRoute from './components/ProtectedRoute';

export default function App() {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Admin Routes */}
        <Route path="/admin" element={
          <ProtectedRoute requiredRole="admin"><AdminDashboard /></ProtectedRoute>
        } />
        <Route path="/create-exam" element={
          <ProtectedRoute requiredRole="admin"><CreateExam /></ProtectedRoute>
        } />
        <Route path="/analytics/:examId" element={
          <ProtectedRoute requiredRole="admin"><Analytics /></ProtectedRoute>
        } />

        {/* Student Routes */}
        <Route path="/student" element={
          <ProtectedRoute requiredRole="student"><StudentDashboard /></ProtectedRoute>
        } />
        <Route path="/exam/:code" element={
          <ProtectedRoute><ExamPortal /></ProtectedRoute>
        } />
        <Route path="/result/:code" element={
          <ProtectedRoute><Results /></ProtectedRoute>
        } />

        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
}
