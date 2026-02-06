"""cannon-mcp: Stateless MCP server for serving grounding docs from GitHub."""

import json
import os

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers
from starlette.requests import Request
from starlette.responses import JSONResponse

from github_client import GitHubClient

# --- Config from environment ---
GROUNDING_REPO = os.environ.get("GROUNDING_REPO", "yourorg/grounding-docs")
GROUNDING_BRANCH = os.environ.get("GROUNDING_BRANCH", "main")
PORT = int(os.environ.get("PORT", "8000"))

# --- GitHub client (stateless, no token stored) ---
gh = GitHubClient(repo=GROUNDING_REPO, branch=GROUNDING_BRANCH)

# --- MCP Server ---
mcp = FastMCP(
    "cannon-mcp",
    instructions=(
        "Grounding docs server. Provides architecture docs, API contracts, "
        "service-specific context, and cross-cutting documentation for a "
        "multi-service system. Use list_services to discover available docs, "
        "then get_doc to retrieve specific documents."
    ),
)


def _get_token() -> str:
    """Extract GitHub token from the client's Authorization header."""
    headers = get_http_headers()
    auth = headers.get("authorization", "")
    if auth.startswith("Bearer "):
        return auth.removeprefix("Bearer ").strip()
    if auth.startswith("bearer "):
        return auth.removeprefix("bearer ").strip()
    raise ValueError("Missing or invalid Authorization header. Send: Authorization: Bearer <github_token>")


# --- MCP Tools ---


@mcp.tool
async def list_services() -> str:
    """List all services and their available documents from the grounding docs repo.

    Returns a summary of each service directory and the docs it contains.
    Call this first to understand what documentation is available.
    """
    token = _get_token()
    manifest = await gh.get_manifest(token)
    if manifest:
        return json.dumps(manifest, indent=2)

    # Fallback: list directories from repo root
    items = await gh.list_dir("", token)
    dirs = [item for item in items if item["type"] == "dir"]
    result = {"services": []}
    for d in dirs:
        files = await gh.list_dir(d["path"], token)
        doc_names = [f["name"] for f in files if f["name"].endswith(".md")]
        result["services"].append({"name": d["name"], "docs": doc_names})
    return json.dumps(result, indent=2)


@mcp.tool
async def get_doc(service: str, filename: str) -> str:
    """Get a specific grounding document by service name and filename.

    Args:
        service: Service name (e.g. "backend", "frontend", "rag", "ingestion", "shared")
        filename: Document filename (e.g. "CLAUDE.md", "api-spec.md")
    """
    token = _get_token()
    path = f"{service}/{filename}"
    content = await gh.get_file(path, token)
    if content is None:
        return f"Document not found: {path}"
    return content


@mcp.tool
async def get_all_docs_for_service(service: str) -> str:
    """Get all documents for a given service.

    Args:
        service: Service name (e.g. "backend", "frontend", "rag", "ingestion")
    """
    token = _get_token()
    files = await gh.get_all_files_in_dir(service, token)
    if not files:
        return f"No docs found for service: {service}"
    result = {}
    for f in files:
        result[f.path] = f.content
    return json.dumps(result, indent=2)


@mcp.tool
async def get_shared_docs() -> str:
    """Get all cross-cutting shared documentation (architecture, conventions, API contracts, etc.)."""
    token = _get_token()
    files = await gh.get_all_files_in_dir("shared", token)
    if not files:
        return "No shared docs found."
    result = {}
    for f in files:
        result[f.path] = f.content
    return json.dumps(result, indent=2)


@mcp.tool
async def search_docs(query: str) -> str:
    """Search across all grounding documents for a keyword or phrase.

    Args:
        query: Search term (e.g. "embedding", "authentication", "rate limit")
    """
    token = _get_token()
    results = await gh.search_docs(query, token)
    if not results:
        return f"No results found for: {query}"
    return json.dumps(results, indent=2)


@mcp.tool
async def get_manifest() -> str:
    """Get the manifest file showing all available docs, their versions, and last update times."""
    token = _get_token()
    manifest = await gh.get_manifest(token)
    if manifest is None:
        return "No manifest.json found in the grounding docs repo."
    return json.dumps(manifest, indent=2)


# --- Custom HTTP routes (for health checks and webhooks) ---


@mcp.custom_route("/health", methods=["GET"])
async def health(request: Request) -> JSONResponse:
    return JSONResponse({
        "status": "healthy",
        "repo": GROUNDING_REPO,
        "branch": GROUNDING_BRANCH,
    })


@mcp.custom_route("/api/refresh", methods=["POST"])
async def refresh(request: Request) -> JSONResponse:
    """Webhook endpoint for scripts to signal a doc update.

    Currently a no-op since we're stateless (always fetch fresh from GitHub).
    Future: could invalidate a cache layer here.
    """
    return JSONResponse({
        "status": "ok",
        "message": "Server is stateless — docs are always fetched fresh from GitHub.",
    })


# --- App for uvicorn ---
app = mcp.http_app(
    path="/mcp",
    stateless_http=True,
    json_response=True,
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
