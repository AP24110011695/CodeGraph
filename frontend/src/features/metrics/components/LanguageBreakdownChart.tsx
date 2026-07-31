import {
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import { CHART_COLORS, type ChartDatum } from '../api/metrics.adapters';

interface LanguageBreakdownChartProps {
  data: ChartDatum[];
}

export function LanguageBreakdownChart({ data }: LanguageBreakdownChartProps) {
  if (data.length === 0) {
    return (
      <div className="rounded-md border border-border-base bg-bg-elevated p-4">
        <h3 className="text-sm font-medium text-text-primary">Language breakdown</h3>
        <p className="mt-2 text-sm text-text-secondary">No language data available.</p>
      </div>
    );
  }

  return (
    <div className="rounded-md border border-border-base bg-bg-elevated p-4">
      <h3 className="mb-3 text-sm font-medium text-text-primary">Language breakdown</h3>
      <div className="h-[280px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={90}
              label={({ name, percent }) =>
                `${name} ${((percent ?? 0) * 100).toFixed(0)}%`
              }
            >
              {data.map((entry, index) => (
                <Cell key={entry.name} fill={CHART_COLORS[index % CHART_COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: '#18181b',
                border: '1px solid #3f3f46',
                borderRadius: '6px',
              }}
            />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
