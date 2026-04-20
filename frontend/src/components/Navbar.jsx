import { Link, useNavigate } from 'react-router-dom';

export default function Navbar() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const token = localStorage.getItem('token');

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  if (!token) return null;

  return (
    <nav className="glass sticky top-0 z-50 px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Logo */}
        <Link to={user.role === 'admin' ? '/admin' : '/student'} className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30 group-hover:shadow-indigo-500/50 transition-all">
            <span className="text-white font-bold text-lg">🎓</span>
          </div>
          <span className="text-xl font-bold gradient-text">AI Exam Portal</span>
        </Link>

        {/* Navigation */}
        <div className="flex items-center gap-6">
          {user.role === 'admin' && (
            <>
              <Link to="/admin" className="text-dark-300 hover:text-white transition-colors font-medium">
                Dashboard
              </Link>
              <Link to="/create-exam" className="text-dark-300 hover:text-white transition-colors font-medium">
                Create Exam
              </Link>
            </>
          )}

          {/* User Info */}
          <div className="flex items-center gap-3 ml-4 pl-4 border-l border-dark-600">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center">
              <span className="text-white text-sm font-bold">
                {(user.name || user.email || '?')[0].toUpperCase()}
              </span>
            </div>
            <div className="hidden sm:block">
              <p className="text-sm font-medium text-white">{user.name || user.email}</p>
              <p className="text-xs text-dark-400 capitalize">{user.role}</p>
            </div>
            <button
              onClick={handleLogout}
              className="ml-2 px-3 py-1.5 text-sm text-dark-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
