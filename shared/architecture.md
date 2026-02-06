# System Architecture

## Overview

This is a multi-service system with a backend and frontend, managed in a single repo across branches.

## Services

- **backend** (`backend` branch) — API server
- **frontend** (`frontend` branch) — Web client

## Repository Structure

All services live in `PandaWhoCodes/cannon-mcp` on separate branches:
- `master` — MCP server (this grounding docs server)
- `backend` — Backend service
- `frontend` — Frontend service
- `grounding-docs` — Centralized documentation (this branch)
