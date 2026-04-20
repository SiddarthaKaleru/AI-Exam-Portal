import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { register } from '../services/api';

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', email: '', password: '', role: 'student', adminSecret: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const { data } = await register(form);
      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));
      navigate(data.user.role === 'admin' ? '/admin' : '/student');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen gradient-bg flex items-center justify-center p-4">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/3 right-1/3 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-1/3 left-1/3 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }} />
      </div>

      <div className="glass-card p-8 w-full max-w-md animate-slide-up relative z-10">
        <div className="text-center mb-8">
          <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-purple-500/30">
            <span className="text-3xl">✨</span>
          </div>
          <h1 className="text-3xl font-bold gradient-text">Create Account</h1>
          <p className="text-dark-400 mt-2">Join the AI Exam Portal</p>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-dark-300 mb-1.5">Full Name</label>
            <input type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="input-field" placeholder="John Doe" required id="register-name" />
          </div>
          <div>
            <label className="block text-sm font-medium text-dark-300 mb-1.5">Email</label>
            <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}
              className="input-field" placeholder="you@example.com" required id="register-email" />
          </div>
          <div>
            <label className="block text-sm font-medium text-dark-300 mb-1.5">Password</label>
            <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })}
              className="input-field" placeholder="••••••••" required id="register-password" />
          </div>
          <div>
            <label className="block text-sm font-medium text-dark-300 mb-1.5">Role</label>
            <div className="grid grid-cols-2 gap-3">
              {['student', 'admin'].map((role) => (
                <button key={role} type="button"
                  onClick={() => setForm({ ...form, role })}
                  className={`p-3 rounded-xl border text-sm font-medium transition-all ${
                    form.role === role
                      ? 'bg-primary-500/20 border-primary-500/50 text-primary-400'
                      : 'bg-dark-800/50 border-dark-600 text-dark-400 hover:border-dark-500'
                  }`}
                  id={`register-role-${role}`}
                >
                  {role === 'student' ? '🎓 Student' : '👑 Admin'}
                </button>
              ))}
            </div>
          </div>
          {form.role === 'admin' && (
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-1.5">Admin Secret Key</label>
              <input type="password" value={form.adminSecret} onChange={(e) => setForm({ ...form, adminSecret: e.target.value })}
                className="input-field" placeholder="Enter admin secret key" required id="register-admin-secret" />
            </div>
          )}
          <button type="submit" disabled={loading} className="btn-primary w-full" id="register-submit">
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <p className="text-center text-dark-400 mt-6 text-sm">
          Already have an account?{' '}
          <Link to="/login" className="text-primary-400 hover:text-primary-300 font-medium transition-colors">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
