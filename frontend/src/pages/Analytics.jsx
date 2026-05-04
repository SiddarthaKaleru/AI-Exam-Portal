import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getAnalytics, getExamDetails } from '../services/api';
import Navbar from '../components/Navbar';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';

const COLORS = ['#6366f1', '#8b5cf6', '#a78bfa', '#c4b5fd', '#818cf8'];

const CustomYAxisTick = ({ x, y, payload }) => {
  const maxLineLength = 25;
  const words = payload.value.split(' ');
  let lines = [];
  let currentLine = '';

  words.forEach(word => {
    if ((currentLine + word).length > maxLineLength) {
      if (currentLine) lines.push(currentLine.trim());
      currentLine = word + ' ';
    } else {
      currentLine += word + ' ';
    }
  });
  if (currentLine) lines.push(currentLine.trim());

  return (
    <g transform={`translate(${x - 10},${y})`}>
      {lines.map((line, i) => (
        <text
          key={i}
          x={0}
          y={(i - (lines.length - 1) / 2) * 12}
          dy={4}
          textAnchor="end"
          fill="#94a3b8"
          fontSize={11}
        >
          {line}
        </text>
      ))}
    </g>
  );
};

export default function Analytics() {
  const { examId } = useParams();
  const [analytics, setAnalytics] = useState(null);
  const [exam, setExam] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, [examId]);

  const loadAnalytics = async () => {
    try {
      const [analyticsRes, examRes] = await Promise.allSettled([
        getAnalytics(examId),
        getExamDetails(examId),
      ]);
      if (analyticsRes.status === 'fulfilled') setAnalytics(analyticsRes.value.data.analytics);
      if (examRes.status === 'fulfilled') setExam(examRes.value.data.exam);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-dark-950 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-10 w-10 border-2 border-primary-500 border-t-transparent rounded-full mx-auto" />
          <p className="text-dark-400 mt-4">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (!analytics || analytics.total_students === 0) {
    return (
      <div className="min-h-screen bg-dark-950">
        <Navbar />
        <div className="max-w-5xl mx-auto px-6 py-12">
          <div className="text-center mb-8">
            <span className="text-6xl block mb-4">📊</span>
            <h2 className="text-2xl font-bold text-white mb-2">No Submissions Yet</h2>
            <p className="text-dark-400">No students have submitted this exam yet.</p>
          </div>

          {/* Show questions even when no submissions */}
          {exam && exam.questions && exam.questions.length > 0 && (
            <div className="glass-card p-6">
              <h3 className="text-lg font-bold text-white mb-4">📝 Exam Questions ({exam.questions.length})</h3>
              <div className="space-y-4">
                {exam.questions.map((q, i) => (
                  <div key={q.id || i} className="p-4 bg-dark-800/50 rounded-xl border border-dark-700">
                    <div className="flex items-start justify-between gap-4 mb-2">
                      <p className="text-white font-medium">
                        <span className="text-dark-500 mr-2">Q{i + 1}.</span>
                        {q.question}
                      </p>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                          q.type === 'mcq' ? 'bg-blue-500/20 text-blue-400' :
                          q.type === 'short' ? 'bg-amber-500/20 text-amber-400' :
                          'bg-purple-500/20 text-purple-400'
                        }`}>
                          {q.type === 'mcq' ? 'MCQ' : q.type === 'short' ? 'Short' : 'Long'}
                        </span>
                        <span className="px-2 py-0.5 rounded text-xs font-medium bg-dark-700 text-dark-300">
                          {q.marks} {q.marks === 1 ? 'mark' : 'marks'}
                        </span>
                      </div>
                    </div>
                    {q.difficulty && (
                      <p className="text-xs text-dark-500 mb-2">Difficulty: <span className={`font-medium ${
                        q.difficulty === 'easy' ? 'text-emerald-400' : q.difficulty === 'medium' ? 'text-amber-400' : 'text-red-400'
                      }`}>{q.difficulty}</span></p>
                    )}
                    {q.type === 'mcq' && q.options && (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-3">
                        {q.options.map((opt, j) => (
                          <div key={j} className={`px-3 py-2 rounded-lg text-sm ${
                            opt === q.correct_answer
                              ? 'bg-emerald-500/15 border border-emerald-500/30 text-emerald-400'
                              : 'bg-dark-700/50 border border-dark-700 text-dark-300'
                          }`}>
                            {opt === q.correct_answer && <span className="mr-1">✓</span>}
                            {opt}
                          </div>
                        ))}
                      </div>
                    )}
                    {q.type !== 'mcq' && q.correct_answer && (
                      <div className="mt-3 p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg">
                        <p className="text-xs text-emerald-500 font-medium mb-1">Expected Answer:</p>
                        <p className="text-sm text-dark-300">{q.correct_answer}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Chart data
  const distributionData = Object.entries(analytics.score_distribution || {}).map(([range, count]) => ({
    range, count,
  }));

  const topicData = (analytics.topic_analysis || []).map((t) => ({
    topic: t.topic,
    percentage: t.average_percentage,
  }));

  // Dynamic height to prevent long labels from overlapping vertically
  const chartHeight = Math.max(250, topicData.length * 60);

  const statCards = [
    { label: 'Students', value: analytics.total_students, icon: '👥', color: 'from-blue-500 to-cyan-500' },
    { label: 'Average', value: `${analytics.average_score}%`, icon: '📊', color: 'from-indigo-500 to-purple-500' },
    { label: 'Highest', value: `${analytics.highest_score}%`, icon: '🏆', color: 'from-emerald-500 to-teal-500' },
    { label: 'Pass Rate', value: `${analytics.pass_rate}%`, icon: '✅', color: 'from-amber-500 to-orange-500' },
  ];

  return (
    <div className="min-h-screen bg-dark-950">
      <Navbar />
      <div className="max-w-7xl mx-auto px-6 py-8">
        <h1 className="text-3xl font-bold text-white mb-1 animate-fade-in">📊 Analytics Dashboard</h1>
        <p className="text-dark-400 mb-8">{analytics.exam_title} • Code: {analytics.exam_code}</p>

        {/* Stat Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {statCards.map((stat, i) => (
            <div key={i} className="glass-card p-5 animate-slide-up" style={{ animationDelay: `${i * 100}ms` }}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-dark-400 text-sm">{stat.label}</p>
                  <p className="text-2xl font-bold text-white mt-1">{stat.value}</p>
                </div>
                <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${stat.color} flex items-center justify-center`}>
                  <span className="text-xl">{stat.icon}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Score Distribution */}
          <div className="glass-card p-6">
            <h3 className="text-lg font-bold text-white mb-4">Score Distribution</h3>
            <ResponsiveContainer width="100%" height={chartHeight}>
              <BarChart data={distributionData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="range" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', color: '#f1f5f9' }} />
                <Bar dataKey="count" fill="#6366f1" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Topic Analysis */}
          <div className="glass-card p-6">
            <h3 className="text-lg font-bold text-white mb-4">Topic Performance</h3>
            <ResponsiveContainer width="100%" height={chartHeight}>
              <BarChart data={topicData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis type="number" domain={[0, 100]} stroke="#94a3b8" fontSize={12} />
                <YAxis dataKey="topic" type="category" stroke="#94a3b8" width={180} tick={<CustomYAxisTick />} />
                <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', color: '#f1f5f9' }} />
                <Bar dataKey="percentage" fill="#8b5cf6" radius={[0, 8, 8, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Student Rankings */}
        <div className="glass-card p-6">
          <h3 className="text-lg font-bold text-white mb-4">🏆 Student Rankings</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-dark-700">
                  <th className="text-left py-3 px-4 text-dark-400 text-sm font-medium">Rank</th>
                  <th className="text-left py-3 px-4 text-dark-400 text-sm font-medium">Student</th>
                  <th className="text-left py-3 px-4 text-dark-400 text-sm font-medium">Score</th>
                  <th className="text-left py-3 px-4 text-dark-400 text-sm font-medium">Percentage</th>
                  <th className="text-left py-3 px-4 text-dark-400 text-sm font-medium">Grade</th>
                  <th className="text-left py-3 px-4 text-dark-400 text-sm font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {(analytics.rankings || []).map((student, i) => {
                  const pct = student.percentage;
                  const grade = pct >= 90 ? 'A+' : pct >= 80 ? 'A' : pct >= 70 ? 'B' : pct >= 60 ? 'C' : pct >= 40 ? 'D' : 'F';
                  return (
                    <tr key={i} className="border-b border-dark-800 hover:bg-dark-800/50 transition-colors">
                      <td className="py-3 px-4">
                        <span className={`w-7 h-7 rounded-full inline-flex items-center justify-center text-xs font-bold ${
                          i === 0 ? 'bg-amber-500/20 text-amber-400' : i === 1 ? 'bg-gray-400/20 text-gray-300' : i === 2 ? 'bg-orange-500/20 text-orange-400' : 'bg-dark-700 text-dark-400'
                        }`}>
                          {i + 1}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <p className="text-white font-medium">{student.student_name}</p>
                        {student.student_email && (
                          <p className="text-xs text-dark-400">{student.student_email}</p>
                        )}
                      </td>
                      <td className="py-3 px-4 text-dark-300">{student.score}/{student.max_score}</td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <div className="w-24 h-2 bg-dark-700 rounded-full overflow-hidden">
                            <div className="h-full rounded-full bg-primary-500" style={{ width: `${pct}%` }} />
                          </div>
                          <span className="text-sm text-dark-300">{pct}%</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                          grade === 'F' ? 'bg-red-500/20 text-red-400' :
                          grade === 'D' ? 'bg-orange-500/20 text-orange-400' :
                          'bg-emerald-500/20 text-emerald-400'
                        }`}>{grade}</span>
                      </td>
                      <td className="py-3 px-4">
                        {student.tab_switch_auto_submitted ? (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-red-500/15 border border-red-500/25" title="Exam was auto-submitted due to tab switch violations">
                            <span className="text-base">🚩</span>
                            <span className="text-xs font-semibold text-red-400">Tab Switch</span>
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-emerald-500/15 border border-emerald-500/25">
                            <span className="text-xs">✓</span>
                            <span className="text-xs font-semibold text-emerald-400">Clean</span>
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Suspicious Activity */}
        {analytics.suspicious_students > 0 && (
          <div className="glass-card p-6 mt-6 border-red-500/20">
            <h3 className="text-lg font-bold text-red-400 mb-2">⚠️ Anti-Cheat Alerts</h3>
            <p className="text-dark-300">{analytics.suspicious_students} student(s) flagged for suspicious behavior</p>
          </div>
        )}

        {/* Exam Questions */}
        {exam && exam.questions && exam.questions.length > 0 && (
          <div className="glass-card p-6 mt-6">
            <h3 className="text-lg font-bold text-white mb-4">📝 Exam Questions ({exam.questions.length})</h3>
            <div className="space-y-4">
              {exam.questions.map((q, i) => (
                <div key={q.id || i} className="p-4 bg-dark-800/50 rounded-xl border border-dark-700">
                  <div className="flex items-start justify-between gap-4 mb-2">
                    <p className="text-white font-medium">
                      <span className="text-dark-500 mr-2">Q{i + 1}.</span>
                      {q.question}
                    </p>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                        q.type === 'mcq' ? 'bg-blue-500/20 text-blue-400' :
                        q.type === 'short' ? 'bg-amber-500/20 text-amber-400' :
                        'bg-purple-500/20 text-purple-400'
                      }`}>
                        {q.type === 'mcq' ? 'MCQ' : q.type === 'short' ? 'Short' : 'Long'}
                      </span>
                      <span className="px-2 py-0.5 rounded text-xs font-medium bg-dark-700 text-dark-300">
                        {q.marks} {q.marks === 1 ? 'mark' : 'marks'}
                      </span>
                    </div>
                  </div>
                  {q.difficulty && (
                    <p className="text-xs text-dark-500 mb-2">Difficulty: <span className={`font-medium ${
                      q.difficulty === 'easy' ? 'text-emerald-400' : q.difficulty === 'medium' ? 'text-amber-400' : 'text-red-400'
                    }`}>{q.difficulty}</span></p>
                  )}
                  {q.type === 'mcq' && q.options && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-3">
                      {q.options.map((opt, j) => (
                        <div key={j} className={`px-3 py-2 rounded-lg text-sm ${
                          opt === q.correct_answer
                            ? 'bg-emerald-500/15 border border-emerald-500/30 text-emerald-400'
                            : 'bg-dark-700/50 border border-dark-700 text-dark-300'
                        }`}>
                          {opt === q.correct_answer && <span className="mr-1">✓</span>}
                          {opt}
                        </div>
                      ))}
                    </div>
                  )}
                  {q.type !== 'mcq' && q.correct_answer && (
                    <div className="mt-3 p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg">
                      <p className="text-xs text-emerald-500 font-medium mb-1">Expected Answer:</p>
                      <p className="text-sm text-dark-300">{q.correct_answer}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
