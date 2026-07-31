export function RiskRing({ score }: { score: number }) {
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;
  
  const getColor = (s: number) => {
    if (s >= 90) return "text-ds-success";
    if (s >= 70) return "text-text-primary";
    return "text-ds-danger";
  };

  return (
    <div className="relative flex items-center justify-center w-40 h-40">
      {/* Background Ring */}
      <svg className="absolute inset-0 w-full h-full transform -rotate-90">
        <circle
          cx="80"
          cy="80"
          r={radius}
          fill="transparent"
          stroke="currentColor"
          strokeWidth="8"
          className="text-ds-border"
        />
        {/* Progress Ring */}
        <circle
          cx="80"
          cy="80"
          r={radius}
          fill="transparent"
          stroke="currentColor"
          strokeWidth="8"
          strokeLinecap="round"
          className={`${getColor(score)} transition-all duration-1000 ease-out`}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
        />
      </svg>
      <div className="flex flex-col items-center justify-center z-10">
        <span className="text-4xl font-medium text-white tracking-tighter">{score}</span>
        <span className="text-[10px] uppercase tracking-wider text-text-muted mt-1 font-semibold">Score</span>
      </div>
    </div>
  );
}
