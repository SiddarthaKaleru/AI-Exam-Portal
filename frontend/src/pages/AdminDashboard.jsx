import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { listExams, toggleExamStatus } from '../services/api';
import Navbar from '../components/Navbar';

export default function AdminDashboard() {
  const [exams, setExams] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadExams();
  }, []);

  const loadExams = async () => {
    try {
      const { data } = await listExams();
      setExams(data.exams || []);
    } catch (err) {
      console.error('Failed to load exams:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleStatus = async (examId) => {
    try {
      const { data } = await toggleExamStatus(examId);
      setExams(prev => prev.map(e =>
        e._id === examId ? { ...e, status: data.status } : e
      ));
    } catch (err) {
      console.error('Failed to toggle status:', err);
    }
  };

  const stats = [
    { label: 'Total Exams', value: exams.length, icon: '📝', color: 'from-indigo-500 to-blue-500' },
    { label: 'Active', value: exams.filter(e => e.status === 'active').length, icon: '🟢', color: 'from-emerald-500 to-teal-500' }
  ];

  return (
    <div className="min-h-screen bg-dark-950">
      <Navbar />
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8 animate-fade-in">
          <div>
            <h1 className="text-3xl font-bold text-white">Admin Dashboard</h1>
            <p className="text-dark-400 mt-1">Manage your AI-generated exams</p>
          </div>
          <Link to="/create-exam" className="btn-primary flex items-center gap-2" id="create-exam-btn">
            <span>+</span> Create Exam
          </Link>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
          {stats.map((stat, i) => (
            <div key={i} className="glass-card p-5 animate-slide-up" style={{ animationDelay: `${i * 100}ms` }}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-dark-400 text-sm">{stat.label}</p>
                  <p className="text-3xl font-bold text-white mt-1">{stat.value}</p>
                </div>
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${stat.color} flex items-center justify-center shadow-lg`}>
                  <span className="text-2xl">{stat.icon}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Exams List */}
        <div className="glass-card p-6">
          <h2 className="text-xl font-bold text-white mb-4">Your Exams</h2>
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin h-8 w-8 border-2 border-primary-500 border-t-transparent rounded-full mx-auto" />
              <p className="text-dark-400 mt-3">Loading exams...</p>
            </div>
          ) : exams.length === 0 ? (
            <div className="text-center py-12">
              <span className="text-5xl mb-4 block">📭</span>
              <p className="text-dark-400">No exams yet. Create your first AI-powered exam!</p>
              <Link to="/create-exam" className="btn-primary inline-block mt-4">Create Exam</Link>
            </div>
          ) : (
            <div className="space-y-3">
              {exams.map((exam) => (
                <div key={exam._id} className="flex items-center justify-between p-4 bg-dark-800/50 rounded-xl border border-dark-700 hover:border-primary-500/30 transition-all group">
                  <div className="flex-1">
                    <h3 className="text-white font-medium group-hover:text-primary-400 transition-colors">
                      {exam.title || `${exam.subject} — ${exam.topic}`}
                    </h3>
                    <div className="flex items-center gap-4 mt-1 text-sm text-dark-400">
                      <span>📚 {exam.subject}</span>
                      <span>⏱️ {exam.duration_minutes} min</span>
                      <span>📊 {exam.config?.total_questions || '?'} questions</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="px-3 py-1 rounded-lg bg-primary-500/20 text-primary-400 font-mono text-sm font-bold">
                      {exam.exam_code}
                    </span>
                    <button
                      onClick={() => handleToggleStatus(exam._id)}
                      className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                        exam.status === 'active'
                          ? 'bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 border border-emerald-500/25'
                          : 'bg-red-500/15 text-red-400 hover:bg-red-500/25 border border-red-500/25'
                      }`}
                      title={exam.status === 'active' ? 'Click to deactivate' : 'Click to activate'}
                      id={`toggle-status-${exam._id}`}
                    >
                      <span className={`w-8 h-4 rounded-full relative transition-all ${
                        exam.status === 'active' ? 'bg-emerald-500/40' : 'bg-dark-600'
                      }`}>
                        <span className={`absolute top-0.5 w-3 h-3 rounded-full transition-all ${
                          exam.status === 'active' ? 'left-4 bg-emerald-400' : 'left-0.5 bg-dark-400'
                        }`} />
                      </span>
                      {exam.status === 'active' ? 'Active' : 'Inactive'}
                    </button>
                    <Link to={`/analytics/${exam._id}`}
                      className="px-3 py-1.5 rounded-lg bg-dark-700 text-dark-300 hover:text-white hover:bg-dark-600 text-sm transition-all">
                      📊 Analytics
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
