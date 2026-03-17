# CLI Reference

`vault` is a Python CLI for reading, writing, and traversing an Obsidian vault stored in CouchDB via Self-hosted LiveSync. No Obsidian app required.

## Installation

```bash
pip install obsidian-vault-cli
```

## Configuration

```bash
vault config set vault.host obsidian.yourhost.com
vault config set vault.port 443
vault config set vault.protocol https
vault config set vault.database obsidian
vault config set vault.username admin
vault config set vault.password yourpassword

vault ping   # verify connection
```

Config is stored at `~/.vault-cli/config.json`. Environment variables (`VAULT_HOST`, `VAULT_PORT`, etc.) override the file.

---

## Safety flags

All mutating commands support these flags:

| Flag | Behaviour |
|------|-----------|
| `--force` | Skip existence guard, overwrite unconditionally |
| `--yes` | Accept vault rule warnings automatically (for scripts/agents) |
| `--strict` | Treat vault rule violations as hard errors (exit code 2) |
| `--dry-run` | Print what would happen, do nothing |
| `--diff` | Show unified diff of content change, do nothing |

---

## Vault rule guardrails

`vault create`, `vault write`, and `vault move` enforce vault design conventions before any write:

| Rule | Trigger |
|------|---------|
| **Folder placement** | Target folder does not exist in the vault |
| **Properties system** | Note has no `categories` property in frontmatter |
| **Placement rules** | `[[References]]` category at root, or non-References category in `References/` |

Warning output is parseable (starts with `⚠ Rule:`):

```
⚠ Rule: Folder placement
  Folder "30 References" does not exist in the vault.
  Existing folders: Categories, Daily, Projects, References, Templates
  ...
  See: vault design rules → "Folders are for infrastructure, not organization"

Proceed anyway? [y/N]
```

| Mode | Flag | Behaviour |
|------|------|-----------|
| Interactive (default) | _(none)_ | Prompt with y/N, defaults to No |
| Agent/script | `--yes` | Accept and log warning, proceed |
| CI/strict | `--strict` | Hard fail with exit code 2 |

Exit codes: `0` success, `1` error, `2` rule violation rejected.

`--force` does NOT bypass rules — it only controls overwrite. These are separate concerns.

---

## Commands

### Read

```bash
vault read --file "north star"              # wikilink-style name resolution
vault read --path "References/Person.md"    # exact path from vault root
vault read --file "closedclaw" --json       # JSON output
```

### Create

Fails clearly if the note already exists. Runs vault rule guardrails before writing.

```bash
vault create --name "New Idea" --folder "References" --content "# Idea"
vault create --name "Daily Note" --template "Daily"
vault create --name "Idea" --folder "NewFolder" --content "..." --yes     # accept rule warnings
vault create --name "Idea" --folder "NewFolder" --content "..." --strict  # fail on violations
```

### Write

**Requires `--force` to overwrite an existing note.** Runs vault rule guardrails before writing.

```bash
vault write --path "References/Person.md" --content "..." --force
vault write --path "References/Person.md" --content "..." --diff     # preview only
vault write --path "References/Person.md" --content "..." --dry-run  # no write
vault write --path "NewFolder/Note.md" --content "..." --yes         # accept rule warnings
```

### Append / Prepend

Safe — reads existing content first, never blindly overwrites.

```bash
vault append --file "north star" --content "\n## New section"
vault prepend --file "north star" --content "**Updated today**\n"
```

### Delete

Requires `--yes` in scripts. Prompts interactively in a TTY.

```bash
vault delete --file "old note" --yes     # scripted
vault delete --file "old note"           # interactive prompt
vault delete --file "old note" --dry-run # preview only
```

### Move / Rename

Runs vault rule guardrails on the destination path.

```bash
vault move --file "draft" --to "References/final.md"
vault move --file "draft" --to "NewFolder/final.md" --yes     # accept rule warnings
vault move --file "draft" --to "NewFolder/final.md" --strict  # fail on violations
vault rename --file "draft" --name "Final Version"
```

---

## Search

```bash
vault search --query "agent loop"
vault search --query "TODO" --context          # show surrounding lines
vault search --query "closedclaw" --limit 10
vault search --query "agent" --json
```

---

## Graph traversal

```bash
vault backlinks --file "closedclaw"       # notes that link TO this note
vault backlinks --file "closedclaw" --counts
vault links --file "closedclaw"           # notes this note links TO
vault unresolved                          # dead wikilinks (stubs to create)
vault orphans                             # notes with no incoming links
```

---

## Tags

```bash
vault tags                          # all tags
vault tags --counts                 # with frequency counts
vault tags --counts --sort count    # sorted by frequency
vault tag --name "math"             # notes with this tag
vault tag --name "math" --verbose   # with file list
```

---

## Properties (frontmatter)

```bash
vault properties --file "north star"

vault property:read --name "status" --file "north star"

# Reads current value first, shows diff before writing
vault property:set --name "status" --value "active" --file "north star"
vault property:set --name "tags" --value "math" --type list --file "Mathe I"
vault property:set --name "status" --value "active" --file "north star" --yes

vault property:remove --name "status" --file "north star"
```

---

## Templates

```bash
vault templates                           # list available templates
vault template:read --name "Daily"        # read template content
```

---

## Files and folders

```bash
vault files
vault files --folder "References"
vault files --total
vault folders
```

---

## Utility

```bash
vault ping           # test CouchDB connectivity
vault config show    # show resolved config
vault --version
```
