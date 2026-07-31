interface AffectedFilesListProps {
  modules: string[];
  services: string[];
  apis: string[];
  symbols: string[];
}

function ListGroup({ title, items }: { title: string; items: string[] }) {
  if (items.length === 0) return null;

  return (
    <div>
      <h4 className="text-xs font-medium uppercase tracking-wide text-text-tertiary">{title}</h4>
      <ul className="mt-2 space-y-1 text-xs text-text-secondary">
        {items.slice(0, 12).map((item) => (
          <li key={item}>• {item}</li>
        ))}
      </ul>
    </div>
  );
}

export function AffectedFilesList({ modules, services, apis, symbols }: AffectedFilesListProps) {
  const hasItems =
    modules.length > 0 || services.length > 0 || apis.length > 0 || symbols.length > 0;

  return (
    <div className="rounded-md border border-border-base bg-bg-elevated p-4">
      <h3 className="mb-3 text-sm font-medium text-text-primary">Affected scope</h3>
      {!hasItems ? (
        <p className="text-sm text-text-secondary">No affected modules or files identified.</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          <ListGroup title="Modules" items={modules} />
          <ListGroup title="Services" items={services} />
          <ListGroup title="APIs" items={apis} />
          <ListGroup title="Symbols" items={symbols} />
        </div>
      )}
    </div>
  );
}
