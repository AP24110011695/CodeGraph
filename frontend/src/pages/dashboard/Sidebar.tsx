import { useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  GitBranch,
  Layers,
  Network,
  Search,
  Bot,
  FileText,
  History,
  Crosshair,
  ShieldCheck,
  ShieldAlert,
  BarChart3,
  Settings,
  PanelLeftClose,
  PanelLeft,
} from 'lucide-react';
import { cn } from '@/lib/cn';
import { useUiStore } from '@/core/store/ui.store';
import { Separator } from '@/design-system/primitives/Separator';
import { Tooltip } from '@/design-system/primitives/Tooltip';
import { Button } from '@/design-system/primitives/Button';

const primaryNav = [
  { to: '.', end: true, label: 'Overview', icon: LayoutDashboard },
  { to: 'graph', label: 'Graph', icon: GitBranch },
  { to: 'architecture', label: 'Architecture', icon: Layers },
  { to: 'knowledge', label: 'Knowledge', icon: Network },
  { to: 'search', label: 'Search', icon: Search },
] as const;

const secondaryNav = [
  { to: 'copilot', label: 'Copilot', icon: Bot },
  { to: 'reports', label: 'Reports', icon: FileText },
  { to: 'timeline', label: 'Timeline', icon: History },
  { to: 'impact', label: 'Impact', icon: Crosshair },
  { to: 'quality', label: 'Quality', icon: ShieldCheck },
  { to: 'security', label: 'Security', icon: ShieldAlert },
  { to: 'metrics', label: 'Metrics', icon: BarChart3 },
  { to: 'settings', label: 'Settings', icon: Settings },
] as const;

export function Sidebar() {
  const collapsed = useUiStore((s) => s.sidebarCollapsed);
  const setSidebarCollapsed = useUiStore((s) => s.setSidebarCollapsed);
  const toggleSidebarCollapsed = useUiStore((s) => s.toggleSidebarCollapsed);

  useEffect(() => {
    const media = window.matchMedia('(max-width: 1023px)');
    const sync = () => setSidebarCollapsed(media.matches);
    sync();
    media.addEventListener('change', sync);
    return () => media.removeEventListener('change', sync);
  }, [setSidebarCollapsed]);

  return (
    <aside
      className={cn(
        'flex h-full shrink-0 flex-col border-r border-border-base bg-bg-elevated transition-[width] duration-normal ease-out-expo',
        collapsed ? 'w-sidebar-collapsed' : 'w-sidebar'
      )}
      aria-label="Dashboard navigation"
    >
      <nav className="flex flex-1 flex-col gap-1 overflow-y-auto p-2">
        {primaryNav.map((item) => (
          <SidebarLink key={item.label} item={item} collapsed={collapsed} />
        ))}
        <Separator className="my-2" />
        {secondaryNav.map((item) => (
          <SidebarLink key={item.to} item={item} collapsed={collapsed} />
        ))}
      </nav>
      <div className="border-t border-border-base p-2">
        <Tooltip content={collapsed ? 'Expand sidebar' : 'Collapse sidebar'} side="right">
          <Button
            variant="ghost"
            size="sm"
            className={cn('w-full', collapsed ? 'justify-center px-0' : 'justify-start')}
            onClick={toggleSidebarCollapsed}
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? <PanelLeft className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
            {!collapsed && <span>Collapse</span>}
          </Button>
        </Tooltip>
      </div>
    </aside>
  );
}

function SidebarLink({
  item,
  collapsed,
}: {
  item: { to: string; label: string; icon: typeof LayoutDashboard; end?: boolean };
  collapsed: boolean;
}) {
  const Icon = item.icon;
  const link = (
    <NavLink
      to={item.to}
      end={item.end}
      className={({ isActive }) =>
        cn(
          'flex items-center gap-3 rounded-md px-2 py-2 text-sm text-text-secondary transition-colors duration-fast hover:bg-bg-subtle hover:text-text-primary',
          collapsed && 'justify-center px-0',
          isActive && 'bg-accent-subtle text-text-primary'
        )
      }
    >
      <Icon className="h-4 w-4 shrink-0" aria-hidden />
      {!collapsed && <span>{item.label}</span>}
    </NavLink>
  );

  if (collapsed) {
    return (
      <Tooltip content={item.label} side="right">
        {link}
      </Tooltip>
    );
  }

  return link;
}
