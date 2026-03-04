# obsctl

> Control plane for Obsidian. Like `kubectl`, but for your knowledge graph.

obsctl makes Obsidian programmable — for AI agents and humans alike. One repo, three layers:

| Package | What it does |
|---------|-------------|
| `packages/cli` | Python CLI — `vault read`, `vault write`, `vault search`, graph traversal |
| `packages/plugin` | Obsidian plugin — replaces LiveSync's manual setup with Google Sign-In |
| `packages/backend` | FastAPI service — provisions a CouchDB vault per user, issues JWTs |

Skills and prompts for AI agents live in `skills/` and `prompts/`.

---

## The problem

Your Obsidian vault is a knowledge graph. AI agents should be able to read it, write to it, and traverse it — without Obsidian running, without copy-pasting CouchDB credentials, without curl scripts.

obsctl fixes that.

---

## Quickstart

### CLI (for agents and power users)

```bash
pip install obsidian-vault-cli    # published from packages/cli/

vault config set vault.host obsidian.yourhost.com
vault config set vault.username admin
vault config set vault.password yourpassword

vault read file="north star"
vault search query="agent loop" --context
vault backlinks file="closedclaw"
vault create name="New Idea" folder="References" content="# Idea"
```

### Managed sync (zero-config)

1. Install the plugin from `packages/plugin/` into Obsidian
2. Click **Sign in with Google**
3. Done — vault syncs automatically, no server config required

### Self-hosting

```bash
cp packages/backend/.env.example packages/backend/.env
# fill in GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, JWT_SECRET
docker compose up
```

---

## Monorepo structure

```
obsctl/
├── packages/
│   ├── cli/         # Python 3.10+ CLI — pip install obsidian-vault-cli
│   ├── plugin/      # Obsidian plugin (fork of obsidian-livesync, MIT)
│   └── backend/     # Python 3.12 + FastAPI auth + provisioning
├── skills/
│   ├── obsidian-vault/   # ClawHub skill — vault design system for agents
│   └── obsidian-cli/     # ClawHub skill — how agents use the CLI
├── prompts/         # Reusable agent prompts for vault workflows
├── docs/
│   └── self-hosting.md
├── docker-compose.yml
└── SPEC.md
```

---

## Packages

### `packages/cli` — obsidian-vault-cli

Full CLI reference: [packages/cli/SPEC.md](packages/cli/SPEC.md)

Commands: `read`, `write`, `create`, `delete`, `move`, `search`, `backlinks`, `links`, `tags`, `property:set`, `unresolved`, `orphans`, `templates` and more.

Safety built in: `--force` to overwrite, `--yes` to delete, `--dry-run` to preview, read-before-write on property changes.

### `packages/plugin` — Obsidian plugin

Fork of [obsidian-livesync](https://github.com/vrtmrz/obsidian-livesync) (MIT). Minimal diff — only the auth/config layer changes. All sync logic (conflict resolution, chunking, E2E encryption) is unchanged.

### `packages/backend` — FastAPI provisioning service

- `GET /auth/google` → Google OAuth redirect
- `GET /auth/callback` → JWT
- `GET /credentials` → CouchDB endpoint + per-user credentials
- `GET /health`

Stack: Python 3.12, FastAPI, uvicorn, sqlite3, python-jose, authlib, httpx.

---

## Skills

Skills in `skills/` are [ClawHub](https://clawhub.com)-compatible agent skills.

| Skill | Description |
|-------|-------------|
| `obsidian-vault` | Vault design system — folder structure, properties, linking rules, retrieval patterns |
| `obsidian-cli` | How agents use the `vault` CLI — commands, patterns, safety flags |

---

## License

MIT — plugin package is a fork of [vrtmrz/obsidian-livesync](https://github.com/vrtmrz/obsidian-livesync) (also MIT).
