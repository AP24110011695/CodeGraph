export function StatsRow() {
  const stats = [
    { value: '70+', label: 'API Endpoints' },
    { value: '1200+', label: 'Tests Passing' },
    { value: '12', label: 'Analysis Modules' },
  ];

  return (
    <div className="flex flex-wrap justify-center gap-8 sm:gap-12 lg:gap-16">
      {stats.map((stat) => (
        <div key={stat.label} className="text-center">
          <div className="text-3xl font-medium text-text-primary sm:text-4xl">
            {stat.value}
          </div>
          <div className="mt-1 text-sm text-text-secondary">{stat.label}</div>
        </div>
      ))}
    </div>
  );
}
