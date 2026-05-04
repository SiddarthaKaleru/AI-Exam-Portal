import { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchExam, startExam, submitExam, reportAntiCheat } from '../services/api';
import Timer from '../components/Timer';
import QuestionCard from '../components/QuestionCard';

export default function ExamPortal() {
  const { code } = useParams();
  const navigate = useNavigate();
  const [exam, setExam] = useState(null);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');
  const [currentQ, setCurrentQ] = useState(0);
  const [tabSwitchCount, setTabSwitchCount] = useState(0);
  const antiCheatEvents = useRef([]);
  const answersRef = useRef({});
  const handleSubmitRef = useRef();

  // Load exam
  useEffect(() => {
    loadExam();
  }, [code]);

  const loadExam = async () => {
    try {
      const { data } = await fetchExam(code);
      setExam(data.exam);
      await startExam(code);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load exam');
    } finally {
      setLoading(false);
    }
  };

  // Anti-cheat: tab switching detection
  useEffect(() => {
    const handleVisibility = () => {
      if (document.hidden) {
        antiCheatEvents.current.push({ type: 'tab_switch', timestamp: new Date().toISOString() });
        reportAntiCheat(code, [{ type: 'tab_switch', timestamp: new Date().toISOString() }]).catch(() => {});
        
        setTabSwitchCount(prev => {
          const newCount = prev + 1;
          if (newCount >= 3) {
            alert('Maximum tab switches exceeded. Your exam will be auto-submitted.');
            // We use a timeout to let state update before triggering submit
            setTimeout(() => {
              handleSubmitRef.current({ autoSubmittedByTabSwitch: true });
            }, 100);
          } else {
            alert(`Warning! Tab switching is not allowed. Strike ${newCount}/2.\nIf you switch tabs 3 times, your exam will be auto-submitted.`);
          }
          return newCount;
        });
      }
    };

    const handleCopy = (e) => {
      e.preventDefault();
      antiCheatEvents.current.push({ type: 'copy_paste', timestamp: new Date().toISOString() });
      reportAntiCheat(code, [{ type: 'copy_paste', timestamp: new Date().toISOString() }]).catch(() => {});
    };

    const handleContextMenu = (e) => {
      e.preventDefault();
      antiCheatEvents.current.push({ type: 'right_click', timestamp: new Date().toISOString() });
    };

    document.addEventListener('visibilitychange', handleVisibility);
    document.addEventListener('copy', handleCopy);
    document.addEventListener('contextmenu', handleContextMenu);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibility);
      document.removeEventListener('copy', handleCopy);
      document.removeEventListener('contextmenu', handleContextMenu);
    };
  }, [code]);

  const handleAnswer = useCallback((questionId, answer) => {
    setAnswers((prev) => {
      const updated = { ...prev, [questionId]: answer };
      answersRef.current = updated;
      return updated;
    });
  }, []);

  const handleSubmit = async (options = {}) => {
    if (submitting || submitted) return;
    setSubmitting(true);

    try {
      const formattedAnswers = Object.entries(answersRef.current).map(([qid, answer]) => ({
        question_id: qid, // Ensure it remains a string (UUID)
        answer,
      }));
      await submitExam(code, formattedAnswers, options.autoSubmittedByTabSwitch || false);
      setSubmitted(true);
      setTimeout(() => navigate(`/result/${code}`), 1500);
    } catch (err) {
      setError(err.response?.data?.detail || 'Submission failed');
      setSubmitting(false);
    }
  };

  // Keep the submit ref in sync so the event listener always calls the latest version
  handleSubmitRef.current = handleSubmit;

  const handleTimeUp = () => {
    handleSubmit();
  };

  if (loading) {
    return (
      <div className="min-h-screen gradient-bg flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-12 w-12 border-3 border-primary-500 border-t-transparent rounded-full mx-auto" />
          <p className="text-dark-400 mt-4">Loading exam...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen gradient-bg flex items-center justify-center">
        <div className="glass-card p-8 text-center max-w-md">
          <span className="text-5xl block mb-4">⚠️</span>
          <h2 className="text-xl font-bold text-white mb-2">Error</h2>
          <p className="text-dark-400 mb-4">{error}</p>
          <button onClick={() => navigate('/student')} className="btn-primary">Go Back</button>
        </div>
      </div>
    );
  }

  if (submitted) {
    return (
      <div className="min-h-screen gradient-bg flex items-center justify-center">
        <div className="glass-card p-8 text-center animate-slide-up">
          <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-emerald-500/20 flex items-center justify-center">
            <span className="text-5xl">✅</span>
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Exam Submitted!</h2>
          <p className="text-dark-400">Redirecting to results...</p>
        </div>
      </div>
    );
  }

  const questions = exam?.questions || [];
  const answeredCount = Object.keys(answers).length;

  return (
    <div className="min-h-screen bg-dark-950">
      {/* Sticky Header */}
      <div className="glass sticky top-0 z-50 px-6 py-3">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold text-white">{exam?.title}</h1>
            <p className="text-xs text-dark-400">{answeredCount}/{questions.length} answered</p>
          </div>
          <div className="flex items-center gap-4">
            <Timer durationMinutes={exam?.duration_minutes ?? 30} onTimeUp={handleTimeUp} />
            <button onClick={handleSubmit} disabled={submitting}
              className="btn-primary text-sm px-4 py-2" id="submit-exam-btn">
              {submitting ? '⏳ Submitting...' : '📤 Submit'}
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-6 flex gap-6">
        {/* Question Navigation */}
        <div className="hidden lg:block w-48 shrink-0">
          <div className="glass-card p-4 sticky top-24">
            <p className="text-sm font-medium text-dark-300 mb-3">Questions</p>
            <div className="grid grid-cols-5 gap-2">
              {questions.map((q, i) => (
                <button key={q.id} onClick={() => setCurrentQ(i)}
                  className={`w-8 h-8 rounded-lg text-xs font-bold transition-all ${
                    currentQ === i ? 'bg-primary-500 text-white shadow-lg' :
                    answers[q.id] ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                    'bg-dark-700 text-dark-400 hover:bg-dark-600'
                  }`}>
                  {i + 1}
                </button>
              ))}
            </div>
            <div className="mt-4 space-y-1 text-xs text-dark-400">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded bg-emerald-500/20 border border-emerald-500/30" /> Answered
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded bg-primary-500" /> Current
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded bg-dark-700" /> Unanswered
              </div>
            </div>
          </div>
        </div>

        {/* Questions */}
        <div className="flex-1 space-y-4">
          {questions.map((q, i) => (
            <div key={q.id} className={currentQ === i ? '' : 'hidden lg:block'}>
              <QuestionCard
                question={q}
                answer={answers[q.id]}
                onAnswer={handleAnswer}
                index={i}
              />
            </div>
          ))}

          {/* Mobile: Prev/Next */}
          <div className="flex gap-3 lg:hidden">
            <button onClick={() => setCurrentQ(Math.max(0, currentQ - 1))}
              disabled={currentQ === 0} className="btn-secondary flex-1">← Previous</button>
            <button onClick={() => setCurrentQ(Math.min(questions.length - 1, currentQ + 1))}
              disabled={currentQ === questions.length - 1} className="btn-primary flex-1">Next →</button>
          </div>
        </div>
      </div>
    </div>
  );
}
