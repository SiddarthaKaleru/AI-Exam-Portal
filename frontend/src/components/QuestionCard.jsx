export default function QuestionCard({ question, answer, onAnswer, index }) {
  const difficultyColors = {
    easy: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    medium: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    hard: 'bg-red-500/20 text-red-400 border-red-500/30',
  };

  return (
    <div className="glass-card p-6 animate-fade-in" id={`question-${question.id}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className="w-8 h-8 rounded-lg bg-primary-500/20 flex items-center justify-center text-primary-400 font-bold text-sm">
            {index + 1}
          </span>
          <span className={`px-2.5 py-1 rounded-lg text-xs font-medium border ${difficultyColors[question.difficulty] || difficultyColors.medium}`}>
            {question.difficulty?.toUpperCase()}
          </span>
          <span className="px-2.5 py-1 rounded-lg text-xs font-medium bg-dark-700 text-dark-300 border border-dark-600">
            {question.type?.toUpperCase()}
          </span>
        </div>
        <span className="text-sm text-dark-400">{question.marks} mark{question.marks > 1 ? 's' : ''}</span>
      </div>

      {/* Question Text */}
      <p className="text-white text-base mb-4 leading-relaxed">{question.question}</p>

      {/* Answer Input */}
      {question.type === 'mcq' ? (
        <div className="space-y-2">
          {question.options?.map((option, i) => (
            <label
              key={i}
              className={`flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-all border ${
                answer === option
                  ? 'bg-primary-500/20 border-primary-500/50 text-white'
                  : 'bg-dark-800/50 border-dark-600 hover:border-dark-500 text-dark-300 hover:text-white'
              }`}
            >
              <input
                type="radio"
                name={`q-${question.id}`}
                value={option}
                checked={answer === option}
                onChange={() => onAnswer(question.id, option)}
                className="sr-only"
              />
              <span className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-all ${
                answer === option ? 'border-primary-500 bg-primary-500' : 'border-dark-500'
              }`}>
                {answer === option && (
                  <span className="w-2 h-2 rounded-full bg-white" />
                )}
              </span>
              <span className="text-sm">{option}</span>
            </label>
          ))}
        </div>
      ) : (
        <textarea
          value={answer || ''}
          onChange={(e) => onAnswer(question.id, e.target.value)}
          onPaste={(e) => {
            e.preventDefault();
            alert("Pasting answers is disabled for this exam.");
          }}
          rows={question.type === 'long' ? 8 : 4}
          placeholder={question.type === 'short' ? 'Write your answer in 2-4 sentences...' : 'Write your detailed answer here...'}
          className="input-field resize-none"
        />
      )}
    </div>
  );
}
