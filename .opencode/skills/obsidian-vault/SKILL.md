---
name: obsidian-vault
description: Opinionated Obsidian vault design system — folder structure, properties, categories, composable templates, aggressive linking, base patterns, and graph-based retrieval. Use when creating, organizing, or finding notes, deciding where a note should go, writing frontmatter, choosing categories, composing templates, or reasoning about knowledge stored in the vault.
---

# Obsidian Vault System

Bottom-up, chaos-embracing vault design. Folders are infrastructure, properties are meaning, links are connections, bases are views, templates are speed.

## Related skill

- **obsidian-reference** — CLI commands, Obsidian-specific Markdown syntax, and Bases `.base` file syntax. Use when you need command syntax or format details.

---

## Core Philosophy

1. **Folders are for infrastructure, not organization** — never categorize by folder
2. **Properties are for meaning** — `categories`, `type`, `tags` do all classification
3. **Links are for connections** — wikilinks in body text and in properties create the knowledge graph
4. **Bases are for views** — `.base` files surface notes dynamically, embedded directly in notes
5. **Templates are for speed** — every replicable pattern gets a template; compose, don't duplicate
6. **Link everything, even what doesn't exist yet** — unresolved links are knowledge gaps and breadcrumbs

### The golden rule

> Never ask "where should I put this?" — it goes in the root (your world) or References (the external world). Add properties. Done.

---

## Folder Structure

```
Vault/
├── References/      ← External world (books, people, podcasts, technologies, others' projects)
├── Clippings/       ← Things other people wrote (articles, essays, web clips)
├── Attachments/     ← Images, PDFs, audio, video
├── Templates/       ← Note templates (composable)
│   └── Bases/       ← .base files (query engines)
├── Categories/      ← Category overview pages (each embeds a base)
├── Daily/           ← Daily notes (YYYY-MM-DD.md)
├── *.md             ← YOUR world: projects, ideas, truths, journal, evergreen notes
```

### Placement rules

| Note is about...                                              | Put in...      | Why                   |
| ------------------------------------------------------------- | -------------- | --------------------- |
| Your project, idea, truth, course, journal, evergreen insight | Root `/`       | Your world            |
| A book, person, podcast, technology, someone else's project   | `References/`  | External world        |
| An article or essay someone else wrote                        | `Clippings/`   | Someone else wrote it |
| An image, PDF, audio, or video file                           | `Attachments/` | Binary assets         |

---

## Properties System

### Categories use wikilinks

The `categories` property is a **list of wikilinks** pointing to Category pages — the primary classification mechanism.

```yaml
categories:
  - "[[Ideas]]"
  - "[[Projects]]" # a note can have multiple categories
```

### References in properties use wikilinks

Any property referencing another entity uses `[[wikilinks]]`, even if the target note doesn't exist yet:

```yaml
author:
  - "[[Peter Thiel]]"
show:
  - "[[Founders]]"
org:
  - "[[Obsidian]]"
topics:
  - "[[Emergence]]"
```

### The `type` property enables composition

`type` is a list of wikilinks representing **roles** layered on top of the base category:

```yaml
# An Author is a Person with the Authors role
categories:
  - "[[People]]"
type:
  - "[[Authors]]"
```

### Standard properties

| Property     | Type         | Used by                | Description                                 |
| ------------ | ------------ | ---------------------- | ------------------------------------------- |
| `categories` | list (links) | All notes              | Primary classification via `[[wikilinks]]`  |
| `type`       | list (links) | Composed notes         | Role/sub-type for composition               |
| `status`     | text         | Projects, Ideas        | active, paused, finished, abandoned         |
| `tags`       | list (text)  | All notes              | Secondary classification, always pluralized |
| `rating`     | number       | Books, References      | 1-7 scale (7=perfect, 4=passable, 1=evil)   |
| `author`     | list (links) | Books, Clippings       | Who created it                              |
| `genre`      | list (links) | Books, Movies, Shows   | Shared across media                         |
| `topics`     | list (links) | Books, Episodes, Ideas | Subject matter links                        |
| `url`        | text         | Projects, References   | External URL                                |
| `created`    | date         | All notes              | YYYY-MM-DD                                  |
| `start`      | date         | Projects, Trips        | Start date                                  |
| `published`  | date         | Episodes, Posts        | Publication date                            |

### Property rules

- Default to **list type** if there's any chance of multiple values
- **Short names**: `start` not `start-date`, `org` not `organization`
- **Reuse names across categories**: `genre` works for books, movies, and shows
- **Use `[[wikilinks]]`** for anything referencing another entity

---

## Aggressive Linking

**Link every meaningful entity, even when no note exists for it yet.** Unresolved links are knowledge gaps and future connections.

Raw: `Elon Musk wrote about "We live and die only once" on Saturn`
Linked: `[[Elon Musk]] wrote about [[We live and die only once]] on [[Saturn]]`

### What to link

People, places, quotes, concepts, projects, events — link the **first mention** in a note's body.

### Rules

1. Link first mentions of any named entity
2. Unresolved links are features, not bugs — they reveal knowledge gaps
3. Quotes worth remembering get their own link
4. Properties use links too — `author: - "[[Person Name]]"` even if the note doesn't exist

### ⚠️ Stub Rule (mandatory)

**Every `[[wikilink]]` you write must have a corresponding note — even if it's just a stub.**

After creating any note, scan every wikilink in its body and create stub reference notes for anything that doesn't exist yet. A stub needs only:

```yaml
---
categories:
  - "[[References]]"
tags:
  - <relevant-tag>
created: YYYY-MM-DD
---
# Concept Name

> One-line definition.

## Links
- [[parent-note]] ← context
```

No note is an island. No link should be dead. Stubs are placeholders that get filled in over time — they still make the graph navigable.

---

## Categories

Categories are **not hardcoded** — they are whatever already exists in the vault. Always discover dynamically before assigning.

### Discovering existing categories

```bash
vault files --folder "Categories"                         # list all category pages
vault tags --counts --sort count                          # see tag landscape
vault search --query "categories:" --context --limit 20   # sample how notes use categories
```

Pick categories from what already exists. If none fit, create a new one — it's just a page + a base file.

### Category page pattern

Each category has a page in `Categories/` that embeds its base:

```yaml
---
tags:
  - categories
---
```

Followed by: `![[Books.base]]`

---

## Composable Templates

> An Author is not a different thing from a Person — it's a Person with the Authors role layered on.

1. **Base templates** define the "noun" — set `categories`, define core properties
2. **Role templates** add a `type` and embed contextual bases (e.g., Author template adds `type: [[Authors]]` + `![[Books.base#Author]]`)
3. **Apply multiple templates** to compose identity

### Rules

- Every replicable pattern gets a template
- Compose, don't duplicate — never create a separate category for a role
- Include embedded bases in templates
- Use `{{date}}` for `created`

---

## Base Patterns

Bases live in `Templates/Bases/` and are embedded in notes via `![[BaseName.base]]` or `![[BaseName.base#ViewName]]`.

### Contextual views with `this`

```yaml
views:
  - type: table
    name: Author
    filters:
      and:
        - list(author).contains(this)
    order: [file.name, year, genre]
```

Embedded via `![[Books.base#Author]]` in a person's note — shows only their books.

### Category filtering

```yaml
filters:
  and:
    - categories.contains(link("Books"))
    - '!file.name.contains("Template")'
```

### Where bases are embedded

| Note type       | Embedded base                      | Shows                        |
| --------------- | ---------------------------------- | ---------------------------- |
| Category page   | `![[Books.base]]`                  | All books                    |
| Person (Author) | `![[Books.base#Author]]`           | Books by this person         |
| Podcast         | `![[Podcast episodes.base#Show]]`  | Episodes for this show       |
| Person (Guest)  | `![[Podcast episodes.base#Guest]]` | Episodes featuring them      |
| Technology      | `![[Projects.base#Technology]]`    | Projects using this tech     |
| Any note        | `![[Related.base]]`                | Notes with overlapping links |
| Any note        | `![[Backlinks.base]]`              | Notes linking here           |

### Rules

- Every category needs a base
- Include a `this`-filtered view for contextual embedding
- Always exclude templates: `'!file.name.contains("Template")'`

---

## Retrieval: ENTER -> TRAVERSE -> EXTRACT

The vault is a **knowledge graph**. Notes are nodes, wikilinks are edges, Category pages are hubs. Navigate by traversal, not filesystem search.

### Phase 1: ENTER (pick highest-precision entry point)

1. **Direct name** — you know the note → open it (O(1))
2. **Category page** — you know the type → open `Categories/Books.md` (O(1))
3. **Related entity** — you know a connected note → open it, traverse links
4. **Property query** — grep frontmatter for `author`, `topics`, etc. (O(n))
5. **Full-text search** — last resort → search body, then switch to traversal (O(n))

### Phase 2: TRAVERSE (follow edges, rarely >2-3 hops)

| Edge type              | Source                      | Direction |
| ---------------------- | --------------------------- | --------- |
| Body wikilinks         | `[[Name]]` in body          | Forward   |
| Property wikilinks     | `author: - "[[Person]]"`    | Forward   |
| Backlinks              | Notes linking TO this note  | Reverse   |
| Category co-membership | Notes sharing `categories`  | Lateral   |
| Shared properties      | Notes sharing author, topic | Lateral   |

### Phase 3: EXTRACT

1. **Frontmatter first** — properties answer 80% of metadata questions
2. **Body second** — narrative content, links as relationships, headers as structure

### Common patterns

- **"What do I know about X?"** → Open X → frontmatter → body → backlinks → outgoing links
- **"All books about Y"** → Category page → scan → filter by topics/tags
- **"Connected to this note?"** → Outgoing links + backlinks → read neighbors
- **"Relationship A to B"** → Open A → check link to B (1-hop) → neighbors (2-hop) → backlink overlap

---

## Style Rules

1. Avoid folders for organization — infrastructure only
2. Always pluralize categories and tags — `books` not `book`
3. Use `[[wikilinks]]` in properties
4. Use `YYYY-MM-DD` dates everywhere
5. Link aggressively — even unresolved
6. Every replicable pattern gets a template
7. Compose templates with `type` — never a separate category for a role
8. Embed bases in notes — not just category dashboards
9. One vault for everything
10. Navigate via Quick Switcher, backlinks, and links — not the file explorer

---

## Migration Checklist (from folder-based vault)

1. Create infrastructure folders: `References/`, `Clippings/`, `Attachments/`, `Templates/`, `Templates/Bases/`, `Categories/`, `Daily/`
2. Create composable templates in `Templates/`
3. Create `.base` files in `Templates/Bases/`
4. Create Category pages in `Categories/` (each embeds its base)
5. Move reference notes to `References/`, personal notes to root
6. Update frontmatter: `categories: - "[[X]]"`, add `type` for composed roles
7. Add embedded bases to notes for contextual views
8. Delete old empty folders

---

## Workflow: Creating a New Note

Every note creation follows three phases: **discover → create → connect**.

### Phase 1: DISCOVER (understand the vault context)

Before creating, query the vault to make informed decisions:

```bash
# 1. What categories exist?
vault files --folder "Categories"

# 2. What templates are available?
vault templates

# 3. Does a similar note already exist?
vault search --query "<topic>"

# 4. What tags are commonly used?
vault tags --counts --sort count
```

Choose categories from what exists. Choose a template that fits (or compose multiple).

### Phase 2: CREATE (write the note)

1. **Root or References?** — Your world or external world?
2. **Apply template(s)** — compose with `categories` + `type`
3. **Fill properties** — `[[wikilinks]]` for all entities, even if notes don't exist yet
4. **Write body + link aggressively** — people, places, quotes, concepts
5. **Embed bases** — contextual views like `![[Books.base#Author]]`

### Phase 3: CONNECT (weave into the knowledge graph)

After creating the note, actively strengthen its connections:

```bash
# 1. Find notes that should reference the new note
vault search --query "<key terms from new note>" --context

# 2. Check what links TO related topics
vault backlinks --file "<related note>"

# 3. Find notes sharing the same categories/topics
vault search --query "<category or topic>" --context
```

For each relevant existing note found:

- **Add a `[[wikilink]]` to the new note** in the existing note's body where it's contextually relevant
- **Add shared `topics` or `tags`** to the new note's frontmatter if discovered during traversal
- **Add property cross-references** (e.g., if a Person note is relevant, add them to `author`, `guests`, etc.)

The goal: no note is an island. Every new note should have at least 2-3 incoming links from existing notes by the time you're done.
