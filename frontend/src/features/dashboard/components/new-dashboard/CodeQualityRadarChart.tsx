import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, Tooltip } from 'recharts';

interface QualityScores {
  architecture?: number;
  security?: number;
  documentation?: number;
  maintainability?: number;
  testing?: number;
  performance?: number;
}

interface CodeQualityRadarChartProps {
  scores?: QualityScores;
  loading?: boolean;
}

export function CodeQualityRadarChart({ scores, loading = false }: CodeQualityRadarChartProps) {
  if (loading) {
    return (
      <div className="flex h-[250px] items-center justify-center text-sm text-text-tertiary">
        Loading...
      </div>
    );
  }

  if (!scores) {
    return (
      <div className="flex h-[250px] items-center justify-center text-sm text-text-tertiary">
        No quality scores available
      </div>
    );
  }

  const data = [
    { subject: 'Security', value: scores.security ?? 0, fullMark: 100 },
    { subject: 'Architecture', value: scores.architecture ?? 0, fullMark: 100 },
    { subject: 'Testing', value: scores.testing ?? 0, fullMark: 100 },
    { subject: 'Maintainability', value: scores.maintainability ?? 0, fullMark: 100 },
    { subject: 'Performance', value: scores.performance ?? 0, fullMark: 100 },
    { subject: 'Documentation', value: scores.documentation ?? 0, fullMark: 100 },
  ];

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="rounded-lg border border-border-base bg-bg-elevated px-3 py-2 shadow-lg">
          <p className="text-sm font-medium text-text-primary">{data.subject}</p>
          <p className="text-xs text-text-secondary">{data.value}/100</p>
        </div>
      );
    }
    return null;
  };

  return (
    <ResponsiveContainer width="100%" height={250}>
      <RadarChart data={data}>
        <PolarGrid stroke="#2A2A2A" opacity={0.3} />
        <PolarAngleAxis 
          dataKey="subject" 
          tick={{ fill: '#999', fontSize: 10 }}
        />
        <PolarRadiusAxis 
          angle={90} 
          domain={[0, 100]} 
          tick={{ fill: '#999', fontSize: 9 }}
          tickCount={5}
        />
        <Radar
          name="Score"
          dataKey="value"
          stroke="#E8A045"
          fill="#E8A045"
          fillOpacity={0.3}
          strokeWidth={2}
        />
        <Tooltip content={<CustomTooltip />} />
      </RadarChart>
    </ResponsiveContainer>
  );
}
