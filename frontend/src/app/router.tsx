import { Suspense, lazy, type ReactNode } from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { AuthGuard } from '@/core/auth/AuthGuard';
import { DashboardRouteGuard } from '@/core/auth/RouteGuard';
import DashboardLayout from '@/pages/dashboard/DashboardLayout';
import { RouteFallback } from './RouteFallback';
import { IndexingRouteGuard, UploadRouteGuard } from '@/core/navigation/FlowRouteGuards';

const LandingPage = lazy(() => import('@/pages/LandingPage'));
const UploadPage = lazy(() => import('@/pages/UploadPage'));
const IndexingPage = lazy(() => import('@/pages/IndexingPage'));
const OverviewPage = lazy(() => import('@/pages/dashboard/OverviewPage'));
const DependencyGraphPage = lazy(() => import('@/pages/dashboard/DependencyGraphPage'));
const ArchitecturePage = lazy(() => import('@/pages/dashboard/ArchitecturePage'));
const KnowledgeGraphPage = lazy(() => import('@/pages/dashboard/KnowledgeGraphPage'));
const SearchPage = lazy(() => import('@/pages/dashboard/SearchPage'));
const CopilotPage = lazy(() => import('@/pages/dashboard/CopilotPage'));
const ReportsPage = lazy(() => import('@/pages/dashboard/ReportsPage'));
const ReportDetailPage = lazy(() => import('@/pages/dashboard/ReportDetailPage'));
const TimelinePage = lazy(() => import('@/pages/dashboard/TimelinePage'));
const ImpactPage = lazy(() => import('@/pages/dashboard/ImpactPage'));
const QualityPage = lazy(() => import('@/pages/dashboard/QualityPage'));
const SecurityPage = lazy(() => import('@/pages/dashboard/SecurityPage'));
const MetricsPage = lazy(() => import('@/pages/dashboard/MetricsPage'));
const SettingsPage = lazy(() => import('@/pages/dashboard/SettingsPage'));

function withSuspense(element: ReactNode) {
  return <Suspense fallback={<RouteFallback />}>{element}</Suspense>;
}

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AuthGuard>{withSuspense(<LandingPage />)}</AuthGuard>,
  },
  {
    path: '/upload',
    element: <AuthGuard><UploadRouteGuard>{withSuspense(<UploadPage />)}</UploadRouteGuard></AuthGuard>,
  },
  {
    path: '/indexing/:repoId',
    element: <AuthGuard><IndexingRouteGuard>{withSuspense(<IndexingPage />)}</IndexingRouteGuard></AuthGuard>,
  },
  {
    path: '/dashboard/:repoId',
    element: (
      <AuthGuard>
        <DashboardRouteGuard>
          <DashboardLayout />
        </DashboardRouteGuard>
      </AuthGuard>
    ),
    children: [
      { index: true, element: withSuspense(<OverviewPage />) },
      { path: 'graph', element: withSuspense(<DependencyGraphPage />) },
      { path: 'architecture', element: withSuspense(<ArchitecturePage />) },
      { path: 'knowledge', element: withSuspense(<KnowledgeGraphPage />) },
      { path: 'search', element: withSuspense(<SearchPage />) },
      { path: 'copilot', element: withSuspense(<CopilotPage />) },
      { path: 'reports', element: withSuspense(<ReportsPage />) },
      { path: 'reports/:reportId', element: withSuspense(<ReportDetailPage />) },
      { path: 'timeline', element: withSuspense(<TimelinePage />) },
      { path: 'impact', element: withSuspense(<ImpactPage />) },
      { path: 'quality', element: withSuspense(<QualityPage />) },
      { path: 'security', element: withSuspense(<SecurityPage />) },
      { path: 'metrics', element: withSuspense(<MetricsPage />) },
      { path: 'settings', element: withSuspense(<SettingsPage />) },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
]);
