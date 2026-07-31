# CodeGraph Frontend Architecture

Version: 1.0

Status: Official Frontend Blueprint

This document is the single source of truth for building the CodeGraph frontend.

Any AI coding agent working on the frontend must follow this architecture.

Implementation agent:
Cursor Agent

Backend:
FastAPI

Frontend:
React + TypeScript + Vite

# CodeGraph Frontend — Software Architecture Document

### Version 2.0 | Principal Frontend Architecture

---

## Preface

This document is the authoritative blueprint for the CodeGraph frontend. Every decision here is made with three constraints in mind simultaneously: it must feel like a premium SaaS product, it must be implementable by Cursor Agent in isolated phases, and it must faithfully surface the capabilities of a sophisticated backend. Where these constraints conflict, product quality wins.

---

## Section 1 — Technology Stack

Every technology below is justified. Nothing is included because it is popular.

### Core

**React 18** with concurrent features. Suspense boundaries, `useTransition`, and `useDeferredValue` are all necessary for a platform that streams LLM responses and renders large dependency graphs without blocking the UI.

**TypeScript 5** in strict mode. The backend exposes complex nested types (knowledge graph nodes, AST representations, multi-agent traces). Without strict typing, the frontend becomes unmaintainable within weeks. All API response types are generated from the FastAPI OpenAPI schema using `openapi-typescript` — never written by hand.

**Vite** with the React plugin. Fast HMR during development, tree-shaking for production. No CRA, no Next.js (this is a client-side SaaS app, not a content site — SSR adds complexity with no benefit).

### Styling

**Tailwind CSS** with a custom design token configuration. Not used for component-level styling via utility classes scattered throughout JSX — used as the token system underneath a component library. The actual UI components use CVA (Class Variance Authority) for variant management.

**shadcn/ui** as the component foundation. Critical decision: shadcn components are copied into the repository and owned, not imported as a black box. This means full customization control. The CodeGraph design system extends shadcn, it doesn't fight it.

### Data and State

**TanStack Query v5** for all server state. Every backend API call goes through TanStack Query. No `useEffect` + `useState` for data fetching anywhere in the codebase. This is a hard rule enforced by ESLint.

**Zustand** for client state only. Not for server data (that's TanStack Query's job). Zustand stores hold: active repository context, UI panel layout state, copilot conversation history, user preferences, and notification queue.

**No Redux.** The complexity is not justified. The combination of TanStack Query + Zustand covers every state management need cleanly.

### Routing

**React Router v6** with `createBrowserRouter`. Data loaders for route-level data fetching. Nested routes for the complex multi-panel dashboard layout.

### Visualization

**React Flow** for dependency graphs, architecture diagrams, and knowledge graph visualization. Custom node and edge types. The most complex visual component in the system.

**Recharts** for metrics, trends, and analytics charts. Composable, TypeScript-native, Tailwind-compatible.

**Mermaid** for rendered sequence diagrams, UML, and ERD outputs from the AI system. Rendered in an isolated web worker to avoid blocking the main thread.

### AI and Code Display

**Monaco Editor** for code viewing with syntax highlighting, line highlighting, and symbol hover. The same editor used by VS Code. Used in the file explorer, diff viewer, and code context display.

**`react-markdown` + `rehype-highlight`** for rendering AI-generated markdown responses in the copilot panel. Lightweight, fast, and sufficient for chat-style rendering.

### Animation

**Framer Motion** for layout animations, panel transitions, and loading states. Not used for micro-interactions (those use Tailwind's `transition` utilities). Framer Motion is reserved for: page transitions, dashboard panel entrance animations, graph node animations, and the upload flow.

### Utilities

**`openapi-typescript`** — generates TypeScript types from the FastAPI OpenAPI spec automatically. Run as a pre-build step.

**`lucide-react`** — icon library. Consistent, clean, tree-shakeable.

**`date-fns`** — date formatting. No moment.js.

**`clsx` + `tailwind-merge`** — className utilities for conditional and merged Tailwind classes.

**`zod`** — runtime validation for API responses and form inputs.

### Infrastructure

**ESLint** with `@typescript-eslint`, `eslint-plugin-react-hooks`, and a custom rule prohibiting `useEffect` for data fetching.

**Prettier** with Tailwind plugin for class sorting.

**Vitest** for unit tests. **Playwright** for E2E tests on critical flows (upload, indexing, copilot interaction).

---

## Section 2 — Design System

The design system is the foundation. It must be defined before any feature is built. Cursor Agent can implement any feature independently only if it has a stable, well-defined component vocabulary.

### Design Philosophy

The aesthetic target is: **GitHub's information density + Linear's interaction quality + Vercel's visual restraint**. Dark-first, monochromatic base with precisely controlled accent colors. No gradients except in deliberate hero moments. No shadows except as depth indicators. Spacing is mathematical (4px base unit). Typography is hierarchical.

### Color Tokens

```
Design Tokens (defined in tailwind.config.ts):

Background:
  bg-base:        #0A0A0A    (primary surface)
  bg-elevated:    #111111    (cards, panels)
  bg-overlay:     #1A1A1A    (modals, dropdowns)
  bg-subtle:      #141414    (hover states, secondary panels)

Border:
  border-base:    #1F1F1F    (default borders)
  border-subtle:  #171717    (very subtle separators)
  border-strong:  #2A2A2A    (active, focused borders)

Text:
  text-primary:   #FAFAFA    (headings, primary content)
  text-secondary: #A1A1AA    (labels, meta, descriptions)
  text-tertiary:  #52525B    (placeholders, disabled)
  text-inverse:   #0A0A0A    (text on accent backgrounds)

Accent (singular — purple-violet for AI/intelligence):
  accent-default: #7C3AED
  accent-hover:   #6D28D9
  accent-subtle:  #1E1033    (bg tint for accent elements)
  accent-muted:   #4C1D95    (secondary accent use)

Semantic:
  success:        #22C55E    (analysis complete, healthy)
  warning:        #F59E0B    (drift detected, risks)
  danger:         #EF4444    (vulnerabilities, errors)
  info:           #3B82F6    (general information)

Syntax Highlighting (for Monaco):
  syntax-keyword:    #C084FC
  syntax-string:     #86EFAC
  syntax-comment:    #52525B
  syntax-number:     #FCA5A5
  syntax-function:   #93C5FD
  syntax-type:       #F0ABFC
```

### Typography Scale

```
font-family: "Geist" (primary), "Geist Mono" (code), system-ui (fallback)

Scale:
  xs:   11px / 16px  (meta labels, timestamps)
  sm:   12px / 18px  (secondary content, table cells)
  base: 14px / 22px  (body text, descriptions)
  lg:   16px / 24px  (section headers)
  xl:   20px / 28px  (page titles)
  2xl:  24px / 32px  (dashboard headings)
  3xl:  30px / 36px  (hero moments)
```

### Spacing System

4px base unit. All spacing values are multiples: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96. No arbitrary pixel values anywhere in the codebase.

### Component Variants (CVA Pattern)

Every component that has variants uses CVA:

```typescript
// Example pattern — not a component file
const buttonVariants = cva(baseClasses, {
  variants: {
    variant: {
      primary: "bg-accent-default text-white hover:bg-accent-hover",
      secondary: "bg-bg-elevated border border-border-base text-text-primary",
      ghost: "text-text-secondary hover:text-text-primary hover:bg-bg-subtle",
      danger:
        "bg-danger/10 text-danger border border-danger/30 hover:bg-danger/20",
    },
    size: {
      sm: "h-7 px-3 text-xs",
      md: "h-8 px-4 text-sm",
      lg: "h-10 px-5 text-base",
    },
  },
  defaultVariants: { variant: "secondary", size: "md" },
});
```

This pattern applies to: Button, Badge, Input, Select, Tabs, Alert, Toast.

### Animation Tokens

```
Durations:
  fast:    100ms  (micro-interactions, hover states)
  normal:  200ms  (panel transitions, dropdowns)
  slow:    350ms  (page transitions, modal entrances)
  crawl:   500ms  (graph animations, complex layout changes)

Easings:
  ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1)   (entrances)
  ease-in-expo:  cubic-bezier(0.7, 0, 0.84, 0)    (exits)
  ease-spring:   spring(stiffness: 300, damping: 30) (Framer Motion, interactive elements)
```

---

## Section 3 — Folder Structure

This structure is designed so that Cursor Agent can be pointed at a single feature folder and implement it completely without reading adjacent feature folders.

```
src/
│
├── app/                          # Application shell
│   ├── router.tsx                # createBrowserRouter definition
│   ├── providers.tsx             # All context providers composed here
│   ├── App.tsx                   # Root component
│   └── index.css                 # Tailwind base + CSS custom properties
│
├── core/                         # Shared infrastructure (never feature-specific)
│   ├── api/
│   │   ├── client.ts             # Axios instance, interceptors, base URL
│   │   ├── types.ts              # Generated from OpenAPI: "npm run api:types"
│   │   └── errors.ts             # API error normalization
│   ├── auth/
│   │   ├── useAuth.ts            # Auth hook (stubbed for now, ready for implementation)
│   │   └── AuthGuard.tsx         # Route protection wrapper
│   ├── query/
│   │   └── client.ts             # TanStack Query client configuration
│   ├── store/
│   │   ├── repository.store.ts   # Active repo, indexing state
│   │   ├── ui.store.ts           # Panel layout, sidebar state
│   │   ├── copilot.store.ts      # Conversation history
│   │   └── notification.store.ts # Toast queue
│   └── telemetry/
│       └── analytics.ts          # Frontend event tracking stub
│
├── design-system/                # The component library
│   ├── tokens/
│   │   ├── colors.ts
│   │   ├── typography.ts
│   │   └── spacing.ts
│   ├── primitives/               # Atom-level components
│   │   ├── Button/
│   │   ├── Input/
│   │   ├── Badge/
│   │   ├── Avatar/
│   │   ├── Tooltip/
│   │   ├── Separator/
│   │   └── Skeleton/
│   ├── patterns/                 # Molecule-level components
│   │   ├── Card/
│   │   ├── DataTable/
│   │   ├── EmptyState/
│   │   ├── ErrorBoundary/
│   │   ├── LoadingOverlay/
│   │   ├── ProgressBar/
│   │   ├── SearchInput/
│   │   ├── StatusIndicator/
│   │   └── Tabs/
│   └── layout/                   # Layout components
│       ├── PageShell/
│       ├── SidebarLayout/
│       ├── PanelGroup/
│       └── ResizablePanel/
│
├── features/                     # One folder per feature — Cursor Agent's unit of work
│   ├── upload/
│   ├── repository/
│   ├── indexing/
│   ├── dashboard/
│   ├── dependency-graph/
│   ├── architecture/
│   ├── knowledge-graph/
│   ├── search/
│   ├── copilot/
│   ├── reports/
│   ├── timeline/
│   ├── impact-analysis/
│   ├── quality/
│   ├── security/
│   ├── metrics/
│   ├── settings/
│   └── _shared/                  # Components shared between features (use sparingly)
│
├── pages/                        # Route-level page components (thin wrappers)
│   ├── LandingPage.tsx
│   ├── UploadPage.tsx
│   ├── IndexingPage.tsx
│   └── dashboard/
│       ├── DashboardLayout.tsx
│       ├── OverviewPage.tsx
│       ├── DependencyGraphPage.tsx
│       ├── ArchitecturePage.tsx
│       ├── KnowledgeGraphPage.tsx
│       ├── SearchPage.tsx
│       ├── CopilotPage.tsx
│       ├── ReportsPage.tsx
│       ├── TimelinePage.tsx
│       ├── ImpactPage.tsx
│       ├── QualityPage.tsx
│       ├── SecurityPage.tsx
│       └── MetricsPage.tsx
│
├── hooks/                        # Application-level hooks (cross-feature)
│   ├── useRepository.ts
│   ├── useIndexingStatus.ts
│   ├── useKeyboardShortcuts.ts
│   └── useStreamingResponse.ts
│
└── lib/                          # Pure utility functions
    ├── cn.ts                     # clsx + tailwind-merge
    ├── format.ts                 # Date, number, file size formatters
    └── graph.ts                  # Graph data transformation utilities
```

### Feature Folder Internal Structure

Every feature folder follows the exact same internal structure. Cursor Agent learns this pattern once and applies it everywhere:

```
features/[feature-name]/
├── api/
│   ├── [feature].api.ts          # API call functions
│   ├── [feature].queries.ts      # TanStack Query hooks
│   └── [feature].types.ts        # Feature-specific type overrides
├── components/
│   ├── [FeatureName]Panel.tsx    # Main container component
│   ├── [SubComponent].tsx
│   └── index.ts                  # Named exports only
├── store/
│   └── [feature].store.ts        # Local Zustand slice (if needed)
├── hooks/
│   └── use[FeatureName].ts       # Feature-specific hooks
└── index.ts                      # Public API of the feature
```

This means Cursor Agent receives a prompt like: "Implement the dependency graph feature. Its folder is `src/features/dependency-graph/`. Follow the standard feature folder structure. The API endpoints are listed in `dependency-graph.api.ts`." Everything it needs is contained.

---

## Section 4 — Routing Architecture

```
Routes:

/                               LandingPage
  (redirects to /upload if no active repo)
  (redirects to /dashboard if active repo)

/upload                         UploadPage
  (file drop + GitHub URL input)

/indexing/:repoId               IndexingPage
  (progress tracking, real-time status)

/dashboard/:repoId              DashboardLayout (persistent shell)
  /                             → OverviewPage (default)
  /graph                        → DependencyGraphPage
  /architecture                 → ArchitecturePage
  /knowledge                    → KnowledgeGraphPage
  /search                       → SearchPage
  /copilot                      → CopilotPage
  /reports                      → ReportsPage
  /reports/:reportId            → ReportDetailPage
  /timeline                     → TimelinePage
  /impact                       → ImpactPage
  /quality                      → QualityPage
  /security                     → SecurityPage
  /metrics                      → MetricsPage
  /settings                     → SettingsPage
```

### Route Guards

```
RouteGuard logic:
  /dashboard/* requires: active repository in store + indexing status = READY
  If no active repo → redirect to /upload
  If repo is indexing → redirect to /indexing/:repoId
  If repo is READY → allow access
```

### Data Loaders

React Router v6 data loaders fetch critical route data before the component renders:

```
DashboardLayout loader:
  → fetch repository metadata
  → fetch repository analysis status
  → fetch current indexing progress

OverviewPage loader:
  → fetch dashboard summary (stats, health score, recent analysis)

ReportDetailPage loader:
  → fetch specific report by ID
```

This eliminates the waterfall of "render skeleton → fetch → render content" on route transitions. The route transition itself shows a loading indicator; the page renders with data already available.

---

## Section 5 — API Layer Architecture

### Base Client

```typescript
// core/api/client.ts structure (not code — description)

The Axios instance is configured with:
- baseURL from environment variable (VITE_API_URL)
- 30 second default timeout
- Request interceptor: attach auth token from Zustand store
- Request interceptor: attach active repository ID header (X-Repository-Id)
- Response interceptor: normalize errors into APIError type
- Response interceptor: extract data from FastAPI response envelope

APIError shape:
  code: string       (machine-readable error code from backend)
  message: string    (human-readable message)
  status: number     (HTTP status)
  detail?: unknown   (additional context from FastAPI)
```

### Query Hook Pattern

Every API call is wrapped in a TanStack Query hook. The query key follows a strict hierarchical convention:

```
Query key convention:
  [feature, operation, ...parameters]

Examples:
  ["repository", "metadata", repoId]
  ["dependency-graph", "nodes", repoId, filters]
  ["copilot", "conversation", conversationId]
  ["reports", "list", repoId]
  ["reports", "detail", reportId]

Why this matters:
  Invalidation is predictable: queryClient.invalidateQueries(["repository"])
  invalidates ALL repository queries. Surgical invalidation is also possible:
  queryClient.invalidateQueries(["repository", "metadata", specificRepoId])
```

### Streaming API Pattern

The copilot and several AI responses stream tokens. The streaming pattern:

```
useStreamingResponse hook:
  - Opens EventSource (SSE) connection to backend streaming endpoint
  - Appends tokens to a string buffer in local state
  - On stream end, marks response as complete
  - On error, emits to error boundary
  - Cleanup on unmount: closes EventSource connection

The streaming response is stored in Zustand copilot store, not TanStack Query,
because it's a mutable stream, not a cacheable query result.
```

### API Layer per Feature

Each feature owns its API calls. There is no global `api.ts` with every endpoint. The import path makes ownership explicit:

```
import { fetchDependencyGraph } from "@/features/dependency-graph/api/dependency-graph.api"
import { useDependencyGraphQuery } from "@/features/dependency-graph/api/dependency-graph.queries"
```

---

## Section 6 — State Management Architecture

### The Two-Store Rule

**TanStack Query** = all server state (data that came from the API and can be refetched)
**Zustand** = all client state (UI preferences, derived state, ephemeral state)

Violation of this rule is the most common source of stale data bugs and unnecessary complexity in React applications. It is enforced by ESLint rule.

### Zustand Store Architecture

```
repository.store.ts:
  activeRepositoryId: string | null
  activeRepository: RepositoryMetadata | null
  indexingStatus: IndexingStatus
  setActiveRepository(id, metadata): void
  setIndexingStatus(status): void
  clearRepository(): void

ui.store.ts:
  sidebarCollapsed: boolean
  copilotPanelOpen: boolean
  activePanelLayout: "single" | "split" | "triple"
  graphFilters: GraphFilterState
  preferredTheme: "dark" | "light"   (dark-first, light as option)
  setSidebarCollapsed(v): void
  setCopilotPanelOpen(v): void
  setActivePanelLayout(layout): void

copilot.store.ts:
  conversations: Map<string, Conversation>
  activeConversationId: string | null
  streamingMessageId: string | null
  streamingContent: string
  addMessage(conversationId, message): void
  appendStreamToken(token): void
  finalizeStreamingMessage(): void
  createConversation(): string

notification.store.ts:
  queue: Notification[]
  addNotification(n): void
  removeNotification(id): void
  clearAll(): void
```

### TanStack Query Configuration

```
Query client settings:
  staleTime: 5 minutes     (data is fresh for 5 min — no background refetch)
  gcTime:    30 minutes    (inactive queries kept in cache for 30 min)
  retry:     2             (retry failed requests twice with exponential backoff)
  refetchOnWindowFocus: false  (this is a developer tool, not a live feed)

Per-query overrides (examples):
  Repository metadata: staleTime = Infinity (doesn't change until re-upload)
  Indexing status: staleTime = 0, refetchInterval = 2000 (poll during indexing)
  Dependency graph: staleTime = 10 minutes (heavy to compute, cache aggressively)
  Search results: staleTime = 30 seconds (queries change frequently)
  Copilot messages: not in TanStack Query (in Zustand, it's streaming state)
```

---

## Section 7 — Page and Feature Architecture

For every feature: purpose, UI, user flow, components, APIs used, state, loading/empty/error states.

---

### Feature: Upload

**Purpose**: First contact. The user has no repository yet. This must be frictionless and trustworthy.

**UI**: Full-page centered layout. A large drop zone with subtle animated border. Below it, a text input for GitHub repository URL. Below that, a note about file size limits and supported types. No navigation, no sidebar — the user has one job here.

**User flow**:

1. User drags ZIP onto drop zone (or clicks to browse)
2. File validates client-side (size limit, `.zip` extension)
3. Upload progress bar appears with percentage
4. On completion, redirect to `/indexing/:repoId`

**Components**:

- `UploadDropzone` — handles drag events, file selection, validation
- `UploadProgressBar` — animated progress indicator with percentage
- `GitHubUrlInput` — text field with validation and submit
- `UploadConstraints` — static informational text (supported formats, size limit)

**Backend APIs**:

- `POST /repositories/upload` — multipart form data
- `POST /repositories/github` — GitHub URL submission

**Global state**: On success, `repository.store.setActiveRepository(id, metadata)`

**Local state**: `file: File | null`, `uploadProgress: number`, `isUploading: boolean`, `error: string | null`

**Loading state**: Progress bar with animated fill. Percentage label updates from upload XHR progress event.

**Error state**: Inline error message below drop zone. Red border on drop zone. Clear action to retry.

**Empty state**: N/A — the drop zone is the default state.

**Animation**: Framer Motion `AnimatePresence` on the progress bar entering. Subtle pulse on the drop zone border while dragging.

---

### Feature: Indexing

**Purpose**: Repository is uploaded. Analysis is running. The user must feel informed, not abandoned. This page is the trust-builder between upload and the product.

**UI**: Split into two columns. Left: animated progress steps showing which analysis stage is active. Right: "What's happening" — a live log of events from the backend, rendered as they arrive. At the top, repository name and estimated completion. At the bottom, a "This may take a few minutes for large repositories" note.

**User flow**:

1. User arrives from upload
2. Progress steps animate through: Scanning → Parsing → Indexing → Building Graph → Embedding → Analyzing
3. Each step shows a completion indicator when done
4. Live event log streams from SSE endpoint
5. On `READY` status, button appears: "Open Dashboard" — then auto-redirects after 3 seconds

**Components**:

- `IndexingProgressStepper` — vertical step list with active/complete states
- `IndexingEventLog` — scrolling live log with syntax-colored event types
- `IndexingHeader` — repository name, estimated time, elapsed time
- `IndexingCompleteCard` — appears on completion with CTA

**Backend APIs**:

- `GET /repositories/:id/status` — polled every 2 seconds (TanStack Query `refetchInterval`)
- `GET /repositories/:id/indexing/events` — SSE stream for live log

**Global state**: Updates `repository.store.indexingStatus` on every poll response

**Local state**: `events: IndexingEvent[]` (append-only, SSE-driven)

**Loading state**: The page IS the loading state. Stepper shows which step is active.

**Error state**: If indexing fails, step turns red with error message. "Retry indexing" button appears.

**Empty state**: N/A

---

### Feature: Dashboard Overview

**Purpose**: First view after indexing. Must immediately communicate "this system understands your codebase." High information density but never cluttered.

**UI**: Three-column grid layout. Top row: four stat cards (files, languages, dependencies, health score). Middle row: framework badges detected, tech stack visualization. Bottom row: two panels side by side — architecture summary (AI-generated paragraph) and top risks (3-5 items from risk analysis). Floating: copilot button in bottom-right corner.

**User flow**:

1. User arrives from indexing complete
2. Stats load immediately from pre-fetched route data
3. Framework badges animate in with stagger
4. Architecture summary streams in from AI (typing effect)
5. Risk items appear with severity badges
6. User can click any card/section to navigate to the dedicated page

**Components**:

- `StatCard` — reusable, shows icon + number + label + trend
- `TechStackGrid` — detected frameworks with version badges
- `ArchitectureSummaryCard` — streaming text with typing animation
- `RiskOverviewList` — top risks with severity indicators
- `HealthScoreRing` — circular gauge showing overall codebase health
- `QuickActionGrid` — buttons to main features (Graph, Copilot, Reports)

**Backend APIs**:

- `GET /repositories/:id/summary` — all overview data in one endpoint
- `GET /repositories/:id/health` — health score and breakdown
- `GET /repositories/:id/risks/top` — top 5 risks

**Global state**: Read from `repository.store`

**Local state**: `summaryStreamContent: string` for the streaming summary

**Loading state**: `StatCard` and all sections have skeleton variants that match their shape exactly. No layout shift when data loads.

**Empty state**: N/A — dashboard always has data if indexing completed

**Error state**: Each card handles its own error independently with a "Retry" action. One failed card doesn't break the dashboard.

---

### Feature: Dependency Graph

**Purpose**: Visualize how every file and module relates to every other. The most technically complex and visually impressive feature.

**UI**: Full-screen canvas with React Flow. Left sidebar: filter panel (by language, file type, coupling threshold). Top bar: search for a specific node, zoom controls, layout toggle (hierarchical/force-directed/radial). Right panel (slides in on node click): node detail — file path, metrics, direct dependencies, dependents, LLM-generated explanation of this file's role.

**User flow**:

1. User opens page — graph loads with full repository dependency network
2. Nodes are colored by file type (JS/TS = blue, Python = yellow, CSS = purple, config = gray)
3. Edge thickness represents coupling strength
4. User can search for a node by filename
5. User clicks a node → right panel slides in with details
6. User can filter to show only modules above a coupling threshold
7. User can switch between layout algorithms

**Components**:

- `DependencyGraphCanvas` — React Flow wrapper with custom node/edge types
- `DependencyNode` — custom React Flow node: file icon, name, complexity badge
- `DependencyEdge` — custom React Flow edge: thickness = coupling weight
- `GraphFilterPanel` — left sidebar with filter controls
- `GraphToolbar` — search, layout, zoom controls
- `NodeDetailPanel` — right drawer with file details and AI explanation
- `GraphLegend` — color coding explanation

**Backend APIs**:

- `GET /repositories/:id/graph/dependencies` — full graph data (nodes + edges)
- `GET /repositories/:id/graph/node/:nodeId` — individual node details
- `POST /repositories/:id/graph/explain/:nodeId` — AI explanation of node

**Global state**: Graph filter state in `ui.store.graphFilters`

**Local state**: `selectedNodeId: string | null`, `isDetailPanelOpen: boolean`, `layoutAlgorithm: string`

**Loading state**: Skeleton canvas with 20 placeholder nodes in expected positions. Not a spinner — maintains spatial expectation.

**Empty state**: "No dependencies detected" with explanation and link to check scanner results.

**Error state**: "Failed to load dependency graph" with retry button. Error shown in canvas area, not modal.

**Performance note**: For large graphs (1000+ nodes), implement virtualization: only render nodes within viewport. React Flow handles this natively via `nodesDraggable` and viewport culling. Additionally, cluster nodes by top-level directory and allow expand/collapse.

---

### Feature: Architecture View

**Purpose**: High-level system architecture, not file-level. Shows services, layers, communication patterns, and architectural boundaries.

**UI**: Two-tab layout. Tab 1: "Diagram" — a React Flow canvas showing the high-level architecture (Frontend → Backend → Database → External Services). Tab 2: "Explanation" — AI-generated prose explanation of the architecture with sections (Overview, Key Decisions, Risks, Recommendations). Below the diagram: Mermaid-rendered sequence diagrams for key flows (auth flow, data flow, etc.).

**Components**:

- `ArchitectureCanvas` — React Flow with architectural-layer node types
- `ArchitectureLayerNode` — custom node: layer name, contained components list
- `ArchitectureExplainer` — markdown renderer for AI prose
- `MermaidDiagram` — Mermaid renderer (isolated in web worker)
- `ArchitectureTabBar` — tab navigation between views

**Backend APIs**:

- `GET /repositories/:id/architecture` — architectural structure data
- `GET /repositories/:id/architecture/explanation` — AI prose explanation
- `GET /repositories/:id/architecture/flows` — sequence diagram Mermaid strings

**Global state**: None

**Local state**: `activeTab`, `selectedLayer`

**Loading states**: Skeleton for diagram canvas. Typing animation for streaming AI explanation.

---

### Feature: Knowledge Graph

**Purpose**: The semantic graph of code entities — classes, functions, interfaces, their relationships, and AI-derived semantic connections. More abstract than dependency graph; more conceptual.

**UI**: Force-directed graph with React Flow. Nodes are semantic entities (class, function, interface, module). Edges are typed relationships (inherits, implements, calls, uses). Node size represents usage frequency. Color represents entity type. On hover: tooltip with entity signature. On click: full detail panel with cross-references, callers, callees, and AI-generated description of the entity's role.

**Components**:

- `KnowledgeGraphCanvas` — React Flow with semantic node types
- `SemanticNode` — entity node with type icon and frequency indicator
- `RelationshipEdge` — typed, labeled edges
- `EntityDetailPanel` — side panel with full entity information
- `GraphSearchCommand` — command-palette style search for finding entities

**Backend APIs**:

- `GET /repositories/:id/knowledge-graph/entities` — all graph entities
- `GET /repositories/:id/knowledge-graph/relationships` — all relationships
- `GET /repositories/:id/knowledge-graph/entity/:id` — entity details
- `POST /repositories/:id/knowledge-graph/entity/:id/explain` — AI explanation

---

### Feature: Search

**Purpose**: Semantic code search. Not grep. "Find all functions that handle authentication" should return relevant results even if they don't contain the word "authentication."

**UI**: Prominent search input at top. Below: filter chips (by file type, by result type). Results list: each result shows file path, matched code snippet with syntax highlighting, semantic relevance score, and an AI-generated explanation of why this result is relevant. Side panel on result click: full file view in Monaco Editor with the matched section highlighted and scrolled into view.

**Components**:

- `SearchBar` — large, prominent search input with placeholder text cycling through examples
- `SearchFilterChips` — filter by language, result type, file path
- `SearchResultItem` — result card: path, snippet, score, explanation
- `CodeViewerPanel` — Monaco Editor showing full file with highlight
- `SearchEmptyState` — shown before first search and on no results

**Backend APIs**:

- `POST /repositories/:id/search` — semantic search with filters
- `GET /repositories/:id/search/suggestions` — autocomplete/suggestions
- `GET /repositories/:id/files/:path` — file content for viewer

**Local state**: `query: string`, `filters: SearchFilters`, `selectedResult: SearchResult | null`

**Performance**: Results debounced 300ms. Cancel previous request on new query.

---

### Feature: Copilot

**Purpose**: The conversational AI architect. Ask anything about the codebase, get grounded, cited answers. The highest-value and most-used feature.

**UI**: Two-panel layout. Left (60%): conversation interface — message history, streaming responses, input box. Right (40%): context panel — shows what code context was retrieved and used to generate the response (source files, graph nodes, metrics). The context panel builds up as the response streams in, making the retrieval process visible and trustworthy.

The conversation interface feels like a premium chat product: user messages on the right (dark bubble), AI messages on the left (slightly elevated surface), markdown rendering with syntax-highlighted code blocks, citations shown as inline `[file.py:45]` links that scroll the context panel to the relevant file.

**User flow**:

1. User opens copilot — previous conversations shown in left sidebar if they exist
2. User types question and submits
3. Context panel shows "Retrieving..." with spinner
4. Context panel populates with retrieved sources (files, functions, graph nodes)
5. AI response streams in on the left, tokens appearing progressively
6. Citations in the response are clickable, scrolling context panel to source
7. At end of response, user sees confidence indicators and a "Was this helpful?" thumbs
8. User can ask follow-up questions

**Components**:

- `CopilotLayout` — two-panel container
- `ConversationSidebar` — list of past conversations
- `MessageThread` — scrollable message history
- `UserMessage` — user message bubble
- `AIMessage` — AI response with markdown rendering, citations, confidence
- `StreamingIndicator` — animated "thinking" and token streaming indicator
- `ContextPanel` — retrieved sources display
- `ContextSource` — individual source file/node card in context panel
- `MessageInput` — text area with send button, model indicator, context toggle
- `FeedbackButtons` — thumbs up/down for response quality

**Backend APIs**:

- `POST /repositories/:id/copilot/chat` (streaming SSE)
- `GET /repositories/:id/copilot/conversations` — conversation list
- `GET /repositories/:id/copilot/conversations/:id` — conversation history
- `POST /repositories/:id/copilot/feedback` — thumbs up/down

**Global state**: `copilot.store` — conversation history, streaming state

**Local state**: `inputValue: string`, `isStreaming: boolean`, `contextVisible: boolean`

**Loading state**: "Thinking" animation with three-dot pulse. Context panel shows skeleton source cards while retrieving.

**Empty state**: "Ask anything about your codebase." with 6 suggested question chips.

**Error state**: "I encountered an error analyzing your codebase." in the message thread. Retry button inline in the message.

---

### Feature: Reports

**Purpose**: Formal, structured output documents. Unlike the conversational copilot, reports are comprehensive artifacts — architecture reports, security reports, quality reports.

**UI**: Reports list page shows report cards with type, generation date, and status. Click a report: full-page report viewer with left navigation (table of contents, jump to section), main content area with rich markdown rendering, and right sidebar with metadata and download options.

**Components**:

- `ReportsList` — grid of report cards
- `ReportCard` — type icon, title, date, status badge, action menu
- `ReportViewer` — full report display
- `ReportTableOfContents` — sticky left navigation
- `ReportSection` — individual section with heading, content, supporting diagrams
- `ReportMetaSidebar` — generated date, repository SHA, download button
- `GenerateReportModal` — report type selection and generation trigger

**Backend APIs**:

- `GET /repositories/:id/reports` — list all reports
- `GET /repositories/:id/reports/:reportId` — report content
- `POST /repositories/:id/reports/generate` — generate new report
- `GET /repositories/:id/reports/:reportId/download` — PDF download

---

### Feature: Timeline

**Purpose**: Architecture evolution over time. How has the codebase changed? When did complexity increase? When were services split?

**UI**: Horizontal timeline at the top showing commits/releases. Main area: "architecture snapshot" for the selected point in time — mini dependency graph, key metrics, and change summary. Comparison mode: select two points, see side-by-side or diff view of what changed architecturally.

**Components**:

- `TimelineRail` — horizontal scrollable timeline with event markers
- `TimelineEvent` — commit marker with branch, message, date
- `SnapshotView` — mini architecture diagram for selected point
- `SnapshotMetrics` — metrics at that point in time
- `ChangesSummary` — what changed between snapshots (AI-generated)
- `ComparisonToggle` — enable/disable comparison mode
- `TimelineDiff` — side-by-side comparison view

**Backend APIs**:

- `GET /repositories/:id/timeline` — timeline events
- `GET /repositories/:id/timeline/:commitSha/snapshot` — snapshot data
- `POST /repositories/:id/timeline/compare` — compare two snapshots

---

### Feature: Impact Analysis

**Purpose**: "If I change this file, what breaks?" Pre-change risk assessment.

**UI**: Search/select a file or function. Below: concentric ring visualization showing direct impact (inner ring), transitive impact (outer rings), and estimated risk score. Below that: a list of affected files sorted by impact severity. A "Generate Impact Report" button triggers a full AI analysis.

**Components**:

- `ImpactTargetSelector` — search/select file or function
- `ImpactRingVisualization` — concentric SVG rings showing blast radius
- `ImpactFileList` — list of affected files with severity
- `ImpactRiskScore` — large numeric risk indicator with interpretation
- `ImpactReportGenerator` — trigger and display full AI report

**Backend APIs**:

- `POST /repositories/:id/impact/analyze` — compute impact for a target
- `GET /repositories/:id/impact/report/:analysisId` — full impact report

---

### Feature: Quality Analysis

**Purpose**: Code quality metrics, hotspots, and improvement recommendations.

**UI**: Dashboard layout. Top: quality score with trend chart. Below: three columns — Hotspots (files with high complexity + churn), Code Smells (list with severity), SOLID Violations (list with file and explanation). Each item is clickable to view the specific code in Monaco Editor.

**Components**:

- `QualityScoreHeader` — score, trend, last analyzed date
- `HotspotList` — files ranked by complexity × churn
- `CodeSmellList` — smells with type badges and severity
- `SOLIDViolationList` — violations with principle label
- `QualityCodeViewer` — Monaco Editor panel for viewing flagged code

**Backend APIs**:

- `GET /repositories/:id/quality/summary`
- `GET /repositories/:id/quality/hotspots`
- `GET /repositories/:id/quality/smells`
- `GET /repositories/:id/quality/solid`

---

### Feature: Security Analysis

**Purpose**: Security vulnerabilities, CVE matches, and risk assessment.

**UI**: Red-tinted header if critical vulnerabilities found (contextual severity signaling). Three tabs: Vulnerabilities (CVE matches from dependency analysis), Code Risks (hardcoded secrets, injection risks from static analysis), Architecture Risks (missing auth, insecure patterns at system level). Each item: severity badge, description, affected file/dependency, remediation recommendation.

**Components**:

- `SecuritySeverityHeader` — overall risk level with color coding
- `VulnerabilityList` — CVE items with CVSS score, affected version, fix version
- `CodeRiskList` — static analysis findings with file and line reference
- `ArchitectureRiskList` — system-level security findings
- `SecurityItemDetail` — expanded detail panel for any security finding

**Backend APIs**:

- `GET /repositories/:id/security/summary`
- `GET /repositories/:id/security/vulnerabilities`
- `GET /repositories/:id/security/code-risks`
- `GET /repositories/:id/security/architecture-risks`

---

### Feature: Metrics Dashboard

**Purpose**: Quantitative engineering metrics. Complexity trends, coupling distribution, size analysis, language breakdown.

**UI**: Grid of charts. Each chart is a Recharts component. Metrics: lines of code by language (pie), complexity distribution (histogram), coupling scores (bar chart), file size distribution (histogram), dependency depth distribution (bar chart), code growth over time (line chart if git history available).

**Components**:

- `MetricsGrid` — responsive chart grid
- `LanguageBreakdownChart` — donut chart
- `ComplexityHistogram` — bar chart
- `CouplingDistributionChart` — scatter or bar
- `MetricsFilterBar` — filter by module, time range
- `MetricCard` — wrapper for every chart with title, description, export button

**Backend APIs**:

- `GET /repositories/:id/metrics/overview`
- `GET /repositories/:id/metrics/complexity`
- `GET /repositories/:id/metrics/coupling`
- `GET /repositories/:id/metrics/language`

---

## Section 8 — Loading State Architecture

Loading states are not an afterthought. There are exactly four loading patterns in CodeGraph, and each has a specific use case:

**Pattern 1: Skeleton** — Used when the layout of the content is known. Skeleton components match the exact shape of the loaded content (same height, same columns, same card structure). Zero layout shift on data load. Used for: all list views, all card grids, dashboard overview, report viewer.

**Pattern 2: Spinner** — Used only when the loading duration is unpredictable and the layout shape is unknown. Used for: code viewer loading, graph data loading (before any nodes appear), AI response start (before first token).

**Pattern 3: Progress bar** — Used for multi-stage processes with measurable progress. Used for: file upload, repository indexing.

**Pattern 4: Streaming** — Used for AI responses. Text appears token by token with a blinking cursor. The container is present from the start; content fills in. No skeleton, no spinner — the streaming itself is the loading feedback.

**Rule**: A loading state must never cause layout shift. Every skeleton must be dimensionally identical to its loaded counterpart.

---

## Section 9 — Error Handling Architecture

Errors are handled at three levels:

**Level 1: React Error Boundaries** — Catch rendering errors and display a fallback UI. Placed at the feature level (not the page level, not the global level). If the dependency graph crashes, only the dependency graph panel shows an error. The rest of the dashboard is unaffected.

**Level 2: TanStack Query Error States** — Every `useQuery` and `useMutation` returns an `error` value. The component is responsible for rendering the appropriate error UI based on the error code. The `APIError` type from the client provides machine-readable error codes so components can show specific messages.

```
Error code → User message mapping:
  REPO_NOT_FOUND       → "Repository not found. It may have been deleted."
  ANALYSIS_FAILED      → "Analysis could not complete. Check the indexing logs."
  LLM_UNAVAILABLE      → "AI features are temporarily unavailable."
  RATE_LIMITED         → "You've made too many requests. Please wait a moment."
  GRAPH_TOO_LARGE      → "This graph is too large to render fully. Try filtering first."
```

**Level 3: Global Error Toast** — For unexpected errors that the component cannot handle gracefully. The `notification.store` receives the error and displays a toast. Used sparingly — only when no inline error UI is possible.

**Error UI Principle**: Every error state must answer three questions: What went wrong? Is it the user's fault? What can they do next? An error that just says "Something went wrong" fails all three.

---

## Section 10 — Notification Architecture

```
Notification types:
  toast:   transient, 4-second auto-dismiss, bottom-right
  banner:  persistent, requires user dismissal, top of page
  inline:  embedded in component, never dismissed automatically

Toast variants:
  success   (green border, checkmark icon)
  error     (red border, x-circle icon)
  warning   (amber border, alert icon)
  info      (blue border, info icon)

Toast triggers:
  - Report generation started → info
  - Report generation complete → success
  - Indexing failed → error
  - Security vulnerability found → warning (non-dismissable banner in security panel)
  - Analysis complete → success
```

The `ToastContainer` component subscribes to `notification.store.queue` and renders toasts using Framer Motion for enter/exit animations.

---

## Section 11 — Animation Strategy

Framer Motion is used in six specific scenarios. Nothing else gets Framer Motion — use Tailwind transitions for everything else.

1. **Page transitions**: Fade + slight upward slide when navigating between dashboard pages. 200ms, ease-out-expo.

2. **Panel entrance**: The right-side detail panels (node detail, search result viewer, impact analysis) slide in from the right. 350ms, spring easing.

3. **Dashboard card entrance**: Cards stagger in on first render. 100ms delay between each card. This is the "wow" moment after indexing completes.

4. **Upload completion**: The drop zone scales down and fades out, transitioning to the redirect animation. 200ms.

5. **Graph node selection**: Selected node scales up slightly (1.05) and its edges highlight with a color transition. Handled by React Flow's built-in animation props, not Framer Motion directly.

6. **Streaming response**: The AI message container height animates open as content streams in. Framer Motion layout animations handle this automatically.

All other interactions (hover states, focus rings, button states, dropdown open/close) use Tailwind's `transition-colors`, `transition-opacity`, and `transition-transform` utilities with the `duration-100` or `duration-200` tokens.

---

## Section 12 — Dashboard Layout Architecture

The dashboard has a persistent shell that surrounds all dashboard pages:

```
DashboardLayout:
├── TopBar (fixed, full width)
│   ├── Left: CodeGraph logo + repository name + status indicator
│   ├── Center: Global search trigger (⌘K opens SearchPage)
│   └── Right: Notifications bell + settings + user avatar
│
├── Sidebar (fixed left, collapsible)
│   ├── Navigation items: Overview, Graph, Architecture, Knowledge, Search
│   ├── Navigation items: Copilot, Reports, Timeline, Impact, Quality, Security, Metrics
│   ├── Collapse toggle at bottom
│   └── Width: 240px expanded, 48px collapsed (icon-only)
│
├── Main Content Area (scrollable)
│   └── <Outlet /> — current page renders here
│
└── Copilot Panel (fixed right, slides in/out)
    ├── Toggle button: floating button OR keyboard shortcut ⌘J
    ├── Width: 400px when open
    └── Available on ALL dashboard pages (persistent across navigation)
```

The copilot panel is globally available and persists across page navigation. A user can navigate to the Dependency Graph page and ask the copilot about a specific node they see — the copilot has awareness of the current page context (passed as metadata in the conversation request).

### Resizable Panels

On the Dependency Graph, Architecture, and Knowledge Graph pages, the canvas and detail panel are resizable using a drag handle. Implemented with a custom `ResizablePanel` component (or `react-resizable-panels`). Panel sizes persist to `localStorage` via the `ui.store`.

---

## Section 13 — Responsive Strategy

CodeGraph is a desktop-first developer tool. This is the honest assessment: complex graph visualizations, multi-panel layouts, and code viewers cannot meaningfully degrade to mobile without becoming a different product.

The responsive strategy is:

- **Desktop (≥1280px)**: Full feature set, multi-panel layouts, all visualizations
- **Tablet (768px–1279px)**: Single-panel view, all features accessible but panels are full-screen (no side-by-side). Navigation collapses to icon sidebar.
- **Mobile (<768px)**: Read-only views only. Reports, metrics, and analysis summaries are readable. Graph and code features show a "Best experienced on desktop" message. The copilot is accessible. No upload capability on mobile.

This is not a failure to support mobile — it is an honest acknowledgment that certain tools belong on certain devices.

---

## Section 14 — Authentication Readiness

Auth is not implemented yet but the architecture is ready for it. The auth layer is stubbed:

```
core/auth/useAuth.ts:
  - Returns: { user: null, isAuthenticated: false, isLoading: false }
  - Will be replaced with actual auth provider (Clerk, Auth0, or custom JWT)

core/auth/AuthGuard.tsx:
  - Currently: passthrough (renders children)
  - Will be: redirect to /login if not authenticated

The API client already has an interceptor slot for the auth token.
Adding authentication is a matter of:
  1. Implement the auth provider
  2. Replace useAuth stub with real implementation
  3. The interceptor picks up the token automatically
  4. AuthGuard starts enforcing redirects
```

No other code needs to change when auth is added. This is the correct way to prepare for auth without over-engineering it.

---

## Section 15 — Performance Strategy

**Code splitting**: Every feature folder is a lazy-loaded chunk. `React.lazy()` on every page component. `DashboardLayout` is eagerly loaded (it's the shell). Everything inside is lazy.

**Graph rendering**: React Flow handles viewport culling automatically. For graphs with more than 500 nodes, cluster by directory (top-level folder = cluster node, expand on click). Never render all 2000 nodes simultaneously.

**Mermaid in web worker**: Mermaid diagram compilation is CPU-intensive. Run it in a web worker using `workerize-loader`. The main thread remains responsive while Mermaid compiles diagrams.

**Monaco Editor**: Load Monaco asynchronously. Show a styled `<pre>` tag while Monaco loads, then swap when ready. Monaco's bundle is ~2MB — never load it on pages that don't need it.

**TanStack Query cache**: Aggressive caching with content-addressed keys. Dependency graph data for a given commit SHA is immutable — `staleTime: Infinity`. Only invalidate when a new indexing run completes.

**Image/asset optimization**: All icons via Lucide (SVG, tree-shakeable). No raster images except user avatars (future). No heavy image assets.

**Bundle size budget**: `< 500KB` gzipped initial bundle (excluding code-split chunks). Monaco and React Flow are split chunks loaded on demand. Enforce with `vite-bundle-analyzer` in CI.

---

## Section 16 — Accessibility Strategy

Dark theme must meet WCAG AA contrast ratios. All text/background combinations are validated at design token definition time, not after. The `text-secondary` on `bg-base` combination meets 4.5:1.

Keyboard navigation is complete:

- Tab order is logical throughout all pages
- All interactive elements are keyboard-focusable
- `⌘K` opens global search (command palette pattern)
- `⌘J` toggles copilot panel
- Arrow keys navigate graph nodes when graph is focused
- `Escape` closes any open panel or modal

Screen reader support:

- All icons that convey meaning have `aria-label`
- All loading states have `aria-live="polite"` regions
- Graph visualizations have a "list view" alternative accessible via a toggle
- AI streaming responses update `aria-live="polite"` regions

Reduced motion: Check `prefers-reduced-motion` media query. When true, disable all Framer Motion animations (use `initial={false}` on AnimatePresence, set durations to 0). The product remains fully functional without any animation.

---

## Section 17 — Implementation Phases

Each phase is independently testable and deployable. Cursor Agent receives one phase at a time.

---

### Phase 1 — Foundation (Week 1)

**Deliverable**: Running application with routing, design system, and empty pages.

Tasks:

- Initialize Vite + React + TypeScript project
- Configure Tailwind with full design token system
- Install and configure shadcn/ui with CodeGraph theme
- Set up folder structure (all folders, no content)
- Configure TanStack Query client
- Configure Zustand stores (empty implementations)
- Configure React Router with all routes defined (pages are stubs)
- Configure Axios client with interceptors
- Run `openapi-typescript` against backend OpenAPI spec
- Implement all design system primitives (Button, Input, Badge, Skeleton, etc.)
- Implement DashboardLayout shell (TopBar, Sidebar, empty outlet)

**Test**: Navigate to all routes without errors. Design system components render correctly.

---

### Phase 2 — Upload Flow (Week 1)

**Deliverable**: Complete upload experience, upload to IndexingPage transition.

Tasks:

- Implement `features/upload` (DropZone, progress, API)
- Implement `features/indexing` (stepper, event log, SSE connection)
- Implement repository state machine in `repository.store`
- Implement route guards

**Test**: Upload a small ZIP, see progress, reach indexing page, see live events.

---

### Phase 3 — Dashboard Overview (Week 2)

**Deliverable**: Overview page with all stat cards and AI summary.

Tasks:

- Implement `features/dashboard` (all components)
- Implement streaming summary display
- Implement route data loaders
- Implement skeleton loading states for all cards

**Test**: After indexing, dashboard shows populated stats, streaming summary appears.

---

### Phase 4 — Dependency Graph (Week 2–3)

**Deliverable**: Interactive dependency graph with node detail panel.

Tasks:

- Implement custom React Flow node and edge types
- Implement `features/dependency-graph` (all components)
- Implement filter panel
- Implement node selection and detail panel
- Implement graph layout algorithms
- Performance test with 200+ node graph

**Test**: Graph renders, nodes are clickable, filters work, detail panel shows node info.

---

### Phase 5 — Copilot (Week 3)

**Deliverable**: Fully functional AI copilot with streaming and context panel.

Tasks:

- Implement `features/copilot` (all components)
- Implement SSE streaming response in `useStreamingResponse`
- Implement `copilot.store` with full conversation management
- Implement context panel with source display
- Implement feedback mechanism
- Implement conversation history sidebar

**Test**: Ask a question, see streaming response, see context panel populate, feedback works.

---

### Phase 6 — Search (Week 3)

**Deliverable**: Semantic search with code viewer.

Tasks:

- Implement `features/search`
- Implement Monaco Editor integration for code viewing
- Implement filter chips
- Implement result ranking display

**Test**: Search query returns results, clicking result shows file in Monaco.

---

### Phase 7 — Reports and Timeline (Week 4)

**Deliverable**: Report generation, viewing, and timeline visualization.

Tasks:

- Implement `features/reports` (list, viewer, generator)
- Implement `features/timeline` (rail, snapshot, comparison)
- Implement Mermaid web worker renderer

**Test**: Generate a report, view it, navigate timeline, compare two snapshots.

---

### Phase 8 — Quality, Security, Metrics (Week 4–5)

**Deliverable**: All analysis dashboard features.

Tasks:

- Implement `features/quality`
- Implement `features/security`
- Implement `features/metrics`
- Implement all Recharts visualizations
- Implement `features/impact-analysis`

**Test**: Each analysis page shows data, charts render, items are explorable.

---

### Phase 9 — Architecture and Knowledge Graph (Week 5)

**Deliverable**: Architecture diagram view and knowledge graph explorer.

Tasks:

- Implement `features/architecture` with layered React Flow diagram
- Implement `features/knowledge-graph` with semantic node types
- Implement Mermaid sequence diagram rendering

**Test**: Architecture diagram shows correct layers, knowledge graph shows entities.

---

### Phase 10 — Polish and Performance (Week 6)

**Deliverable**: Production-ready frontend with all animations, keyboard shortcuts, and performance optimizations.

Tasks:

- Implement all Framer Motion animations
- Implement `useKeyboardShortcuts` (⌘K, ⌘J, etc.)
- Implement notification system
- Run bundle analysis, optimize chunks
- Accessibility audit (contrast, keyboard, screen reader)
- Responsive layout for tablet
- E2E tests for critical flows (upload, indexing, copilot)
- Error boundary testing (intentionally trigger errors)

**Test**: Full walkthrough of user flow with no errors, all animations present, Lighthouse score ≥90.

---

## Section 18 — Cursor Agent Instructions Format

When directing Cursor Agent at each phase, the prompt structure should be:

```
Context:
  - This is CodeGraph, an AI-powered code analysis platform
  - Tech stack: React 18, TypeScript, Vite, Tailwind, shadcn/ui, TanStack Query, Zustand, React Router
  - Design tokens are defined in tailwind.config.ts
  - API types are in src/core/api/types.ts (auto-generated)
  - Follow the feature folder structure in ARCHITECTURE.md

Task:
  Implement the [feature name] feature.
  Feature folder: src/features/[feature-name]/

  Create:
  - api/[feature].api.ts  (API calls using the Axios client from src/core/api/client.ts)
  - api/[feature].queries.ts  (TanStack Query hooks)
  - components/[FeatureName]Panel.tsx  (main component)
  - [additional components as listed below]

  API endpoints to use:
  [list specific endpoints]

  Do NOT:
  - Create global state (use local state unless specified)
  - Import from other feature folders
  - Install new dependencies

  Reference:
  - Similar completed feature: src/features/[comparable feature]
```

This prompt format minimizes context, maximizes specificity, and prevents scope creep. The architectural decisions in this document mean Cursor Agent never needs to make architectural decisions — only implementation decisions.

---

## Closing Architectural Principles

Three principles underlie every decision in this document:

**Isolation over convenience.** It would be more convenient to have a global `api.ts` with every endpoint, a global `types.ts` with every type, a single large Zustand store. Convenient code is code that becomes unmaintainable. Every feature owns its API, its types, its local state. Cross-feature sharing is the exception, documented explicitly, not the default.

**Explicit over implicit.** Loading states are explicitly modeled. Error states are explicitly coded per error type. State transitions are explicitly named. There are no magic behaviors, no assumed states, no "it just works until it doesn't." Every state the application can be in is accounted for in the component design.

**The user knows what's happening.** Streaming responses, live progress steps, context panel showing retrieved sources — every AI operation is transparent. The user never stares at a spinner wondering what the system is doing. Every non-trivial operation communicates its progress. This is what separates a tool engineers trust from a tool engineers tolerate.
