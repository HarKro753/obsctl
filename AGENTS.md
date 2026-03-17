# AGENTS.md — obsctl

Control plane for Obsidian: CLI + managed sync plugin + provisioning backend + agent skills.

## Packages

| Package            | Language         | Entry                            |
| ------------------ | ---------------- | -------------------------------- |
| `packages/cli`     | Python 3.10+     | `pip install obsidian-vault-cli` |
| `packages/plugin`  | TypeScript (Bun) | Obsidian plugin                  |
| `packages/backend` | Python 3.12      | FastAPI, uvicorn                 |

## Build / Run / Test

### CLI (`packages/cli`)

```bash
pip install -e ".[dev]"
pytest
```

### Backend (`packages/backend`)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 3001
pytest
```

### Plugin (`packages/plugin`)

```bash
bun install
bun run build
bun run dev
```

## Coding conventions

- No file over 500 lines
- Push after every meaningful change
- Tests before implementation
- Commit format: `feat(cli): ...`, `feat(plugin): ...`, `feat(backend): ...`
