import { useState, useEffect } from 'react';

export default function Timer({ durationMinutes, onTimeUp }) {
  const [timeLeft, setTimeLeft] = useState(durationMinutes * 60);

  useEffect(() => {
    if (timeLeft <= 0) {
      onTimeUp?.();
      return;
    }

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          onTimeUp?.();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;
  const percentage = durationMinutes > 0 ? (timeLeft / (durationMinutes * 60)) * 100 : 0;

  const isWarning = timeLeft < 300; // less than 5 min
  const isDanger = timeLeft < 60;   // less than 1 min

  return (
    <div className={`flex items-center gap-3 px-4 py-2 rounded-xl border transition-all ${
      isDanger ? 'bg-red-500/20 border-red-500/50 animate-pulse' :
      isWarning ? 'bg-amber-500/20 border-amber-500/50' :
      'bg-dark-800/80 border-dark-600'
    }`}>
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="12" cy="12" r="10" className={isDanger ? 'text-red-400' : isWarning ? 'text-amber-400' : 'text-primary-400'} />
        <path d="M12 6v6l4 2" className={isDanger ? 'text-red-400' : isWarning ? 'text-amber-400' : 'text-primary-400'} />
      </svg>
      <span className={`font-mono text-lg font-bold ${
        isDanger ? 'text-red-400' : isWarning ? 'text-amber-400' : 'text-white'
      }`}>
        {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
      </span>
      {/* Progress bar */}
      <div className="w-20 h-1.5 bg-dark-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-1000 ${
            isDanger ? 'bg-red-500' : isWarning ? 'bg-amber-500' : 'bg-primary-500'
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
