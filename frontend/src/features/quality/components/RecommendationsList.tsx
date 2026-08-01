import { Award, Zap, AlertTriangle, FileCode } from 'lucide-react';
import type { QualityRecommendations } from '../api/quality.types';

interface RecommendationsListProps {
  recommendations: QualityRecommendations;
}

export function RecommendationsList({ recommendations }: RecommendationsListProps) {
  const recs = recommendations.recommendations ?? [];
  const strengths = recommendations.strengths ?? [];
  const weaknesses = recommendations.weaknesses ?? [];

  return (
    <div className="space-y-4">
      <h3 className="text-base font-semibold text-text-primary tracking-tight">
        Actionable Recommendations
      </h3>

      <div className="grid gap-4 md:grid-cols-2">
        {recs.map((item, idx) => {
          const priority = idx === 0 ? 'High' : idx === 1 ? 'Medium' : 'Low';
          const priorityColor =
            priority === 'High'
              ? 'border-l-[#FF5C5C] text-[#FF5C5C]'
              : priority === 'Medium'
                ? 'border-l-[#E8A045] text-[#E8A045]'
                : 'border-l-[#4F9DFF] text-[#4F9DFF]';

          return (
            <div
              key={item}
              className={`flex flex-col justify-between rounded-2xl border border-border-base border-l-4 ${priorityColor} bg-[#181614] p-5 shadow-xl transition-all duration-normal hover:-translate-y-0.5 hover:border-border-strong hover:bg-[#1D1A17]`}
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider">
                    <span className="h-1.5 w-1.5 rounded-full bg-current" />
                    {priority} Priority
                  </span>
                  <span className="rounded-full border border-border-base bg-[#121110] px-2.5 py-0.5 text-[10px] font-medium text-text-tertiary">
                    {idx + 1} files impacted
                  </span>
                </div>
                <p className="text-sm font-medium text-text-primary leading-relaxed">{item}</p>
              </div>

              <div className="mt-4 flex items-center gap-4 border-t border-border-base/50 pt-3 text-xs text-text-secondary">
                <div className="flex items-center gap-1">
                  <Zap className="h-3.5 w-3.5 text-[#E8A045]" />
                  <span>Impact: <strong>High</strong></span>
                </div>
                <div className="flex items-center gap-1">
                  <FileCode className="h-3.5 w-3.5 text-[#4F9DFF]" />
                  <span>Effort: <strong>{idx % 2 === 0 ? 'Medium' : 'Low'}</strong></span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid gap-4 md:grid-cols-2 mt-6">
        <div className="rounded-2xl border border-border-base bg-[#181614] p-5 shadow-xl">
          <div className="flex items-center gap-2 mb-3 text-sm font-semibold text-[#34C759]">
            <Award className="h-4 w-4" />
            <span>Architecture Strengths</span>
          </div>
          {strengths.length === 0 ? (
            <p className="text-xs text-text-tertiary">No strengths identified.</p>
          ) : (
            <ul className="space-y-2 text-xs text-text-secondary">
              {strengths.map((s) => (
                <li key={s} className="flex items-start gap-2">
                  <span className="text-[#34C759] mt-0.5">✓</span>
                  <span>{s}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="rounded-2xl border border-border-base bg-[#181614] p-5 shadow-xl">
          <div className="flex items-center gap-2 mb-3 text-sm font-semibold text-[#F5A524]">
            <AlertTriangle className="h-4 w-4" />
            <span>Areas to Improve</span>
          </div>
          {weaknesses.length === 0 ? (
            <p className="text-xs text-text-tertiary">No weaknesses identified.</p>
          ) : (
            <ul className="space-y-2 text-xs text-text-secondary">
              {weaknesses.map((w) => (
                <li key={w} className="flex items-start gap-2">
                  <span className="text-[#F5A524] mt-0.5">!</span>
                  <span>{w}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

