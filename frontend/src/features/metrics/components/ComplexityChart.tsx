import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { CHART_COLORS, type ChartDatum } from '../api/metrics.adapters';

interface ComplexityChartProps {
  data: ChartDatum[];
  title?: string;
}

export function ComplexityChart({
  data,
  title = 'Complexity & architecture',
}: ComplexityChartProps) {
  if (data.length === 0) {
    return (
      <div className="rounded-md border border-border-base bg-bg-elevated p-4">
        <h3 className="text-sm font-medium text-text-primary">{title}</h3>
        <p className="mt-2 text-sm text-text-secondary">No complexity data available.</p>
      </div>
    );
  }

  return (
    <div className="rounded-md border border-border-base bg-bg-elevated p-4">
      <h3 className="mb-3 text-sm font-medium text-text-primary">{title}</h3>
      <div className="h-[280px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 24 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" />
            <XAxis
              dataKey="name"
              tick={{ fill: '#a1a1aa', fontSize: 11 }}
              interval={0}
              angle={-20}
              textAnchor="end"
              height={60}
            />
            <YAxis tick={{ fill: '#a1a1aa', fontSize: 11 }} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#18181b',
                border: '1px solid #3f3f46',
                borderRadius: '6px',
              }}
            />
            <Bar dataKey="value" fill={CHART_COLORS[0]} radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
