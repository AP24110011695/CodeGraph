import { FeatureCard } from './FeatureCard';

export function FeatureGrid() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <FeatureCard
        icon={
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 4L10 1L17 4V16L10 19L3 16V4Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M10 1V19" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M3 4L10 7L17 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        }
        title="Architecture"
        description="Architecture diagrams"
      />
      <FeatureCard
        icon={
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="10" cy="10" r="3" stroke="currentColor" strokeWidth="1.5"/>
            <path d="M10 1V4M10 16V19M19 10H16M4 10H1M16.36 3.64L14.25 5.75M5.75 14.25L3.64 16.36M16.36 16.36L14.25 14.25M5.75 5.75L3.64 3.64" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
        }
        title="Dependency Graph"
        description="Dependency visualization"
      />
      <FeatureCard
        icon={
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10 2C10 2 10 6 10 6C10 6 6 6 6 6C6 6 6 10 6 10C6 10 2 10 2 10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M18 10C18 10 14 10 14 10C14 10 14 14 14 14C14 14 10 14 10 14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M10 18C10 18 10 14 10 14C10 14 14 14 14 14C14 14 14 10 14 10C14 10 18 10 18 10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        }
        title="AI Copilot"
        description="Ask questions about code"
      />
      <FeatureCard
        icon={
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 9L14.5 11.5L12 14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M14.5 11.5H9C7.62 11.5 6.5 10.38 6.5 9V7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M10 17H5C3.89 17 3 16.1 3 15V5C3 3.9 3.89 3 5 3H15C16.1 3 17 3.9 17 5V10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        }
        title="Security"
        description="Find code risks"
      />
    </div>
  );
}
