interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

export function FeatureCard({ icon, title, description }: FeatureCardProps) {
  return (
    <div className="rounded-xl border border-border-subtle bg-bg-elevated p-6 transition-all duration-normal hover:border-border-base hover:-translate-y-0.5 hover:shadow-lg">
      <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-accent-subtle text-accent-default">
        {icon}
      </div>
      <h3 className="mb-2 text-base font-medium text-text-primary">{title}</h3>
      <p className="text-sm text-text-secondary">{description}</p>
    </div>
  );
}
