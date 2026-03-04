---
name: obsidian-cli
description: Use the obsctl vault CLI to read, write, search, and traverse an Obsidian vault stored in CouchDB via LiveSync. Use when you need to read notes, create or update notes, search content, traverse the knowledge graph (backlinks, links, orphans), manage tags, or set properties.
---

# obsidian-cli — Vault CLI Usage

The `vault` CLI (from `obsidian-vault-cli`) gives agents direct access to an Obsidian vault via CouchDB/LiveSync — no Obsidian app needed.

## Setup check

```bash
vault ping          # verify CouchDB connectivity
vault config show   # see current config
```

## Reading notes

```bash
vault read --file "north star"              # by wikilink-style name
vault read --path "References/Person.md"    # by exact path
vault read --file "closedclaw" --json       # JSON output for parsing
```

## Writing notes

**Always use `--force` to overwrite existing notes. Without it, the command aborts.**

```bash
# Create new note
vault create --name "New Idea" --folder "References" --content "# Idea\n..."

# Overwrite existing note (requires --force)
vault write --path "References/Person.md" --content "..." --force

# Preview changes without writing
vault write --path "References/Person.md" --content "..." --diff

# Append / prepend (safe — reads first, never blindly overwrites)
vault append --file "north star" --content "\n## New section"
vault prepend --file "north star" --content "**Updated today**\n"
```

## Searching

```bash
vault search --query "agent loop"
vault search --query "TODO" --context          # show surrounding lines
vault search --query "closedclaw" --limit 10
```

## Graph traversal (ENTER → TRAVERSE → EXTRACT)

```bash
vault backlinks --file "closedclaw"           # who links TO this note?
vault links --file "closedclaw"               # what does this note link TO?
vault unresolved                               # dead wikilinks (stubs to create)
vault orphans                                  # notes with no incoming links
```

## Tags

```bash
vault tags --counts --sort count              # tag landscape
vault tag --name "math"                       # notes with this tag
```

## Properties (frontmatter)

```bash
vault properties --file "north star"          # all frontmatter
vault property:read --name "status" --file "north star"

# property:set reads current value first and shows diff before writing
vault property:set --name "status" --value "active" --file "north star"
vault property:set --name "tags" --value "math" --type list --file "Mathe I"
vault property:set --name "status" --value "active" --file "north star" --yes  # skip prompt
```

## Deleting

**Delete requires `--yes` in scripts. Interactive TTY prompts by default.**

```bash
vault delete --file "old note" --yes          # scripted
vault delete --file "old note"                # prompts in TTY
vault delete --file "old note" --dry-run      # preview only
```

## Safety flags (always available on mutating commands)

| Flag | Behaviour |
|------|-----------|
| `--force` | Skip existence guard, overwrite unconditionally |
| `--yes` | Skip confirmation prompts (for scripts/agents) |
| `--dry-run` | Print what would happen, do nothing |
| `--diff` | Show unified diff of content change, do nothing |

## ⚠️ Rules for agents

1. **Never use `vault write` without `--force`** — it aborts on existing notes by design
2. **Always `vault read` before `vault write`** when updating — preserve frontmatter
3. **`vault property:set` reads and diffs first** — safe for frontmatter mutations
4. **Use `vault create` for new notes** — fails clearly if already exists
5. **CouchDB `deleted: true` bug**: if a write was preceded by `vault delete`, the CLI will warn you. Acknowledge with `--yes`.

## File listing

```bash
vault files                           # all files
vault files --folder "References"     # in a folder
vault folders                         # all folder paths
vault templates                       # available templates
```
