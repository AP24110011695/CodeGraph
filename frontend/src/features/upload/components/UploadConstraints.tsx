export function UploadConstraints() {
  return (
    <div className="flex flex-wrap items-center justify-center gap-2">
      <span className="rounded-full border border-border-base bg-[#181614] px-3 py-1 text-xs font-semibold text-text-secondary shadow-sm">
        ZIP Only
      </span>
      <span className="rounded-full border border-border-base bg-[#181614] px-3 py-1 text-xs font-medium text-text-tertiary shadow-sm">
        Max 50 MB
      </span>
      <span className="rounded-full border border-border-base bg-[#181614] px-3 py-1 text-xs font-medium text-text-tertiary shadow-sm">
        Recommended 30 MB
      </span>
      <span className="rounded-full border border-accent-muted/40 bg-accent-subtle px-3 py-1 text-xs font-semibold text-accent-default shadow-sm">
        Fast Analysis
      </span>
    </div>
  );
}

