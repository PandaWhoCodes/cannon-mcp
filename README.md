# Canon-MCP

### Ground your AI in the truth. Not in yesterday's truth.

Canon-MCP is a stateless MCP server that feeds your project's real documentation — API specs, data models, architecture decisions — directly into Claude as it works. When a developer changes an API response shape on the backend, Canon-MCP ensures the frontend developer's Claude session knows about it before it writes a single line of code.

---

## The Problem

In multi-service projects, Claude hallucinates. Not because it's bad at code, but because it doesn't know your code. It doesn't know that your `/api/threads` endpoint returns `post_count` not `postCount`. It doesn't know that your frontend expects a `PaginatedResponse<T>` wrapper. It doesn't know that you switched from REST to GraphQL last Tuesday.

Documentation exists, but it's stale. The backend team updated the response schema three commits ago and nobody told the frontend's `CLAUDE.md`.

Canon-MCP solves this by making documentation a living, enforced part of your development workflow:

1. Every service maintains its own docs alongside its code
2. Docs sync to a central location automatically
3. Claude reads from that central location via MCP — always fresh, always consistent across teams

---

## How It Works

```
Your Service Repos                    Canon-MCP Server (Fly.io)
┌──────────────┐                     ┌─────────────────────┐
│ backend/     │                     │                     │
│   app/       │──docs/ synced to──> │  Reads from GitHub  │
│   docs/      │  grounding branch   │  via API on every   │
│   CLAUDE.md  │                     │  request (stateless) │
├──────────────┤                     │                     │
│ frontend/    │                     │  Serves docs to     │
│   src/       │──docs/ synced to──> │  Claude via MCP     │
│   docs/      │  grounding branch   │  protocol           │
│   CLAUDE.md  │                     │                     │
└──────────────┘                     └──────────┬──────────┘
                                                │
                                     ┌──────────▼──────────┐
                                     │  Claude Code        │
                                     │  (any dev, any repo)│
                                     │                     │
                                     │  "What's the API    │
                                     │   contract for      │
                                     │   thread creation?" │
                                     └─────────────────────┘
```

**Key design decision:** The server stores nothing. No database, no filesystem, no cache. Every request fetches fresh from GitHub using the developer's own token. This means zero maintenance, zero stale state, and horizontal scaling for free.

---

## Quick Start (15 minutes)

### Step 1: Deploy the MCP server

Fork this repo and deploy to Fly.io (or any container host):

```bash
# Clone your fork
git clone https://github.com/yourorg/cannon-mcp.git
cd cannon-mcp

# Configure for your org
# Edit fly.toml — change these two values:
#   GROUNDING_REPO = "yourorg/your-repo"      # where your grounding docs live
#   GROUNDING_BRANCH = "grounding-docs"        # the branch with centralized docs

# Deploy
fly launch --name your-cannon-mcp --region iad --no-deploy
fly deploy
```

Environment variables (set in `fly.toml` or Fly dashboard):

| Variable | Description | Example |
|---|---|---|
| `GROUNDING_REPO` | GitHub repo with centralized docs (owner/repo format) | `yourorg/your-project` |
| `GROUNDING_BRANCH` | Branch containing the grounding docs | `grounding-docs` |
| `PORT` | Server port (default 8000) | `8000` |

The server has no secrets of its own. Each developer's GitHub token is passed from the client via the `Authorization` header.

### Step 2: Set up the grounding docs branch

Create an orphan branch in the repo you specified in `GROUNDING_REPO`:

```bash
git checkout --orphan grounding-docs
git rm -rf .
```

Create the folder structure:

```
grounding-docs branch
├── manifest.json           # Index of all services and their docs
├── shared/                 # Cross-cutting docs (architecture, conventions)
│   ├── architecture.md
│   ├── conventions.md
│   └── api-contracts.md
├── backend/                # Backend-specific docs (synced from backend service)
│   ├── CLAUDE.md
│   └── service-overview.md
└── frontend/               # Frontend-specific docs (synced from frontend service)
    ├── CLAUDE.md
    └── service-overview.md
```

The `manifest.json` tells the MCP server what's available:

```json
{
  "version": "1.0",
  "last_updated": "2026-02-07T00:00:00Z",
  "services": {
    "backend": {
      "docs": [
        { "path": "backend/CLAUDE.md", "description": "Backend context" },
        { "path": "backend/service-overview.md", "description": "Backend overview" }
      ]
    },
    "frontend": {
      "docs": [
        { "path": "frontend/CLAUDE.md", "description": "Frontend context" },
        { "path": "frontend/service-overview.md", "description": "Frontend overview" }
      ]
    }
  },
  "shared": {
    "docs": [
      { "path": "shared/architecture.md", "description": "System architecture" },
      { "path": "shared/conventions.md", "description": "Coding conventions" },
      { "path": "shared/api-contracts.md", "description": "API contracts between services" }
    ]
  }
}
```

Commit and push:

```bash
git add -A && git commit -m "init: grounding-docs branch"
git push -u origin grounding-docs
```

### Step 3: Connect Claude Code

Every developer needs two things:

**A. A GitHub token** with `repo` read access, set as an environment variable:

```bash
# Add to your shell profile (~/.zshrc, ~/.bashrc, etc.)
export MCP_GITHUB_TOKEN=ghp_your_token_here
```

**B. An `.mcp.json` file** in the root of every service repo:

```json
{
  "mcpServers": {
    "grounding-docs": {
      "type": "http",
      "url": "https://your-cannon-mcp.fly.dev/mcp",
      "headers": {
        "Authorization": "Bearer ${MCP_GITHUB_TOKEN}"
      }
    }
  }
}
```

Commit this file to each service repo. Claude Code auto-discovers it on startup.

Verify it's working — open Claude Code and ask: *"What services are available in the grounding docs?"*

---

## Writing Good Grounding Docs

The MCP server is only as good as the docs you feed it. Here's how to write docs that actually prevent Claude from hallucinating.

### What to document

| Document | Purpose | When it saves you |
|---|---|---|
| **Data model** (tables, schemas, types) | Exact column names, types, constraints, relationships | Claude writes `post_count` not `postCount`, uses correct FK constraints |
| **API reference** (endpoints, request/response shapes) | Every endpoint with exact field names, types, validation rules | Claude constructs correct API calls, handles all error codes |
| **API integration** (client-side types, functions) | TypeScript types, API client function signatures | Claude uses your existing API client instead of raw fetch |
| **Component reference** | What each component renders, its props | Claude reuses existing components instead of building duplicates |
| **Architecture** | Data flow, routing, key design decisions | Claude follows your patterns instead of inventing its own |

### What NOT to document

- **Aspirational features** — only document what the code does today
- **Implementation details that change constantly** — focus on interfaces and contracts
- **Anything that can be read from the code itself** — docs should add context the code can't (e.g., *why* you chose SQLite over Postgres, not *how* the SQLite connection works)

### Doc format that works

Use tables for structured data (schemas, endpoints). Use code blocks for exact values. Be specific:

**Bad:** "The thread endpoint returns thread data with some metadata"

**Good:**

```markdown
### ThreadDetail Response
| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique identifier |
| title | string | Thread title, max 300 chars |
| post_count | integer | Number of posts in the thread |
| tags | string[] | List of tag names, lowercased |
```

---

## Keeping Docs Alive: The CLAUDE.md Hook

This is the most important part. Without this, your docs will go stale within a week.

Add a **Grounding Doc Maintenance** section to each service's `CLAUDE.md`. This acts as a standing instruction to Claude: whenever it changes code that affects a contract, it must update the docs in the same commit.

See [`samples/backend-CLAUDE.md`](samples/backend-CLAUDE.md) and [`samples/frontend-CLAUDE.md`](samples/frontend-CLAUDE.md) for complete examples.

The key section looks like this:

```markdown
## Grounding Doc Maintenance

When you make code changes, you MUST update the corresponding
grounding docs in `docs/` as part of the same change.

### What triggers a doc update

| Code Change                         | Update This Doc           |
|-------------------------------------|---------------------------|
| Database schema changes             | docs/data-model.md        |
| API endpoint changes                | docs/api-reference.md     |
| Request/response body fields        | docs/api-reference.md     |
| Pydantic model changes              | docs/api-reference.md     |
| Architecture decisions              | docs/architecture.md      |
```

**This is not optional.** This is the mechanism that keeps docs fresh. When Claude modifies a Pydantic model, the CLAUDE.md instruction forces it to update `docs/api-reference.md` in the same commit. When that doc syncs to the grounding branch, every other team's Claude session immediately sees the change.

### Syncing docs to the grounding branch

The simplest approach — a script that copies `docs/` from each service branch to the grounding branch:

```bash
#!/bin/bash
# sync-docs.sh — run after merging to a service branch
SERVICE=$1  # "backend" or "frontend"
BRANCH=$2   # source branch

git checkout grounding-docs
git checkout $BRANCH -- docs/ CLAUDE.md
mkdir -p $SERVICE
cp -r docs/* $SERVICE/
cp CLAUDE.md $SERVICE/CLAUDE.md
git add $SERVICE/
git commit -m "sync: $SERVICE docs from $BRANCH"
git push origin grounding-docs
git checkout -
```

Or automate via GitHub Actions on merge to your service branches.

---

## Available MCP Tools

Once connected, Claude has access to these tools:

| Tool | What it does |
|---|---|
| `list_services` | List all services and their available docs from the manifest |
| `get_doc(service, filename)` | Get a specific doc (e.g., `get_doc("backend", "api-reference.md")`) |
| `get_all_docs_for_service(service)` | Get every doc for a service in one call |
| `get_shared_docs` | Get all cross-cutting docs (architecture, conventions, contracts) |
| `search_docs(query)` | Full-text search across all grounding docs |
| `get_manifest` | Get the raw manifest showing all available docs |

Claude will call these automatically when it needs context. You don't need to prompt it — the MCP server's instructions tell Claude to check docs when working on cross-service features.

---

## Multi-Repo vs. Multi-Branch

Canon-MCP works with both setups:

**Multi-branch** (one repo, many branches):
- `yourorg/project` branch `frontend` — frontend code + `docs/`
- `yourorg/project` branch `backend` — backend code + `docs/`
- `yourorg/project` branch `grounding-docs` — centralized docs

**Multi-repo** (separate repos):
- `yourorg/frontend` — frontend code + `docs/`
- `yourorg/backend` — backend code + `docs/`
- `yourorg/grounding-docs` — centralized docs (separate repo)

Set `GROUNDING_REPO` and `GROUNDING_BRANCH` in your Fly deployment to point to wherever your centralized docs live.

---

## What You Must Do

1. **Write a `CLAUDE.md` for every service** — project overview, tech stack, file structure, key patterns, common tasks. See the [samples/](samples/) directory.

2. **Write detailed `docs/` for contracts** — data models, API reference, component reference. These are the files that prevent cross-service hallucinations.

3. **Include the Grounding Doc Maintenance section** in every `CLAUDE.md` — this is the hook that forces Claude to update docs when it changes contracts.

4. **Commit `.mcp.json` to every service repo** — this is how Claude Code discovers the MCP server.

5. **Sync docs to the grounding branch** after merges — via script or GitHub Actions.

6. **Review doc changes in PRs** — treat doc updates the same as code. If a PR changes a response shape but doesn't update the API reference, reject it.

## What You Must NOT Do

1. **Don't skip writing docs because "we'll add them later"** — you won't, and Claude will hallucinate the old contract in every other service.

2. **Don't put implementation details in grounding docs** — grounding docs are for *interfaces and contracts*. Claude can read the code for implementation details.

3. **Don't let the grounding branch go stale** — if docs aren't synced after merges, you're back to square one. Automate the sync.

4. **Don't store secrets in the MCP server** — the server is stateless. Tokens come from each developer's environment via `MCP_GITHUB_TOKEN`.

5. **Don't write aspirational docs** — only document what exists in the code *right now*. Planned features in grounding docs will cause Claude to implement them as if they already exist.

6. **Don't duplicate information across docs** — the API reference should be the single source for endpoint shapes. The frontend's `api-integration.md` should reference it, not copy it.

---

## How This Helps

**Without Canon-MCP:**
- Backend changes a response field from `post_count` to `postCount`
- Frontend developer asks Claude to add a feature
- Claude uses the old field name because its `CLAUDE.md` is stale
- Feature breaks at runtime, developer debugs for 30 minutes

**With Canon-MCP:**
- Backend changes the field and Claude updates `docs/api-reference.md` in the same commit (enforced by CLAUDE.md instructions)
- Docs sync to grounding branch
- Frontend developer asks Claude to add a feature
- Claude calls `get_doc("backend", "api-reference.md")` and sees the current contract
- Feature works on first try

**Cross-team contract validation:**
Claude can compare the backend's API reference against the frontend's TypeScript types and flag mismatches *before* they become runtime bugs. Ask Claude: *"Compare the backend API reference with the frontend types and find any mismatches."*

**Onboarding:**
New developers don't need to read every service's codebase. Claude has full context from day one — architecture, patterns, API contracts — and can answer questions accurately.

---

## Self-Hosting

The server is a single Python process. Deploy anywhere that runs Docker:

```
Server code:  server.py, github_client.py
Dependencies: fastmcp, httpx, uvicorn
Dockerfile:   included
fly.toml:     included (Fly.io config)
```

The server needs zero secrets. All GitHub auth comes from the client's `Authorization` header.

| Platform | Deploy command |
|---|---|
| Fly.io | `fly deploy` |
| Railway | Connect repo, set env vars |
| Render | Docker deploy, set env vars |
| Any Docker host | `docker build -t cannon-mcp . && docker run -p 8000:8000 -e GROUNDING_REPO=... -e GROUNDING_BRANCH=... cannon-mcp` |

---

## Project Structure

```
cannon-mcp/
├── server.py              # MCP server — tools, health check, webhook endpoint
├── github_client.py       # Async GitHub API wrapper (fetch files, list dirs, search)
├── requirements.txt       # fastmcp, httpx, uvicorn
├── Dockerfile             # Python 3.12 slim, uvicorn
├── fly.toml               # Fly.io deployment config
├── .mcp.json              # Client MCP config (example — commit to your service repos)
└── samples/
    ├── backend-CLAUDE.md  # Sample CLAUDE.md for a backend service
    └── frontend-CLAUDE.md # Sample CLAUDE.md for a frontend service
```
