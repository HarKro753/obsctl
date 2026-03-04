<div align="center">

# obsctl

**Programmatic access to your Obsidian vault.**

CLI · Managed Sync · Obsidian Plugin · Agent Skills

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB.svg)](packages/cli)
[![PyPI](https://img.shields.io/pypi/v/obsidian-vault-cli)](https://pypi.org/project/obsidian-vault-cli/)

</div>

---

obsctl is a monorepo for making Obsidian vaults programmable. It provides a CLI for agents and power users, a managed sync backend with Google OAuth, an Obsidian plugin that replaces manual CouchDB setup with a single sign-in, and ClawHub skills for AI agents.

All packages share the same underlying model: your vault lives in CouchDB via [Self-hosted LiveSync](https://github.com/vrtmrz/obsidian-livesync), and obsctl gives structured, safe access to everything in it.

---

## Packages

| Package                                | Description                                                         |
| -------------------------------------- | ------------------------------------------------------------------- |
| [`packages/cli`](packages/cli)         | Python CLI — read, write, search, graph traversal, tags, properties |
| [`packages/plugin`](packages/plugin)   | Obsidian plugin — Google Sign-In replaces manual CouchDB setup      |
| [`packages/backend`](packages/backend) | FastAPI service — provisions a CouchDB vault per user, issues JWTs  |

## Skills

| Skill                                            | Description                                                                |
| ------------------------------------------------ | -------------------------------------------------------------------------- |
| [`skills/obsidian-vault`](skills/obsidian-vault) | Vault design system for agents — structure, properties, linking, retrieval |
| [`skills/obsidian-cli`](skills/obsidian-cli)     | How agents use the `vault` CLI — commands, patterns, safety flags          |

---

## Getting started

### CLI

```bash
pip install obsidian-vault-cli

vault config set vault.host obsidian.yourhost.com
vault config set vault.username admin
vault config set vault.password yourpassword

vault ping
vault read --file "north star"
vault search --query "agent loop" --context
vault backlinks --file "closedclaw"
```

Full reference: [docs/cli.md](docs/cli.md)

### Plugin

Install `packages/plugin/` as an Obsidian community plugin, then click **Sign in with Google** in the plugin settings. No server URLs. No credential copying.

Full guide: [docs/plugin.md](docs/plugin.md)

### Self-hosting the backend

```bash
cp packages/backend/.env.example packages/backend/.env
# Set GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, JWT_SECRET, COUCHDB_URL
docker compose up
```

Full guide: [docs/self-hosting.md](docs/self-hosting.md)

---

## Documentation

- [docs/cli.md](docs/cli.md) — full CLI command reference
- [docs/plugin.md](docs/plugin.md) — plugin installation and OAuth setup
- [docs/self-hosting.md](docs/self-hosting.md) — running the backend yourself
- [docs/architecture.md](docs/architecture.md) — how the pieces fit together

---

## License

MIT. The plugin package is a fork of [vrtmrz/obsidian-livesync](https://github.com/vrtmrz/obsidian-livesync), also MIT.
