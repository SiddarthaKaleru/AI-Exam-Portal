import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getResult } from '../services/api';
import Navbar from '../components/Navbar';

export default function Results() {
  const { code } = useParams();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadResult();
  }, [code]);

  const loadResult = async () => {
    try {
      const { data } = await getResult(code);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load results');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-dark-950 flex items-center justify-center">
        <div className="animate-spin h-10 w-10 border-2 border-primary-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-dark-950">
        <Navbar />
        <div className="max-w-3xl mx-auto px-6 py-12 text-center">
          <span className="text-5xl block mb-4">⚠️</span>
          <p className="text-dark-400">{error}</p>
        </div>
      </div>
    );
  }

  const submission = result?.result || {};
  const percentage = submission.percentage || 0;
  const grade = percentage >= 90 ? 'A+' : percentage >= 80 ? 'A' : percentage >= 70 ? 'B' : percentage >= 60 ? 'C' : percentage >= 40 ? 'D' : 'F';
  const gradeColors = { 'A+': 'text-emerald-400', 'A': 'text-emerald-400', 'B': 'text-blue-400', 'C': 'text-amber-400', 'D': 'text-orange-400', 'F': 'text-red-400' };

  return (
    <div className="min-h-screen bg-dark-950">
      <Navbar />
      <div className="max-w-4xl mx-auto px-6 py-8">
        <h1 className="text-3xl font-bold text-white mb-2">Exam Results</h1>
        <p className="text-dark-400 mb-8">{result?.exam_title}</p>

        {/* Score Card */}
        <div className="glass-card p-8 mb-8 text-center animate-slide-up">
          <div className="w-32 h-32 mx-auto mb-4 rounded-full border-4 border-primary-500/30 flex items-center justify-center relative">
            <div className="text-center">
              <span className={`text-5xl font-bold ${gradeColors[grade]}`}>{grade}</span>
            </div>
            {/* Circular progress */}
            <svg className="absolute inset-0 w-full h-full -rotate-90" viewBox="0 0 128 128">
              <circle cx="64" cy="64" r="58" fill="none" stroke="currentColor" className="text-dark-700" strokeWidth="4" />
              <circle cx="64" cy="64" r="58" fill="none" stroke="currentColor" className="text-primary-500"
                strokeWidth="4" strokeDasharray={`${percentage * 3.64} 364`} strokeLinecap="round" />
            </svg>
          </div>
          <p className="text-4xl font-bold text-white">{submission.score}/{submission.max_score}</p>
          <p className="text-lg text-dark-400 mt-1">{percentage}%</p>
        </div>

        {/* Detailed Results */}
        <div className="glass-card p-6">
          <h2 className="text-xl font-bold text-white mb-4">Question-wise Breakdown</h2>
          <div className="space-y-3">
            {(submission.evaluation_details || []).map((detail, i) => (
              <div key={i} className={`p-4 rounded-xl border transition-all ${
                detail.marks_obtained === detail.marks_total
                  ? 'bg-emerald-500/10 border-emerald-500/20'
                  : detail.marks_obtained > 0
                  ? 'bg-amber-500/10 border-amber-500/20'
                  : 'bg-red-500/10 border-red-500/20'
              }`}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-dark-300">
                    Q{detail.question_id} • {detail.type?.toUpperCase()}
                  </span>
                  <span className={`font-bold ${
                    detail.marks_obtained === detail.marks_total ? 'text-emerald-400' :
                    detail.marks_obtained > 0 ? 'text-amber-400' : 'text-red-400'
                  }`}>
                    {detail.marks_obtained}/{detail.marks_total}
                  </span>
                </div>
                {detail.feedback && (
                  <p className="text-sm text-dark-300 mt-1">{detail.feedback}</p>
                )}
                {detail.correct_answer && detail.type === 'mcq' && (
                  <div className="mt-2 text-xs">
                    <span className="text-dark-500">Your answer: </span>
                    <span className={detail.is_correct ? 'text-emerald-400' : 'text-red-400'}>{detail.student_answer}</span>
                    {!detail.is_correct && (
                      <><span className="text-dark-500"> | Correct: </span><span className="text-emerald-400">{detail.correct_answer}</span></>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="mt-6 text-center">
          <Link to="/student" className="btn-secondary">← Back to Dashboard</Link>
        </div>
      </div>
    </div>
  );
}
