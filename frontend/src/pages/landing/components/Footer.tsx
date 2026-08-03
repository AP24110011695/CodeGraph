export function Footer() {
  return (
    <footer className="border-t border-border-subtle py-6">
      <div className="mx-auto flex max-w-[1280px] flex-col items-center justify-between gap-4 px-6 sm:flex-row">
        <div className="flex items-center gap-6 text-sm text-text-secondary">
          <span>MIT License</span>
          <a
            href="https://github.com/codegraph"
            target="_blank"
            rel="noopener noreferrer"
            className="transition-colors hover:text-text-primary"
          >
            GitHub
          </a>
        </div>
        <div className="text-sm text-text-tertiary">
          Made for developers
        </div>
      </div>
    </footer>
  );
}
