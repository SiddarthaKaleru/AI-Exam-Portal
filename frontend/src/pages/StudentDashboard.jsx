import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { listStudentSubmissions } from '../services/api';

export default function StudentDashboard() {
  const navigate = useNavigate();
  const [examCode, setExamCode] = useState('');
  const [error, setError] = useState('');
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  useEffect(() => {
    loadSubmissions();
  }, []);

  const loadSubmissions = async () => {
    try {
      const { data } = await listStudentSubmissions();
      setSubmissions(data.submissions || []);
    } catch (err) {
      console.error("Failed to load past exams:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleJoin = () => {
    if (!examCode.trim()) return setError('Please enter an exam code');
    setError('');
    navigate(`/exam/${examCode.trim().toUpperCase()}`);
  };

  return (
    <div className="min-h-screen bg-dark-950">
      <Navbar />
      <div className="max-w-3xl mx-auto px-6 py-12">
        {/* Welcome */}
        <div className="text-center mb-12 animate-fade-in">
          <h1 className="text-4xl font-bold text-white mb-2">
            Welcome, <span className="gradient-text">{user.name || 'Student'}</span> 👋
          </h1>
          <p className="text-dark-400 text-lg">Enter your exam code to get started</p>
        </div>

        {/* Exam Code Input */}
        <div className="glass-card p-8 animate-slide-up">
          <div className="text-center mb-6">
            <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center">
              <span className="text-3xl">🎯</span>
            </div>
            <h2 className="text-xl font-bold text-white">Join Exam</h2>
            <p className="text-dark-400 text-sm mt-1">Enter the 6-character code provided by your instructor</p>
          </div>

          {error && (
            <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm text-center">{error}</div>
          )}

          <div className="flex gap-3">
            <input
              type="text"
              value={examCode}
              onChange={(e) => setExamCode(e.target.value.toUpperCase())}
              maxLength={6}
              className="input-field text-center text-2xl font-mono tracking-[0.3em] uppercase"
              placeholder="ABC123"
              id="exam-code-input"
              onKeyDown={(e) => e.key === 'Enter' && handleJoin()}
            />
            <button onClick={handleJoin} className="btn-primary px-8" id="join-exam-btn">
              Join →
            </button>
          </div>
        </div>

        {/* Tips */}
        <div className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            { icon: '⏱️', title: 'Timer', desc: 'Exam auto-submits when time runs out' },
            { icon: '🚫', title: 'Anti-Cheat', desc: 'Tab switching and copy-paste are monitored' },
            { icon: '📊', title: 'Instant Results', desc: 'Get your score immediately after submission' },
          ].map((tip, i) => (
            <div key={i} className="glass-card p-4 text-center animate-slide-up" style={{ animationDelay: `${(i + 1) * 150}ms` }}>
              <span className="text-2xl block mb-2">{tip.icon}</span>
              <h3 className="text-sm font-bold text-white mb-1">{tip.title}</h3>
              <p className="text-xs text-dark-400">{tip.desc}</p>
            </div>
          ))}
        </div>
        
        {/* Past Exams Table */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-white mb-6">Past Exams</h2>
          <div className="glass-card overflow-hidden">
            {loading ? (
              <div className="p-8 text-center text-dark-400">
                <div className="animate-spin h-6 w-6 border-2 border-primary-500 border-t-transparent rounded-full mx-auto mb-3" />
                Loading your history...
              </div>
            ) : submissions.length === 0 ? (
              <div className="p-12 text-center">
                <span className="text-4xl block mb-3">📭</span>
                <p className="text-dark-400">You haven't taken any exams yet.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-dark-800/50 border-b border-dark-700">
                      <th className="p-4 text-sm font-semibold text-dark-300">Exam</th>
                      <th className="p-4 text-sm font-semibold text-dark-300">Date Taken</th>
                      <th className="p-4 text-sm font-semibold text-dark-300">Score</th>
                      <th className="p-4 text-sm font-semibold text-dark-300 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-dark-700/50">
                    {submissions.map((sub) => (
                      <tr key={sub.submission_id} className="hover:bg-dark-800/30 transition-colors">
                        <td className="p-4">
                          <p className="font-medium text-white">{sub.exam_title}</p>
                          <p className="text-xs text-dark-400 mt-0.5 font-mono">Code: {sub.exam_code}</p>
                        </td>
                        <td className="p-4 text-sm text-dark-300">
                          {new Date(sub.submitted_at).toLocaleDateString(undefined, {
                            year: 'numeric', month: 'short', day: 'numeric',
                            hour: '2-digit', minute: '2-digit'
                          })}
                        </td>
                        <td className="p-4">
                          <div className="flex items-center gap-2">
                            <span className={`font-bold ${
                              sub.percentage >= 80 ? 'text-emerald-400' :
                              sub.percentage >= 60 ? 'text-amber-400' :
                              'text-red-400'
                            }`}>
                              {sub.score}/{sub.max_score}
                            </span>
                            <span className="text-xs text-dark-500">({sub.percentage}%)</span>
                          </div>
                        </td>
                        <td className="p-4 text-right">
                          <Link 
                            to={`/result/${sub.exam_code}`} 
                            className="inline-flex items-center justify-center px-4 py-1.5 rounded-lg text-sm font-medium bg-dark-700 text-dark-300 hover:text-white hover:bg-primary-600 transition-all border border-dark-600"
                          >
                            View Result
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
