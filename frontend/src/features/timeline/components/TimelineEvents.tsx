import { SeverityBadge } from '@/features/_shared';
import type { ArchitectureDriftEventDto, HotspotDto } from '../api/timeline.types';

interface TimelineEventsProps {
  driftEvents: ArchitectureDriftEventDto[];
  hotspots: HotspotDto[];
}

export function TimelineEvents({ driftEvents, hotspots }: TimelineEventsProps) {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <section className="rounded-md border border-border-base bg-bg-elevated p-4">
        <h3 className="mb-3 text-sm font-medium text-text-primary">Drift events</h3>
        {driftEvents.length === 0 ? (
          <p className="text-xs text-text-tertiary">No drift events detected.</p>
        ) : (
          <ul className="space-y-2">
            {driftEvents.slice(0, 12).map((event) => (
              <li key={event.event_id} className="rounded-md bg-bg-base px-3 py-2">
                <div className="mb-1 flex items-center justify-between gap-2">
                  <span className="text-xs font-medium text-text-primary">{event.category}</span>
                  <SeverityBadge severity={event.severity} />
                </div>
                <p className="text-xs text-text-secondary">{event.description}</p>
              </li>
            ))}
          </ul>
        )}
      </section>
      <section className="rounded-md border border-border-base bg-bg-elevated p-4">
        <h3 className="mb-3 text-sm font-medium text-text-primary">Hotspots</h3>
        {hotspots.length === 0 ? (
          <p className="text-xs text-text-tertiary">No hotspots detected.</p>
        ) : (
          <ul className="space-y-2">
            {hotspots.slice(0, 12).map((hotspot) => (
              <li key={hotspot.path} className="rounded-md bg-bg-base px-3 py-2">
                <div className="mb-1 flex items-center justify-between gap-2">
                  <span className="truncate font-mono text-xs text-text-primary">{hotspot.path}</span>
                  <SeverityBadge severity={hotspot.risk_level} />
                </div>
                <p className="text-xs text-text-secondary">{hotspot.reason || 'Frequent change area'}</p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
