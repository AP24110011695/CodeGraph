import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

interface LanguageData {
  name: string;
  value: number;
  color: string;
}

interface LanguageDistributionChartProps {
  data: Array<{ name: string; count: number }>;
  loading?: boolean;
}

// Strict language-to-color mapping ensuring every language gets a unique non-purple color
const LANGUAGE_COLOR_MAP: Record<string, string> = {
  python: '#E8A045',    // Amber
  javascript: '#4F9DFF',// Blue
  typescript: '#27C6B7',// Cyan / Teal
  java: '#FF5C5C',      // Red
  go: '#27C6B7',        // Teal
  rust: '#F28C28',      // Orange
  markdown: '#34C759',  // Green
  cpp: '#8E98A8',       // Slate
  c: '#8E98A8',         // Slate
  html: '#F28C28',      // Orange
  css: '#4F9DFF',       // Blue
  shell: '#34C759',     // Emerald
};

const FALLBACK_PALETTE = [
  '#E8A045', // Amber
  '#4F9DFF', // Blue
  '#27C6B7', // Teal / Cyan
  '#34C759', // Emerald
  '#F28C28', // Orange
  '#8E98A8', // Slate
  '#FF5C5C', // Red
];

function getLanguageColor(name: string, index: number): string {
  const normalized = name.toLowerCase().trim();
  return LANGUAGE_COLOR_MAP[normalized] ?? FALLBACK_PALETTE[index % FALLBACK_PALETTE.length];
}

export function LanguageDistributionChart({ data, loading = false }: LanguageDistributionChartProps) {
  if (loading || !data || data.length === 0) {
    return (
      <div className="flex h-[200px] items-center justify-center text-sm text-text-tertiary">
        {loading ? 'Loading...' : 'No language data available'}
      </div>
    );
  }

  const chartData: LanguageData[] = data.map((item, index) => ({
    name: item.name,
    value: item.count,
    color: getLanguageColor(item.name, index),
  }));

  const total = chartData.reduce((sum, item) => sum + item.value, 0);

  const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ payload: { name: string; value: number } }> }) => {
    if (active && payload && payload.length) {
      const itemData = payload[0].payload;
      const percentage = ((itemData.value / total) * 100).toFixed(1);
      return (
        <div className="rounded-xl border border-border-base bg-[#181614] px-3 py-2 shadow-2xl">
          <p className="text-xs font-semibold text-text-primary">{itemData.name}</p>
          <p className="text-[11px] text-text-secondary">
            {itemData.value.toLocaleString()} files ({percentage}%)
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <ResponsiveContainer width="100%" height={250}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={80}
          paddingAngle={3}
          dataKey="value"
          animationDuration={800}
        >
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} stroke="#181614" strokeWidth={2} />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        <Legend 
          verticalAlign="bottom" 
          height={36}
          iconType="circle"
          formatter={(value: string) => (
            <span className="text-xs font-medium text-text-secondary">{value}</span>
          )}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}

