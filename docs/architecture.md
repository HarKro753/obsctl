# Architecture

obsctl is three packages and a shared data model.

---

## Data model

Everything lives in CouchDB via [Self-hosted LiveSync](https://github.com/vrtmrz/obsidian-livesync). Notes are stored as two document types:

**Metadata document** — one per note, keyed by lowercased path:
```json
{
  "_id": "references/some person.md",
  "path": "References/Some Person.md",
  "children": ["h:a1b2c3d4e5f6"],
  "ctime": 1709500000000,
  "mtime": 1709500000000,
  "size": 1234,
  "type": "plain"
}
```

**Leaf/chunk document** — content-addressed by SHA-256, shared across notes:
```json
{
  "_id": "h:a1b2c3d4e5f6",
  "type": "leaf",
  "data": "---\ncategories:\n  - \"[[People]]\"\n---\n\n# Some Person\n..."
}
```

Large notes are split into 50KB chunks. The `children` array in the metadata document lists them in order.

All three packages talk to the same CouchDB database. The CLI reads and writes directly. The plugin syncs in real time. The backend provisions isolated per-user databases.

---

## Packages

### `packages/cli` — Python CLI

Stateless. Each command is a fresh invocation.

```
VaultClient         CouchDB CRUD, LiveSync chunk format
VaultIndex          In-memory graph built from _all_docs (graph/tag/search commands only)
CLI (click)         Thin wrappers around VaultClient and VaultIndex
```

Graph and search commands load the entire vault into memory, build a wikilink graph, run the query, and exit. No daemon, no cache.

### `packages/plugin` — Obsidian plugin

Fork of obsidian-livesync. The sync engine is unchanged. The auth layer is new:

```
main.ts             Registers obsidian://obsctl-auth URI handler
src/auth/           OAuth flow, credential fetch, token storage
src/ui/             AuthScreen replaces the server config pane
PaneRemoteConfig    Injects auth screen; manual config hidden behind toggle
```

OAuth flow:
1. User clicks **Sign in with Google**
2. Plugin opens system browser to `{backendUrl}/auth/google`
3. Google OAuth completes, backend issues JWT, redirects to `obsidian://obsctl-auth?token=...`
4. Plugin receives token, calls `/credentials`, applies CouchDB settings, begins sync

### `packages/backend` — FastAPI service

```
routes/auth.py          GET /auth/google → redirect, GET /auth/callback → JWT
routes/credentials.py   GET /credentials (JWT required) → CouchDB creds
routes/health.py        GET /health
services/oauth.py       Google OAuth: auth URL, token exchange, userinfo
services/jwt.py         HS256 JWT issue + verify
services/couchdb.py     Provision vault_<user_id> DB + CouchDB user (idempotent)
db/                     SQLite: users + vault_credentials tables
```

Per-user isolation: each user gets their own CouchDB database (`vault_<user_id>`) and a CouchDB user scoped to only that database. The backend admin account is never exposed to clients.

---

## Request flow

```
Obsidian plugin
    │
    │  1. GET /auth/google
    ▼
Backend ──────────────► Google OAuth
    │  2. GET /auth/callback
    │     → create user, provision vault, issue JWT
    │
    │  3. obsidian://obsctl-auth?token=JWT
    ▼
Plugin receives token
    │
    │  4. GET /credentials (Authorization: Bearer JWT)
    ▼
Backend returns { couchdb_url, username, password }
    │
    ▼
Plugin configures LiveSync sync engine
    │
    ▼
CouchDB ◄──────────────── LiveSync sync (unchanged from upstream)
    ▲
    │
vault CLI (direct CouchDB access, no backend involved)
```

---

## Skills

`skills/` contains [ClawHub](https://clawhub.com)-compatible agent skills. Skills are Markdown files that tell an AI agent how to use a tool or system. They are loaded at the start of an agent session.

- `skills/obsidian-vault/SKILL.md` — vault design system: folder rules, properties, linking, retrieval patterns
- `skills/obsidian-cli/SKILL.md` — how to use the `vault` CLI safely and effectively

---

## Deployment

Target: **Kubernetes on Proxmox** (home lab).

CI/CD: GitHub Actions → Docker build → push to container registry → Tailscale into home cluster → `kubectl apply` via `deploy/`.

Self-hosting: `docker compose up` at repo root.
