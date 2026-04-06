# Phase 6: Mode 3 Workspace - Research

**Researched:** 2026-03-06
**Domain:** Full-stack agency dashboard -- Next.js 16 frontend + Django DRF backend + SSE real-time + multi-tenant auth
**Confidence:** HIGH

## Summary

Phase 6 builds the agency-facing web dashboard on top of a substantial existing backend. The Django backend already has: DRF viewsets for HITL and WorkflowRun (AllowAny permissions, needing auth enforcement), HaznMemory with search_memory/correct_memory APIs, Celery task for workflow execution (run_workflow.delay()), Deliverable model with QA scoring, and a User model via django-allauth (cookiecutter-django setup). The Next.js 16 frontend is a bare scaffold (default create-next-app page with Tailwind 4 + React 19) -- everything needs to be built.

The architecture follows a clear split: Django serves the API (DRF + allauth headless + SSE endpoints), Next.js serves the UI (shadcn/ui + TanStack Query + SSE client). The Next.js proxy.ts (v16 replacement for middleware.ts) rewrites `/api/*` requests to Django, avoiding CORS entirely. Authentication uses django-allauth in HEADLESS_ONLY mode with session tokens for browser clients, supporting magic link (via Resend), email+password, and OAuth (Google, Facebook, Apple).

**Primary recommendation:** Build the Django API layer first (auth + workspace endpoints), then the Next.js frontend. Use django-eventstream for SSE (it integrates with DRF and provides Redis pub/sub for multi-process delivery). Follow the Agent OS reference codebase for shadcn/ui patterns (MemoryBlockCard, ChatPanel, workspace layout) but adapt to the Hazn data model.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- All three auth methods from day one: magic links (via Resend, already in stack), email+password, and OAuth (Google, Facebook, Apple/iCloud)
- django-allauth handles all auth methods on the same User model
- Multiple users per agency with two roles: Admin and Member
- Admin: full access -- manage team, end-clients, credentials, approve/reject deliverables, trigger workflows, configure settings
- Member: view dashboard, trigger workflows, view deliverables and memory. Cannot manage team, credentials, or agency settings
- Collapsible sidebar layout: full sidebar with labels that collapses to icons on toggle or small screens
- Grouped sidebar sections: Overview (Dashboard), Clients (End-Clients list), Work (Workflows, Approvals, Deliverables), Intelligence (Memory Inspector), Settings
- End-client list in sidebar below main nav for scoping all views to a specific client
- Dashboard landing view: status summary cards at top + chronological activity timeline below
- Global Cmd-K search bar in header across end-clients, workflows, deliverables, HITL items
- Light mode default with dark mode toggle
- Friendly and branded visual feel (Notion/Intercom-like): rounded corners, color accents, personality
- Illustrations + CTAs for empty states
- Responsive design: works on tablets and mobile
- shadcn/ui (Radix UI + Tailwind CSS) for UI components
- TanStack Query for server state management with SSE for real-time updates
- SSE from day one for: workflow status changes, HITL queue updates, deliverable notifications, cost accumulation
- In-app notification bell with unread count badge in header
- Memory Inspector: structured cards, edit craft learnings only (archival), client context read-only, inline edit + save, both "by end-client" and "by agent type" views, semantic search, memory health stats, bulk select + delete
- Workflow catalog page: available workflows as cards, guided form, estimated cost range, live cost tracking, chat-style monitoring, inline HITL approval cards, cancel and clone+re-run
- Dedicated HITL Queue page + inline in workflow chat view
- Deliverables: HTML files rendered inline, public shareable links with unique token + expiry, QA badge (PASS/CONDITIONAL/FAIL with score) + expandable QA report

### Claude's Discretion
- Memory metadata display (creation date, source workflow, confidence score) -- decide what level of detail adds value
- SSE implementation approach (django-eventstream vs custom SSE endpoints)
- Exact sidebar section groupings and icon choices
- Notification bell implementation details
- Search implementation (client-side filtering vs server-side search endpoint)
- Deliverable storage format and file organization
- Share link token generation and expiry configuration
- Auth flow UX details (magic link email template, OAuth redirect flow)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| WS-01 | Agency dashboard shows active projects, running workflows, deliverables | Dashboard API aggregation endpoint, TanStack Query polling + SSE for real-time status, shadcn/ui Card/Badge components |
| WS-02 | Memory Inspector lets L2 agencies view and edit agent memory blocks | Existing HaznMemory.search_memory() and correct_memory() APIs, new DRF endpoints to proxy Letta calls, MemoryBlockCard pattern from Agent OS reference |
| WS-03 | End-Client Manager for creating/managing L3 profiles, brand docs, tool connections | DRF ModelViewSet for EndClient, BrandVoice, VaultCredential CRUD, agency FK scoping for multi-tenant isolation |
| WS-04 | Workflow Trigger lets agencies run workflows from UI | Existing run_workflow Celery task, new DRF endpoint to accept trigger request + return WorkflowRun ID, workflow YAML catalog endpoint, SSE for status updates |
| WS-05 | HITL Queue shows pending approvals across all end-clients | Existing HITLItemViewSet (needs auth scoping by agency FK), cross-client filtering, SSE for new item notifications |
| WS-06 | Deliverables view for approving and sharing agent outputs | Existing Deliverable model with QA scoring, new endpoints for approval actions and share link generation, HTML rendering in iframe/sandboxed div |
</phase_requirements>

## Standard Stack

### Core (Backend - Django)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| django-allauth[headless] | 65.x | Auth: magic link, email+password, OAuth (HEADLESS_ONLY mode) | Already installed (allauth, allauth.account, allauth.socialaccount). Add allauth.headless to INSTALLED_APPS |
| django-eventstream | latest | SSE for real-time push (workflow status, HITL, deliverables, costs) | DRF-compatible, Redis pub/sub for multi-process, database persistence optional, handles reconnection |
| daphne | latest | ASGI server required by django-eventstream | Standard ASGI server for Django streaming |
| django-cors-headers | latest | CORS headers (fallback if proxy.ts not used in dev) | Standard Django CORS library |
| djangorestframework | existing | API endpoints | Already installed and configured |
| django-filter | latest | DRF filtering for list endpoints (HITL, deliverables, workflows) | Standard DRF companion for queryset filtering |

### Core (Frontend - Next.js)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| shadcn/ui (via CLI) | latest | UI component library (Radix UI + Tailwind CSS) | Locked decision. Agent OS reference uses shadcn/ui. Run `npx shadcn@latest init` |
| @tanstack/react-query | ^5.x | Server state management, caching, polling | Locked decision. Handles API data fetching, cache invalidation on SSE events |
| lucide-react | latest | Icon library | Standard with shadcn/ui (Agent OS reference uses it) |
| class-variance-authority | latest | Component variant styling | Required by shadcn/ui |
| clsx + tailwind-merge | latest | Conditional class merging | Required by shadcn/ui (cn() utility) |
| cmdk | latest | Cmd-K command palette (search) | shadcn/ui Command component wraps cmdk |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| next-themes | latest | Dark mode toggle with system detection | Theme switching (light/dark mode) |
| zustand | ^5.x | Client-only UI state (sidebar collapsed, selected client, notification count) | Local UI state that doesn't come from server |
| date-fns | latest | Date formatting for timestamps, relative time ("2 hours ago") | Activity timeline, memory dates, workflow durations |
| sonner | latest | Toast notifications (inline feedback for actions) | shadcn/ui's recommended toast component |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| django-eventstream | Custom SSE views with StreamingHttpResponse | Custom is simpler for basic cases but lacks Redis pub/sub, reconnection ID tracking, and DRF integration. django-eventstream handles all of these |
| zustand | React Context | Zustand is simpler for cross-component state without provider nesting. Context works for small state |
| cmdk | Custom search | cmdk provides keyboard nav, fuzzy search, grouping. Building custom would take days for the same quality |
| next-themes | Custom CSS variables toggle | next-themes handles SSR, system preference, localStorage. Custom solution misses flash-of-wrong-theme |

**Installation (Backend):**
```bash
pip install "django-allauth[headless]" django-eventstream daphne django-cors-headers django-filter
```

**Installation (Frontend):**
```bash
cd hazn_platform/frontend
npx shadcn@latest init
npm install @tanstack/react-query lucide-react next-themes zustand date-fns sonner
```

## Architecture Patterns

### Recommended Project Structure (Frontend)
```
hazn_platform/frontend/src/
├── app/
│   ├── (auth)/                    # Auth pages (login, signup, magic-link)
│   │   ├── login/page.tsx
│   │   ├── signup/page.tsx
│   │   └── layout.tsx             # Centered card layout for auth
│   ├── (workspace)/               # Dashboard pages (authenticated)
│   │   ├── layout.tsx             # Sidebar + header layout
│   │   ├── page.tsx               # Dashboard landing
│   │   ├── clients/
│   │   │   ├── page.tsx           # End-client list
│   │   │   └── [id]/page.tsx      # End-client detail/edit
│   │   ├── workflows/
│   │   │   ├── page.tsx           # Workflow catalog
│   │   │   └── [id]/page.tsx      # Workflow run monitoring (chat view)
│   │   ├── approvals/page.tsx     # HITL Queue
│   │   ├── deliverables/
│   │   │   ├── page.tsx           # Deliverables list
│   │   │   └── [id]/page.tsx      # Deliverable detail + QA report
│   │   ├── memory/page.tsx        # Memory Inspector
│   │   └── settings/page.tsx      # Agency settings, team management
│   ├── share/[token]/page.tsx     # Public share page (no auth)
│   ├── layout.tsx                 # Root layout (providers, fonts)
│   └── globals.css                # Tailwind + shadcn/ui theme vars
├── components/
│   ├── ui/                        # shadcn/ui primitives (auto-generated)
│   ├── layout/
│   │   ├── sidebar.tsx            # Collapsible sidebar with nav groups
│   │   ├── header.tsx             # Search bar + notification bell + user menu
│   │   └── client-switcher.tsx    # End-client scope selector
│   ├── dashboard/
│   │   ├── status-cards.tsx       # Summary cards (running, pending, ready)
│   │   └── activity-timeline.tsx  # Chronological activity feed
│   ├── memory/
│   │   ├── memory-block-card.tsx  # Editable memory card (adapted from Agent OS)
│   │   ├── memory-search.tsx      # Semantic search input
│   │   └── memory-health.tsx      # Health stats display
│   ├── workflow/
│   │   ├── workflow-card.tsx      # Catalog card with trigger action
│   │   ├── workflow-chat.tsx      # Chat-style monitoring view
│   │   ├── phase-stepper.tsx      # Phase progress indicator
│   │   └── cost-tracker.tsx       # Live cost display
│   ├── hitl/
│   │   ├── hitl-item-card.tsx     # Approval card with approve/reject
│   │   └── hitl-queue.tsx         # Filterable queue list
│   ├── deliverables/
│   │   ├── deliverable-card.tsx   # Card with QA badge
│   │   ├── qa-report.tsx          # Expandable QA report
│   │   └── share-dialog.tsx       # Share link generation dialog
│   └── empty-states/
│       └── empty-state.tsx        # Reusable illustrated empty state
├── lib/
│   ├── api.ts                     # API client (fetch wrapper with auth headers)
│   ├── utils.ts                   # cn() utility for shadcn/ui
│   ├── auth.ts                    # Auth helpers (session check, login redirect)
│   └── sse.ts                     # SSE client hook (EventSource wrapper)
├── hooks/
│   ├── use-auth.ts                # Auth state hook
│   ├── use-sse.ts                 # SSE subscription hook
│   ├── use-client-scope.ts        # Selected end-client scope
│   └── use-debounce.ts            # Debounce hook for search
├── stores/
│   ├── ui-store.ts                # Sidebar collapsed, theme, selected client
│   └── notification-store.ts      # Notification bell state
├── providers/
│   └── providers.tsx              # QueryClient + ThemeProvider + AuthProvider
└── types/
    └── api.ts                     # TypeScript types matching DRF serializers
```

### Recommended Project Structure (Backend - New API Endpoints)
```
hazn_platform/hazn_platform/
├── workspace/                      # New Django app for workspace-specific APIs
│   ├── __init__.py
│   ├── apps.py
│   ├── urls.py                    # DRF router registration
│   ├── views.py                   # Agency, EndClient, Memory, Workflow, Deliverable viewsets
│   ├── serializers.py             # Workspace-specific serializers
│   ├── permissions.py             # AgencyMember, AgencyAdmin permission classes
│   ├── filters.py                 # django-filter filtersets
│   ├── sse_views.py               # SSE streaming endpoints using django-eventstream
│   ├── share_views.py             # Public share link views (no auth)
│   └── notifications.py           # Notification model + helpers
├── users/
│   ├── models.py                  # Add agency FK + role field to User model
│   └── ...
```

### Pattern 1: Multi-Tenant API Scoping
**What:** Every API query is scoped by the authenticated user's agency FK. No data from other agencies is ever returned.
**When to use:** Every single API endpoint in the workspace.
**Example:**
```python
# permissions.py
from rest_framework.permissions import IsAuthenticated

class IsAgencyMember(IsAuthenticated):
    """Ensure user belongs to an agency."""
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return hasattr(request.user, 'agency') and request.user.agency is not None

class IsAgencyAdmin(IsAgencyMember):
    """Ensure user is an agency admin."""
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.agency_role == 'admin'

# views.py -- every viewset scopes by agency
class EndClientViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAgencyMember]

    def get_queryset(self):
        return EndClient.objects.filter(agency=self.request.user.agency)

    def perform_create(self, serializer):
        serializer.save(agency=self.request.user.agency)
```

### Pattern 2: SSE with TanStack Query Invalidation
**What:** SSE events trigger TanStack Query cache invalidation so UI updates automatically without polling.
**When to use:** Workflow status changes, HITL queue updates, deliverable notifications, cost updates.
**Example:**
```typescript
// hooks/use-sse.ts
import { useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';

export function useSSE(channels: string[]) {
  const queryClient = useQueryClient();

  useEffect(() => {
    const url = `/api/events/?${channels.map(c => `channel=${c}`).join('&')}`;
    const source = new EventSource(url);

    source.onmessage = (event) => {
      const data = JSON.parse(event.data);

      // Invalidate relevant queries based on event type
      switch (data.type) {
        case 'workflow_status':
          queryClient.invalidateQueries({ queryKey: ['workflows', data.run_id] });
          queryClient.invalidateQueries({ queryKey: ['dashboard'] });
          break;
        case 'hitl_new':
          queryClient.invalidateQueries({ queryKey: ['hitl'] });
          break;
        case 'deliverable_ready':
          queryClient.invalidateQueries({ queryKey: ['deliverables'] });
          break;
        case 'cost_update':
          queryClient.invalidateQueries({ queryKey: ['workflows', data.run_id] });
          break;
      }
    };

    return () => source.close();
  }, [channels, queryClient]);
}
```

### Pattern 3: Next.js 16 Proxy for Django API
**What:** Use proxy.ts (Next.js 16 replacement for middleware.ts) to rewrite `/api/*` requests to the Django backend, eliminating CORS issues.
**When to use:** All API calls from the frontend.
**Example:**
```typescript
// proxy.ts (project root or src/)
import { NextResponse, NextRequest } from 'next/server';

const DJANGO_API_URL = process.env.DJANGO_API_URL || 'http://localhost:8001';

export function proxy(request: NextRequest) {
  if (request.nextUrl.pathname.startsWith('/api/')) {
    const url = new URL(request.nextUrl.pathname + request.nextUrl.search, DJANGO_API_URL);
    return NextResponse.rewrite(url);
  }
}

export const config = {
  matcher: '/api/:path*',
};
```

**Important:** Django uses trailing slashes by default. Set `skipTrailingSlashRedirect: true` in next.config.ts to prevent Next.js from stripping trailing slashes with 308 redirects.

### Pattern 4: django-allauth Headless Auth Flow
**What:** Configure django-allauth in HEADLESS_ONLY mode for API-only auth, with session tokens for browser clients.
**When to use:** All authentication flows (login, signup, magic link, OAuth).
**Example:**
```python
# settings/base.py additions
INSTALLED_APPS += ['allauth.headless']
HEADLESS_ONLY = True
HEADLESS_FRONTEND_URLS = {
    "account_confirm_email": "http://localhost:3000/auth/verify-email/{key}",
    "account_reset_password_from_key": "http://localhost:3000/auth/reset-password/{key}",
    "account_signup": "http://localhost:3000/auth/signup",
    "socialaccount_login_cancelled": "http://localhost:3000/auth/login",
    "socialaccount_login_error": "http://localhost:3000/auth/login",
}
# Configure login by code (magic link) for passwordless auth
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_LOGIN_BY_CODE_ENABLED = True
```

### Pattern 5: SSE Backend with django-eventstream
**What:** Django sends SSE events for workflow status, HITL updates, and deliverable notifications via django-eventstream with Redis pub/sub.
**When to use:** All real-time updates in the dashboard.
**Example:**
```python
# sse_views.py
from django_eventstream import send_event

# When workflow status changes (called from executor/session):
send_event(
    f'agency-{agency_id}',  # channel scoped to agency
    'message',
    {
        'type': 'workflow_status',
        'run_id': str(workflow_run.pk),
        'status': workflow_run.status,
        'total_cost': str(workflow_run.total_cost),
    }
)

# URL config for SSE endpoint
urlpatterns += [
    path(
        'api/events/',
        include(django_eventstream.urls),
        {'format-channels': ['agency-{agency_id}']},
    ),
]
```

### Anti-Patterns to Avoid
- **Polling instead of SSE:** Do NOT use TanStack Query polling intervals for real-time data. Use SSE events to invalidate queries instead -- this gives instant updates with zero wasted requests.
- **Frontend-only auth checks:** Do NOT rely solely on frontend route guards. Every DRF viewset MUST check permissions and scope data by agency FK. Frontend auth is UX only.
- **Global state for server data:** Do NOT put API response data in zustand stores. Use TanStack Query for all server state. zustand is only for UI-only state (sidebar collapsed, theme, selected client filter).
- **Building custom SSE reconnection logic:** Do NOT hand-roll reconnection. EventSource API handles reconnection automatically. django-eventstream tracks Last-Event-ID for reliable delivery.
- **N+1 queries in list views:** Use `select_related` and `prefetch_related` on all DRF viewset querysets that reference foreign keys (agency, end_client, workflow_run).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| SSE server | Custom StreamingHttpResponse with async generators | django-eventstream | Handles reconnection, Last-Event-ID, Redis pub/sub for multi-process, DRF integration |
| Command palette | Custom search modal with keyboard handling | shadcn/ui Command (wraps cmdk) | Fuzzy search, keyboard nav, grouping, accessibility -- 100+ edge cases |
| Dark mode | Custom CSS variable toggle + localStorage | next-themes | Handles SSR flash prevention, system preference, localStorage, proper hydration |
| Toast notifications | Custom floating div system | sonner (shadcn/ui recommended) | Animation, queue management, auto-dismiss, accessibility, undo support |
| API data fetching | Custom fetch + useState + useEffect | TanStack Query | Caching, deduplication, background refetching, optimistic updates, SSE invalidation integration |
| Auth session management | Custom JWT handling | django-allauth headless session tokens | Token refresh, CSRF, cookie security, OAuth state management all handled |
| Date formatting | Custom relative time ("2 hours ago") logic | date-fns formatDistanceToNow | Handles edge cases (just now, minutes ago, yesterday, etc.), i18n ready |
| Form validation | Custom validation functions | React 19 useActionState + server validation | DRF serializer validation is the source of truth; frontend shows errors from API |
| Share token generation | Custom random string | secrets.token_urlsafe(32) | Cryptographically secure, URL-safe, standard Python library |

**Key insight:** The "I'll just build a simple version" trap is especially dangerous in this phase because the workspace has many interacting features (auth, SSE, search, notifications, memory editing). Using established libraries for each concern keeps the integration surface manageable.

## Common Pitfalls

### Pitfall 1: Next.js 16 Trailing Slash vs Django
**What goes wrong:** Next.js strips trailing slashes with 308 redirects, but Django URLs use trailing slashes by default. API calls to `/api/workflows/` get redirected to `/api/workflows` which returns 404 from Django.
**Why it happens:** Next.js behavior changed and it conflicts with Django's APPEND_SLASH convention.
**How to avoid:** Set `skipTrailingSlashRedirect: true` in next.config.ts. Use trailing slashes in all API URLs in the frontend fetch calls.
**Warning signs:** 308 redirect responses from the Next.js proxy, 404s from Django.

### Pitfall 2: SSE Connection Limits per Browser
**What goes wrong:** Browsers limit EventSource connections to 6 per domain (HTTP/1.1). If you open multiple SSE connections for different event types, you quickly exhaust the limit.
**Why it happens:** Each EventSource is a persistent HTTP connection. 6 is the browser-enforced limit per origin.
**How to avoid:** Use a single SSE connection with a channel-based multiplexing approach (django-eventstream supports multiple channels per connection). Pass channel names as query params: `/api/events/?channel=workflow&channel=hitl&channel=deliverables`.
**Warning signs:** SSE connections failing silently, events not arriving on some pages.

### Pitfall 3: User Model Migration for Agency FK
**What goes wrong:** Adding an agency FK and role field to the existing User model requires a migration with nullable fields (existing users have no agency). Forgetting to make it nullable causes migration failures.
**Why it happens:** The User model already has data (at minimum the superuser created during setup).
**How to avoid:** Add `agency = models.ForeignKey(Agency, null=True, blank=True, ...)` and `agency_role = models.CharField(max_length=20, default='member')`. Superusers and L1 staff have agency=None.
**Warning signs:** Migration errors on `NOT NULL constraint failed`.

### Pitfall 4: TanStack Query Stale Data After SSE Invalidation
**What goes wrong:** SSE event fires, invalidateQueries runs, but the UI still shows stale data because the refetch was too fast and hit a cache.
**Why it happens:** TanStack Query has configurable stale times. If staleTime is set too high, invalidation may not trigger an immediate refetch.
**How to avoid:** Set `staleTime: 0` for queries that depend on SSE invalidation (workflows, HITL items, deliverables). Use `refetchType: 'active'` in invalidateQueries to only refetch currently mounted queries.
**Warning signs:** UI updates delayed or requires manual page refresh despite SSE events arriving.

### Pitfall 5: django-eventstream Requires ASGI (Daphne)
**What goes wrong:** django-eventstream requires an ASGI server (Daphne) for streaming responses. Running Django with WSGI (gunicorn sync) causes SSE connections to hang or timeout.
**Why it happens:** WSGI is synchronous and cannot hold persistent connections for SSE. ASGI supports async streaming.
**How to avoid:** Add `daphne` to INSTALLED_APPS (before django.contrib.staticfiles). Set `ASGI_APPLICATION = 'config.asgi.application'`. In Docker, run `daphne config.asgi:application` instead of gunicorn. For development, `daphne config.asgi:application --port 8001`.
**Warning signs:** SSE connections timing out after 30 seconds, "connection refused" on event endpoints.

### Pitfall 6: Memory Inspector Letta API Calls from Frontend
**What goes wrong:** Calling Letta directly from the frontend exposes the Letta server URL and bypasses agency scoping. Memory edits go through without authorization checks.
**Why it happens:** Temptation to skip the Django proxy and call Letta directly for performance.
**How to avoid:** All Letta interactions go through Django DRF endpoints. The DRF endpoint verifies the user's agency, resolves the correct agent_id for the end-client, and calls HaznMemory methods. Never expose Letta URLs to the frontend.
**Warning signs:** Letta URLs appearing in frontend network requests.

### Pitfall 7: OAuth Provider Callback URLs
**What goes wrong:** OAuth providers (Google, Facebook, Apple) need callback URLs registered in their developer consoles. In headless mode, the callback still goes through Django (not the SPA), but the redirect after auth goes to the SPA.
**Why it happens:** OAuth requires server-side token exchange. django-allauth handles the callback at `/accounts/google/login/callback/` even in headless mode.
**How to avoid:** Keep `path("accounts/", include("allauth.urls"))` in urls.py even with HEADLESS_ONLY. Configure HEADLESS_FRONTEND_URLS to redirect post-auth to the SPA. Register `http://localhost:8001/accounts/google/login/callback/` (Django) as the OAuth callback URL, not the Next.js URL.
**Warning signs:** OAuth login redirects to a Django template page instead of the SPA.

## Code Examples

### Example 1: API Client with Auth Headers
```typescript
// lib/api.ts
const API_BASE = '/api';

async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    credentials: 'include', // Send session cookies
  });

  if (response.status === 401) {
    // Redirect to login
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }

  return response.json();
}

export const api = {
  get: <T>(endpoint: string) => fetchAPI<T>(endpoint),
  post: <T>(endpoint: string, data: unknown) =>
    fetchAPI<T>(endpoint, { method: 'POST', body: JSON.stringify(data) }),
  patch: <T>(endpoint: string, data: unknown) =>
    fetchAPI<T>(endpoint, { method: 'PATCH', body: JSON.stringify(data) }),
  delete: <T>(endpoint: string) =>
    fetchAPI<T>(endpoint, { method: 'DELETE' }),
};
```

### Example 2: Workflow Trigger API Endpoint
```python
# workspace/views.py
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

class WorkflowTriggerView(APIView):
    permission_classes = [IsAgencyMember]

    def post(self, request):
        """Trigger a workflow for an end-client."""
        workflow_name = request.data.get('workflow_name')
        end_client_id = request.data.get('end_client_id')

        # Verify end-client belongs to user's agency
        try:
            end_client = EndClient.objects.get(
                pk=end_client_id,
                agency=request.user.agency,
            )
        except EndClient.DoesNotExist:
            return Response(
                {'error': 'End client not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Trigger async workflow
        result = run_workflow.delay(
            workflow_name=workflow_name,
            l2_agency_id=str(request.user.agency_id),
            l3_client_id=str(end_client.pk),
            triggered_by=request.user.email,
        )

        return Response({
            'celery_task_id': result.id,
            'message': f'Workflow {workflow_name} triggered',
        }, status=status.HTTP_202_ACCEPTED)
```

### Example 3: Share Link Generation
```python
# workspace/share_views.py
import secrets
from datetime import timedelta
from django.utils import timezone
from django.http import JsonResponse
from rest_framework.views import APIView

class ShareLinkView(APIView):
    permission_classes = [IsAgencyMember]

    def post(self, request, deliverable_id):
        """Generate a public share link for a deliverable."""
        deliverable = Deliverable.objects.get(
            pk=deliverable_id,
            workflow_run__agency=request.user.agency,
        )

        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(days=30)  # Default 30-day expiry

        ShareLink.objects.create(
            deliverable=deliverable,
            token=token,
            expires_at=expires_at,
            created_by=request.user,
        )

        share_url = f"{request.build_absolute_uri('/share/')}{token}"
        return Response({
            'share_url': share_url,
            'token': token,
            'expires_at': expires_at.isoformat(),
        })
```

### Example 4: Collapsible Sidebar Component
```typescript
// components/layout/sidebar.tsx
// Source: Adapted from shadcn/ui Sidebar pattern + Agent OS workspace layout
'use client';

import { cn } from '@/lib/utils';
import {
  LayoutDashboard, Users, Play, CheckSquare,
  FileText, Brain, Settings, ChevronLeft
} from 'lucide-react';
import { useUIStore } from '@/stores/ui-store';

const NAV_GROUPS = [
  {
    label: 'Overview',
    items: [
      { icon: LayoutDashboard, label: 'Dashboard', href: '/' },
    ],
  },
  {
    label: 'Clients',
    items: [
      { icon: Users, label: 'End-Clients', href: '/clients' },
    ],
  },
  {
    label: 'Work',
    items: [
      { icon: Play, label: 'Workflows', href: '/workflows' },
      { icon: CheckSquare, label: 'Approvals', href: '/approvals' },
      { icon: FileText, label: 'Deliverables', href: '/deliverables' },
    ],
  },
  {
    label: 'Intelligence',
    items: [
      { icon: Brain, label: 'Memory Inspector', href: '/memory' },
    ],
  },
];

export function Sidebar() {
  const { sidebarCollapsed, toggleSidebar } = useUIStore();

  return (
    <aside className={cn(
      'flex h-screen flex-col border-r bg-background transition-all duration-200',
      sidebarCollapsed ? 'w-16' : 'w-64'
    )}>
      {/* Logo + collapse toggle */}
      <div className="flex h-14 items-center justify-between border-b px-4">
        {!sidebarCollapsed && <span className="font-bold text-lg">Hazn</span>}
        <button onClick={toggleSidebar}>
          <ChevronLeft className={cn('h-4 w-4 transition-transform', sidebarCollapsed && 'rotate-180')} />
        </button>
      </div>

      {/* Nav groups */}
      <nav className="flex-1 overflow-y-auto p-2">
        {NAV_GROUPS.map((group) => (
          <div key={group.label} className="mb-4">
            {!sidebarCollapsed && (
              <span className="px-3 text-xs font-medium uppercase text-muted-foreground">
                {group.label}
              </span>
            )}
            {group.items.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className="flex items-center gap-3 rounded-md px-3 py-2 text-sm hover:bg-accent"
              >
                <item.icon className="h-4 w-4 shrink-0" />
                {!sidebarCollapsed && <span>{item.label}</span>}
              </a>
            ))}
          </div>
        ))}
      </nav>

      {/* Client switcher at bottom */}
      {/* Settings at bottom */}
    </aside>
  );
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| middleware.ts | proxy.ts | Next.js 16.0.0 | File renamed, function renamed from `middleware()` to `proxy()`. Codemod available: `npx @next/codemod@canary middleware-to-proxy .` |
| django-allauth + DRF token auth | django-allauth headless mode | allauth 65.x (2024-2025) | Built-in headless API with session tokens, no need for dj-rest-auth or djoser |
| Separate CORS library + manual CSRF | Next.js proxy rewrite | Next.js 13+ | Proxy eliminates CORS entirely by making API calls same-origin |
| REST_FRAMEWORK Token auth | allauth headless session tokens | 2025 | Session-based auth for browser clients is simpler and more secure (httpOnly cookies) |
| Redux Toolkit for all state | TanStack Query (server) + zustand (client) | 2024+ | Clear separation: server state in TanStack Query, UI state in zustand. No more duplicate state |

**Deprecated/outdated:**
- `middleware.ts`: Renamed to `proxy.ts` in Next.js 16. Still works but deprecated. Use `proxy.ts`.
- `dj-rest-auth` / `djoser`: No longer needed when using django-allauth headless mode. allauth headless provides the same API endpoints built-in.
- `ACCOUNT_LOGIN_METHODS = {"username"}`: Current setting in base.py. Must change to `{"email"}` for magic link support (allauth 65.x uses email-based login by code).

## Claude's Discretion Recommendations

### SSE Implementation: Use django-eventstream
**Recommendation:** django-eventstream over custom SSE endpoints.
**Reasoning:** django-eventstream provides Redis pub/sub (critical since send_event() calls happen in Celery workers, not in the SSE request handler process), automatic Last-Event-ID tracking for reconnection, DRF renderer integration, and per-channel authorization. Custom SSE would require building all of this. The only downside is the daphne/ASGI requirement, but this is a one-time setup.

### Memory Metadata Display: Show creation date + source + confidence
**Recommendation:** Display creation date, source workflow name, and confidence score on each memory card. Hide passage IDs and agent IDs (internal implementation details).
**Reasoning:** Agencies need to understand when a learning was acquired (is it stale?), where it came from (which workflow produced it?), and how confident the system is. This is the minimum metadata needed for informed memory management without overwhelming the user.

### Search Implementation: Server-side search endpoint
**Recommendation:** Server-side search API endpoint that queries across EndClients, WorkflowRuns, HITLItems, and Deliverables. Return top-N results per category. cmdk renders results in the Cmd-K modal.
**Reasoning:** Client-side filtering would require loading all data upfront (slow, memory-heavy for agencies with many clients). Server-side search allows database-level filtering and keeps the client lightweight. Use Django ORM `Q` objects with `icontains` for v1 -- full-text search can come later if needed.

### Notification Bell: In-memory count + SSE push
**Recommendation:** Track unread count in a zustand store. SSE events increment the count. Clicking the bell opens a dropdown fetching recent notifications from a lightweight API endpoint. No separate Notification model for v1 -- derive notifications from recent HITL items (pending), deliverables (ready), and workflow failures.
**Reasoning:** A separate notification model adds complexity without value in v1. The data already exists in HITLItem, Deliverable, and WorkflowRun tables. A simple aggregation query returns "what needs attention." SSE events push new items in real-time.

### Share Link Token: secrets.token_urlsafe(32) + 30-day default expiry
**Recommendation:** Use Python's `secrets.token_urlsafe(32)` for token generation. Store in a ShareLink model with deliverable FK, token (indexed), expires_at, created_by. Public view at `/share/{token}` requires no auth and renders the HTML deliverable.
**Reasoning:** 32 bytes of URL-safe base64 provides 256 bits of entropy -- more than sufficient for public share links. 30-day default expiry balances usability with security. A simple Django model tracks link metadata for potential future analytics (who shared what, when).

### Deliverable Storage: HTML content in Deliverable model + file system
**Recommendation:** Store deliverable HTML content in WorkflowPhaseOutput.content (already JSONField, can hold HTML string). For larger deliverables (full websites), store as files in MEDIA_ROOT with a file path reference. The deliverables view renders HTML in a sandboxed iframe.
**Reasoning:** Most deliverables (blog posts, email templates, landing pages) are single HTML files under 1MB. Storing in the database (existing JSONField) is simpler than file management for small outputs. For multi-file deliverables (full websites), use Vercel preview URLs (already implemented in QA-04).

## Open Questions

1. **User-Agency FK Migration Strategy**
   - What we know: User model exists with no agency FK. Need to add agency FK + role field. Existing superuser has no agency.
   - What's unclear: Whether to create a separate AgencyMembership model (M2M) or add direct FK on User. Direct FK is simpler but limits users to one agency.
   - Recommendation: Use direct FK (`agency = ForeignKey(Agency, null=True)`) for v1. Multi-agency access is not a v1 requirement. Nullable FK means superusers and L1 staff work without an agency.

2. **ASGI/Daphne Integration with Docker Compose**
   - What we know: django-eventstream requires ASGI (daphne). Current Docker setup likely uses gunicorn (WSGI).
   - What's unclear: Whether to run Django entirely on daphne or split WSGI (gunicorn) for regular requests and ASGI (daphne) for SSE.
   - Recommendation: Switch entirely to daphne for simplicity. Daphne handles both sync views and async SSE. Only split if performance testing reveals issues.

3. **SSE Channel Authorization**
   - What we know: django-eventstream supports channel permissions via a channel manager class.
   - What's unclear: How to pass the authenticated user's agency ID into the SSE channel subscription to ensure users only receive events for their own agency.
   - Recommendation: Use session-cookie auth for SSE (EventSource uses same origin, cookies sent automatically). django-eventstream's `can_read_channel()` checks request.user.agency and verifies channel name matches.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest + pytest-django (backend), vitest (frontend -- not yet configured) |
| Config file | hazn_platform/pyproject.toml (backend), frontend needs vitest.config.ts (Wave 0) |
| Quick run command | `cd hazn_platform && python -m pytest tests/ -x --tb=short -q` |
| Full suite command | `cd hazn_platform && python -m pytest` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| WS-01 | Dashboard API returns running workflows, pending approvals, ready deliverables for agency | unit | `pytest tests/test_workspace_dashboard.py -x` | No -- Wave 0 |
| WS-02 | Memory Inspector API proxies search_memory/correct_memory scoped by agency | unit | `pytest tests/test_workspace_memory.py -x` | No -- Wave 0 |
| WS-03 | EndClient CRUD API scoped by agency FK, brand voice and credential management | unit | `pytest tests/test_workspace_clients.py -x` | No -- Wave 0 |
| WS-04 | Workflow trigger API validates agency ownership and dispatches Celery task | unit | `pytest tests/test_workspace_workflows.py -x` | No -- Wave 0 |
| WS-05 | HITL Queue API returns pending items across all end-clients for agency | unit | `pytest tests/test_workspace_hitl.py -x` | No -- Wave 0 |
| WS-06 | Deliverables API with approval actions, share link generation | unit | `pytest tests/test_workspace_deliverables.py -x` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `cd hazn_platform && python -m pytest tests/ -x --tb=short -q`
- **Per wave merge:** `cd hazn_platform && python -m pytest`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_workspace_dashboard.py` -- covers WS-01
- [ ] `tests/test_workspace_memory.py` -- covers WS-02
- [ ] `tests/test_workspace_clients.py` -- covers WS-03
- [ ] `tests/test_workspace_workflows.py` -- covers WS-04
- [ ] `tests/test_workspace_hitl.py` -- covers WS-05
- [ ] `tests/test_workspace_deliverables.py` -- covers WS-06
- [ ] Frontend test infrastructure: `npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom` + `vitest.config.ts`
- [ ] User model migration adding agency FK + role field (prerequisite for all workspace tests)

## Sources

### Primary (HIGH confidence)
- Next.js 16 proxy.ts documentation -- https://nextjs.org/docs/app/api-reference/file-conventions/proxy -- full proxy.ts API, matcher config, CORS handling, trailing slash fix
- django-allauth headless installation -- https://docs.allauth.org/en/dev/headless/installation.html -- INSTALLED_APPS, URL config, HEADLESS_ONLY mode
- django-allauth headless configuration -- https://docs.allauth.org/en/dev/headless/configuration.html -- HEADLESS_FRONTEND_URLS, token strategy, client types
- Agent OS reference codebase -- /Users/rizwanqaiser/Work/autonomous/hazn/autonomous-agent-os/ -- shadcn/ui components.json, MemoryBlockCard, ChatPanel, workspace patterns, TanStack Query + zustand stores
- Existing Hazn codebase -- orchestrator/api/ (HITL + WorkflowRun viewsets), core/models.py (Agency, EndClient), core/memory.py (HaznMemory), qa/models.py (Deliverable), users/ (django-allauth setup)

### Secondary (MEDIUM confidence)
- django-eventstream GitHub -- https://github.com/fanout/django-eventstream -- SSE setup, Redis pub/sub, DRF integration, channel authorization
- shadcn/ui installation docs -- https://ui.shadcn.com/docs/installation/next -- Next.js setup, React 19 compatibility confirmed
- shadcn/ui Command component -- https://ui.shadcn.com/docs/components/radix/command -- cmdk wrapper for Cmd-K palette
- TanStack Query + SSE integration patterns -- https://fragmentedthought.com/blog/2025/react-query-caching-with-server-side-events -- cache invalidation on SSE events

### Tertiary (LOW confidence)
- Next.js 16 proxy.ts trailing slash issue with Django -- https://github.com/vercel/next.js/issues/63948 -- confirmed issue, skipTrailingSlashRedirect is the fix but needs testing

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- shadcn/ui, TanStack Query, django-allauth headless all verified via official docs and Agent OS reference codebase
- Architecture: HIGH -- patterns derived from existing codebase (DRF viewsets, HaznMemory, Agent OS workspace) with well-documented integration points
- Pitfalls: HIGH -- trailing slash issue confirmed via Next.js docs, SSE connection limits are well-known browser behavior, User model migration is standard Django pattern
- SSE approach: MEDIUM -- django-eventstream is well-documented but specific ASGI/Docker integration needs validation during implementation

**Research date:** 2026-03-06
**Valid until:** 2026-04-06 (30 days -- stable ecosystem, no major releases expected)
