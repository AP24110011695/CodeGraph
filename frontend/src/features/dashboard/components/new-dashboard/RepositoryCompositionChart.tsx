import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface CompositionData {
  name: string;
  value: number;
  color: string;
}

interface RepositoryCompositionChartProps {
  data?: Array<{ name: string; count: number }>;
  loading?: boolean;
}

const COMPOSITION_COLORS: Record<string, string> = {
  'Frontend': '#E8A045',
  'Backend': '#4EA1FF',
  'API': '#2FBF71',
  'Tests': '#F2B75A',
  'Configuration': '#8A8070',
  'Documentation': '#7FB8D8',
};

export function RepositoryCompositionChart({ data, loading = false }: RepositoryCompositionChartProps) {
  if (loading) {
    return (
      <div className="flex h-[200px] items-center justify-center text-sm text-text-tertiary">
        Loading...
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="flex h-[200px] items-center justify-center text-sm text-text-tertiary">
        No composition data available
      </div>
    );
  }

  const chartData: CompositionData[] = data.map((item) => ({
    name: item.name,
    value: item.count,
    color: COMPOSITION_COLORS[item.name] || '#6B7280',
  }));

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="rounded-lg border border-border-base bg-bg-elevated px-3 py-2 shadow-lg">
          <p className="text-sm font-medium text-text-primary">{data.name}</p>
          <p className="text-xs text-text-secondary">{data.value.toLocaleString()} items</p>
        </div>
      );
    }
    return null;
  };

  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart
        data={chartData}
        layout="vertical"
        margin={{ top: 5, right: 30, left: 80, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#2A2A2A" opacity={0.3} />
        <XAxis type="number" stroke="#666" tick={{ fill: '#999', fontSize: 11 }} />
        <YAxis 
          type="category" 
          dataKey="name" 
          stroke="#666" 
          tick={{ fill: '#999', fontSize: 11 }}
          width={75}
        />
        <Tooltip content={<CustomTooltip />} />
        <Bar dataKey="value" radius={[0, 4, 4, 0]}>
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
