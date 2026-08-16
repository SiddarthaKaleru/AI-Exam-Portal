import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadPDF, createExam } from '../services/api';
import Navbar from '../components/Navbar';

const MAX_PDFS = 5;

export default function CreateExam() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [files, setFiles] = useState([]);
  const [uploadedFilenames, setUploadedFilenames] = useState([]);
  const [form, setForm] = useState({
    subject: '', topic: '', syllabus: '',
    duration_minutes: 30, num_mcq: 5, num_short: 3, num_long: 2,
    marks_mcq: 1, marks_short: 3, marks_long: 5
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const handleFileSelect = (e) => {
    const selected = Array.from(e.target.files);
    const total = files.length + selected.length;
    if (total > MAX_PDFS) {
      setError(`You can upload a maximum of ${MAX_PDFS} PDFs. You already have ${files.length} selected.`);
      return;
    }
    setError('');
    setFiles((prev) => [...prev, ...selected]);
    // Reset input so the same file can be re-selected if removed
    e.target.value = '';
  };

  const removeFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) return setError('Please select at least one PDF file');
    setError('');
    setLoading(true);
    try {
      const { data } = await uploadPDF(files);
      setUploadedFilenames(data.filenames);
      setStep(2);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!form.subject || !form.topic) return setError('Subject and topic are required');
    if (parseInt(form.duration_minutes) <= 0) return setError('Exam duration must be at least 1 minute');
    setError('');
    setLoading(true);
    try {
      const payload = {
        ...form,
        pdf_filenames: uploadedFilenames
      };

      const { data } = await createExam(payload);
      setResult(data);
      setStep(4);
    } catch (err) {
      setError(err.response?.data?.detail || 'Exam creation failed');
    } finally {
      setLoading(false);
    }
  };

  const steps = [
    { num: 1, label: 'Upload PDFs' },
    { num: 2, label: 'Details' },
    { num: 3, label: 'Configure' },
    { num: 4, label: 'Complete' },
  ];

  return (
    <div className="min-h-screen bg-dark-950">
      <Navbar />
      <div className="max-w-3xl mx-auto px-6 py-8">
        <h1 className="text-3xl font-bold text-white mb-2 animate-fade-in">Create New Exam</h1>
        <p className="text-dark-400 mb-8">Upload your notes and let AI generate the exam</p>

        {/* Progress Steps */}
        <div className="flex items-center gap-2 mb-8">
          {steps.map((s) => (
            <div key={s.num} className="flex items-center gap-2 flex-1">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all ${
                step >= s.num ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/30' : 'bg-dark-700 text-dark-400'
              }`}>
                {step > s.num ? '✓' : s.num}
              </div>
              <span className={`text-sm hidden sm:block ${step >= s.num ? 'text-white' : 'text-dark-500'}`}>{s.label}</span>
              {s.num < 4 && <div className={`flex-1 h-0.5 rounded ${step > s.num ? 'bg-primary-500' : 'bg-dark-700'}`} />}
            </div>
          ))}
        </div>

        {error && (
          <div className="mb-6 p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm">{error}</div>
        )}

        {/* Step 1: Upload PDFs */}
        {step === 1 && (
          <div className="glass-card p-8 animate-slide-up">
            <div className="text-center">
              <div className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 border-2 border-dashed border-primary-500/30 flex items-center justify-center">
                <span className="text-4xl">📄</span>
              </div>
              <h2 className="text-xl font-bold text-white mb-2">Upload Notes PDFs</h2>
              <p className="text-dark-400 mb-6">Upload up to {MAX_PDFS} PDF files from which questions will be generated</p>
              <input type="file" accept=".pdf" multiple onChange={handleFileSelect}
                className="hidden" id="pdf-upload" />
              <label htmlFor="pdf-upload"
                className={`btn-secondary inline-block cursor-pointer mb-4 ${files.length >= MAX_PDFS ? 'opacity-50 pointer-events-none' : ''}`}>
                📁 Choose PDF Files ({files.length}/{MAX_PDFS})
              </label>
            </div>

            {/* Selected Files List */}
            {files.length > 0 && (
              <div className="mt-4 space-y-2">
                {files.map((f, i) => (
                  <div key={i} className="flex items-center justify-between p-3 bg-dark-800/50 rounded-xl border border-dark-700">
                    <div className="flex items-center gap-3 min-w-0">
                      <span className="text-lg flex-shrink-0">📎</span>
                      <span className="text-sm text-dark-300 truncate">{f.name}</span>
                      <span className="text-xs text-dark-500 flex-shrink-0">({(f.size / 1024).toFixed(0)} KB)</span>
                    </div>
                    <button onClick={() => removeFile(i)}
                      className="text-red-400 hover:text-red-300 text-sm font-medium ml-3 flex-shrink-0 transition-colors">
                      ✕ Remove
                    </button>
                  </div>
                ))}
                <div className="mt-4 text-center">
                  <button onClick={handleUpload} disabled={loading} className="btn-primary" id="upload-btn">
                    {loading ? '⏳ Uploading...' : `🚀 Upload ${files.length} PDF${files.length > 1 ? 's' : ''}`}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Step 2: Exam Details */}
        {step === 2 && (
          <div className="glass-card p-8 animate-slide-up space-y-4">
            <h2 className="text-xl font-bold text-white mb-4">Exam Details</h2>
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-1.5">Subject *</label>
              <input type="text" value={form.subject} onChange={(e) => setForm({ ...form, subject: e.target.value })}
                className="input-field" placeholder="e.g., Computer Science" id="exam-subject" />
            </div>
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-1.5">Topic *</label>
              <input type="text" value={form.topic} onChange={(e) => setForm({ ...form, topic: e.target.value })}
                className="input-field" placeholder="e.g., Data Structures" id="exam-topic" />
            </div>
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-1.5">Syllabus (optional)</label>
              <textarea value={form.syllabus} onChange={(e) => setForm({ ...form, syllabus: e.target.value })}
                className="input-field resize-none" rows={3} placeholder="Key topics to cover..." />
            </div>
            <button onClick={() => setStep(3)} className="btn-primary w-full">Next → Configure</button>
          </div>
        )}

        {/* Step 3: Configuration */}
        {step === 3 && (
          <div className="glass-card p-8 animate-slide-up space-y-4">
            <h2 className="text-xl font-bold text-white mb-4">Exam Configuration</h2>
            {(() => {
              const handleNumberChange = (field, value) => {
                setForm({ ...form, [field]: value === '' ? '' : value });
              };
              const handleNumberBlur = (field, fallback) => {
                const parsed = parseInt(form[field]);
                setForm(prev => ({ ...prev, [field]: isNaN(parsed) || parsed < 0 ? fallback : parsed }));
              };
              return (
              <>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-dark-300 mb-1.5">Duration (minutes)</label>
                <input type="number" value={form.duration_minutes} onChange={(e) => handleNumberChange('duration_minutes', e.target.value)}
                  onBlur={() => handleNumberBlur('duration_minutes', 30)}
                  className="input-field" min={5} max={180} id="exam-duration" />
              </div>
              <div>
                <label className="block text-sm font-medium text-dark-300 mb-1.5">MCQ Count</label>
                <input type="number" value={form.num_mcq} onChange={(e) => handleNumberChange('num_mcq', e.target.value)}
                  onBlur={() => handleNumberBlur('num_mcq', 0)}
                  className="input-field" min={0} max={20} id="exam-mcq" />
              </div>
              <div>
                <label className="block text-sm font-medium text-dark-300 mb-1.5">Marks per MCQ</label>
                <input type="number" value={form.marks_mcq} onChange={(e) => handleNumberChange('marks_mcq', e.target.value)}
                  onBlur={() => handleNumberBlur('marks_mcq', 1)}
                  className="input-field" min={1} max={10} id="exam-marks-mcq" />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-dark-300 mb-1.5">Short Answer Count</label>
                <input type="number" value={form.num_short} onChange={(e) => handleNumberChange('num_short', e.target.value)}
                  onBlur={() => handleNumberBlur('num_short', 0)}
                  className="input-field" min={0} max={10} id="exam-short" />
              </div>
              <div>
                <label className="block text-sm font-medium text-dark-300 mb-1.5">Marks per Short Answer</label>
                <input type="number" value={form.marks_short} onChange={(e) => handleNumberChange('marks_short', e.target.value)}
                  onBlur={() => handleNumberBlur('marks_short', 3)}
                  className="input-field" min={1} max={20} id="exam-marks-short" />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-dark-300 mb-1.5">Long Answer Count</label>
                <input type="number" value={form.num_long} onChange={(e) => handleNumberChange('num_long', e.target.value)}
                  onBlur={() => handleNumberBlur('num_long', 0)}
                  className="input-field" min={0} max={10} id="exam-long" />
              </div>
              <div>
                <label className="block text-sm font-medium text-dark-300 mb-1.5">Marks per Long Answer</label>
                <input type="number" value={form.marks_long} onChange={(e) => handleNumberChange('marks_long', e.target.value)}
                  onBlur={() => handleNumberBlur('marks_long', 5)}
                  className="input-field" min={1} max={50} id="exam-marks-long" />
              </div>
            </div>
              </>
              );
            })()}
            <div className="glass p-4 rounded-xl mt-4">
              <p className="text-sm text-dark-300">
                📊 Total: <span className="text-white font-bold">{(parseInt(form.num_mcq) || 0) + (parseInt(form.num_short) || 0) + (parseInt(form.num_long) || 0)}</span> questions •
                ⏱️ Duration: <span className="text-white font-bold">{parseInt(form.duration_minutes) || 0}</span> minutes •
                📄 PDFs: <span className="text-white font-bold">{uploadedFilenames.length}</span> uploaded
              </p>
            </div>
            <div className="flex gap-3">
              <button onClick={() => setStep(2)} className="btn-secondary flex-1">← Back</button>
              <button onClick={handleCreate} disabled={loading} className="btn-primary flex-1" id="generate-btn">
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                    🤖 AI Generating...
                  </span>
                ) : '🚀 Generate Exam'}
              </button>
            </div>
          </div>
        )}

        {/* Step 4: Complete */}
        {step === 4 && result && (
          <div className="glass-card p-8 animate-slide-up text-center">
            <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-emerald-500/20 flex items-center justify-center animate-glow">
              <span className="text-4xl">🎉</span>
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">Exam Created Successfully!</h2>
            <p className="text-dark-400 mb-6">{result.total_questions} questions generated by AI</p>
            <div className="glass p-6 rounded-xl mb-6 inline-block">
              <p className="text-sm text-dark-400 mb-1">Exam Code</p>
              <p className="text-4xl font-mono font-bold gradient-text tracking-wider">{result.exam_code}</p>
              <p className="text-xs text-dark-500 mt-2">Share this code with students</p>
            </div>
            <div className="flex gap-3 justify-center">
              <button onClick={() => navigator.clipboard.writeText(result.exam_code)}
                className="btn-secondary">📋 Copy Code</button>
              <button onClick={() => navigate('/admin')} className="btn-primary">← Dashboard</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
