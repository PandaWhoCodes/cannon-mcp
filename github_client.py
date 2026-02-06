"""Async GitHub API client for fetching grounding docs from a repo."""

import json
from dataclasses import dataclass

import httpx

GITHUB_API = "https://api.github.com"


@dataclass
class GitHubFile:
    path: str
    content: str


class GitHubClient:
    """Stateless GitHub API wrapper. Every call requires a token."""

    def __init__(self, repo: str, branch: str = "main"):
        self.repo = repo  # e.g. "yourorg/grounding-docs"
        self.branch = branch

    def _headers(self, token: str) -> dict:
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _raw_headers(self, token: str) -> dict:
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3.raw",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def get_file(self, path: str, token: str) -> str | None:
        """Fetch raw content of a single file from the repo."""
        url = f"{GITHUB_API}/repos/{self.repo}/contents/{path}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url,
                headers=self._raw_headers(token),
                params={"ref": self.branch},
                timeout=30,
            )
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.text

    async def list_dir(self, path: str, token: str) -> list[dict]:
        """List files in a directory. Returns list of {name, path, type}."""
        url = f"{GITHUB_API}/repos/{self.repo}/contents/{path}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url,
                headers=self._headers(token),
                params={"ref": self.branch},
                timeout=30,
            )
            if resp.status_code == 404:
                return []
            resp.raise_for_status()
            items = resp.json()
            if not isinstance(items, list):
                return []
            return [
                {"name": item["name"], "path": item["path"], "type": item["type"]}
                for item in items
            ]

    async def get_manifest(self, token: str) -> dict | None:
        """Fetch and parse manifest.json from repo root."""
        content = await self.get_file("manifest.json", token)
        if content is None:
            return None
        return json.loads(content)

    async def get_all_files_in_dir(self, path: str, token: str) -> list[GitHubFile]:
        """Fetch all .md files in a directory (non-recursive)."""
        items = await self.list_dir(path, token)
        files = []
        for item in items:
            if item["type"] == "file" and item["name"].endswith(".md"):
                content = await self.get_file(item["path"], token)
                if content is not None:
                    files.append(GitHubFile(path=item["path"], content=content))
        return files

    async def search_docs(self, query: str, token: str) -> list[dict]:
        """Search for text across all files in the repo using GitHub code search."""
        url = f"{GITHUB_API}/search/code"
        search_query = f"{query} repo:{self.repo}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url,
                headers=self._headers(token),
                params={"q": search_query},
                timeout=30,
            )
            if resp.status_code != 200:
                return []
            data = resp.json()
            results = []
            for item in data.get("items", []):
                results.append({
                    "path": item["path"],
                    "name": item["name"],
                    "url": item["html_url"],
                })
            return results

    async def verify_token(self, token: str) -> bool:
        """Quick check that the token is valid and can access the repo."""
        url = f"{GITHUB_API}/repos/{self.repo}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url,
                headers=self._headers(token),
                timeout=10,
            )
            return resp.status_code == 200
