"""CRUD commands: read, create, write, append, prepend, delete, move, rename."""

import difflib
import os

import click

from vault_cli.cli.errors import handle_write_error, handle_delete_error
from vault_cli.cli.helpers import get_client, output, resolve_file
from vault_cli.core.backlinks import update_backlinks


@click.command()
@click.option(
    "--file", "file_name", default=None, help="Note name (wikilink-style resolution)"
)
@click.option("--path", "file_path", default=None, help="Exact path from vault root")
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON")
def read(file_name, file_path, json_mode):
    """Read a note's content."""
    if not file_name and not file_path:
        click.echo("Error: provide --file or --path", err=True)
        raise SystemExit(1)

    client = get_client()

    if file_path:
        path = file_path
    else:
        path = resolve_file(client, file_name)

    try:
        note = client.read_note(path)
    except ConnectionError as e:
        click.echo(f'Error reading "{path}":\n  {e}\n  Check: vault ping', err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f'Error reading "{path}":\n  {e}', err=True)
        raise SystemExit(1)

    if note is None:
        click.echo(
            f'Error reading "{path}":\n'
            f"  Note not found.\n"
            f'  Use `vault files` to browse, or `vault search query="{path.rsplit("/", 1)[-1].replace(".md", "")}"` to find it.',
            err=True,
        )
        raise SystemExit(1)

    if json_mode:
        output(
            {
                "path": note["path"],
                "content": note["content"],
                "ctime": note["ctime"],
                "mtime": note["mtime"],
            },
            json_mode=True,
        )
    else:
        click.echo(note["content"])


@click.command()
@click.option("--name", required=True, help="Note name")
@click.option("--content", default="", help="Note content")
@click.option("--folder", default=None, help="Target folder (e.g. References)")
@click.option("--template", default=None, help="Template name to use")
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON")
@click.option("--dry-run", is_flag=True, help="Show what would happen without writing")
def create(name, content, folder, template, json_mode, dry_run):
    """Create a new note."""
    client = get_client()

    # Build path
    if not name.endswith(".md"):
        name = name + ".md"
    if folder:
        path = f"{folder}/{name}"
    else:
        path = name

    # Check if note already exists — by exact path or by name in vault
    existing = client.read_note(path)
    if existing is not None:
        click.echo(
            f"Note already exists: {path}\n"
            f'Use `vault write --path "{path}" --force` to overwrite.\n'
            f"Aborted.",
            err=True,
        )
        raise SystemExit(1)

    # Also check by basename across all notes (like wikilink resolution)
    name_lower = name.lower()
    for note in client.list_notes():
        note_path = note["path"]
        basename = note_path.rsplit("/", 1)[-1] if "/" in note_path else note_path
        if basename.lower() == name_lower:
            click.echo(
                f"Note already exists: {note_path}\n"
                f'Use `vault write --path "{note_path}" --force` to overwrite.\n'
                f"Aborted.",
                err=True,
            )
            raise SystemExit(1)

    # If template specified, read it and use as base content
    if template:
        from vault_cli.core.config import load_config

        config = load_config()
        templates_folder = config.get("templates_folder", "Templates")
        template_name = template if template.endswith(".md") else template + ".md"
        template_note = client.read_note(f"{templates_folder}/{template_name}")
        if template_note:
            content = template_note["content"]
            # Replace template variables
            content = content.replace("{{name}}", name.replace(".md", ""))
            content = content.replace("{{title}}", name.replace(".md", ""))
        else:
            click.echo(f"Template not found: {template}", err=True)
            raise SystemExit(1)

    if dry_run:
        click.echo(f"Would create: {path} ({len(content)} chars)")
        return

    try:
        result = client.write_note(path, content)
    except Exception as e:
        handle_write_error(path, e)

    if json_mode:
        output(result, json_mode=True)
    else:
        click.echo(f"Created: {path}")


@click.command("write")
@click.option("--path", "file_path", required=True, help="Exact path from vault root")
@click.option("--content", required=True, help="Note content")
@click.option("--force", is_flag=True, help="Overwrite existing note without prompt")
@click.option(
    "--diff", "show_diff", is_flag=True, help="Show unified diff of changes, no write"
)
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON")
@click.option("--dry-run", is_flag=True, help="Show what would happen without writing")
def write_cmd(file_path, content, force, show_diff, json_mode, dry_run):
    """Write content to a note (create or overwrite)."""
    client = get_client()

    # Check if doc already exists
    existing = client.read_note(file_path)

    if existing is not None:
        existing_content = existing["content"]
        existing_size = len(existing_content)
        is_deleted = existing.get("metadata", {}).get("deleted", False)

        # --diff: show what would change, then exit
        if show_diff:
            old_lines = existing_content.splitlines(keepends=True)
            new_lines = content.splitlines(keepends=True)
            diff = difflib.unified_diff(
                old_lines,
                new_lines,
                fromfile=f"a/{file_path}",
                tofile=f"b/{file_path}",
            )
            diff_text = "".join(diff)
            if diff_text:
                click.echo(diff_text)
            else:
                click.echo("No changes.")
            return

        # --dry-run: show what would happen
        if dry_run:
            click.echo(
                f"Would write {len(content)} chars to {file_path} "
                f"(currently {existing_size} chars)"
            )
            return

        # deleted:true detection
        if is_deleted:
            if not force:
                click.echo(
                    f"Warning: note exists but is marked deleted in CouchDB.\n"
                    f"Writing will restore it. Use --force to proceed.\n"
                    f"Aborted.",
                    err=True,
                )
                raise SystemExit(1)

        # Refuse silent overwrite without --force
        if not force:
            click.echo(
                f"Note already exists ({existing_size} chars).\n"
                f"Use --force to overwrite, or --diff to preview changes.\n"
                f"Aborted.",
                err=True,
            )
            raise SystemExit(1)
    else:
        # New note
        if show_diff:
            # Show all content as additions
            new_lines = content.splitlines(keepends=True)
            diff = difflib.unified_diff(
                [],
                new_lines,
                fromfile="/dev/null",
                tofile=f"b/{file_path}",
            )
            diff_text = "".join(diff)
            if diff_text:
                click.echo(diff_text)
            else:
                click.echo(f"New file: {file_path} ({len(content)} chars)")
            return

        if dry_run:
            click.echo(f"Would write {len(content)} chars to {file_path} (new file)")
            return

    try:
        result = client.write_note(file_path, content)
    except Exception as e:
        handle_write_error(file_path, e)

    if json_mode:
        output(result, json_mode=True)
    else:
        click.echo(f"Written: {file_path}")


@click.command()
@click.option("--file", "file_name", required=True, help="Note name")
@click.option("--content", required=True, help="Content to append")
@click.option("--inline", is_flag=True, help="No newline separator")
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON")
@click.option("--dry-run", is_flag=True, help="Show what would happen without writing")
def append(file_name, content, inline, json_mode, dry_run):
    """Append content to an existing note."""
    client = get_client()
    path = resolve_file(client, file_name)

    note = client.read_note(path)
    if note is None:
        click.echo(f"Note not found: {path}", err=True)
        raise SystemExit(1)

    separator = "" if inline else "\n"
    new_content = note["content"] + separator + content

    if dry_run:
        click.echo(f"Would append {len(content)} chars to: {path}")
        return

    try:
        result = client.write_note(path, new_content)
    except Exception as e:
        handle_write_error(path, e)

    if json_mode:
        output(result, json_mode=True)
    else:
        click.echo(f"Appended to: {path}")


@click.command()
@click.option("--file", "file_name", required=True, help="Note name")
@click.option("--content", required=True, help="Content to prepend")
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON")
@click.option("--dry-run", is_flag=True, help="Show what would happen without writing")
def prepend(file_name, content, json_mode, dry_run):
    """Prepend content to an existing note."""
    client = get_client()
    path = resolve_file(client, file_name)

    note = client.read_note(path)
    if note is None:
        click.echo(f"Note not found: {path}", err=True)
        raise SystemExit(1)

    new_content = content + "\n" + note["content"]

    if dry_run:
        click.echo(f"Would prepend {len(content)} chars to: {path}")
        return

    try:
        result = client.write_note(path, new_content)
    except Exception as e:
        handle_write_error(path, e)

    if json_mode:
        output(result, json_mode=True)
    else:
        click.echo(f"Prepended to: {path}")


@click.command("delete")
@click.option("--file", "file_name", required=True, help="Note name")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt")
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON")
@click.option("--dry-run", is_flag=True, help="Show what would happen without deleting")
def delete_cmd(file_name, yes, json_mode, dry_run):
    """Delete a note (soft-delete, LiveSync compatible)."""
    client = get_client()
    path = resolve_file(client, file_name)

    if dry_run:
        click.echo(f"Would soft-delete: {path}")
        return

    if not yes:
        confirmed = click.confirm(f'Delete "{path}"?', default=False)
        if not confirmed:
            click.echo("Aborted.")
            return

    try:
        result = client.delete_note(path)
    except Exception as e:
        handle_delete_error(path, e)

    if json_mode:
        output(result, json_mode=True)
    else:
        click.echo(f"Deleted: {path}")


@click.command()
@click.option("--file", "file_name", required=True, help="Source note name")
@click.option("--to", "to_path", required=True, help="Destination path")
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON")
@click.option("--dry-run", is_flag=True, help="Show what would happen without moving")
@click.option(
    "--no-backlinks", is_flag=True, help="Skip backlink rewriting (legacy behaviour)"
)
def move(file_name, to_path, json_mode, dry_run, no_backlinks):
    """Move a note to a new path. Rewrites backlinks if the filename changes."""
    client = get_client()
    path = resolve_file(client, file_name)

    # Detect if the filename (not just folder) changed
    old_name = _basename_no_ext(path)
    new_name = _basename_no_ext(to_path)
    name_changed = old_name.lower() != new_name.lower()

    if dry_run:
        click.echo(f"Would move: {path} -> {to_path}")
        if name_changed and not no_backlinks:
            bl = update_backlinks(client, old_name, new_name, dry_run=True)
            _echo_backlink_report(bl, dry_run=True)
        return

    result = client.move_note(path, to_path)

    bl_result = None
    if name_changed and not no_backlinks:
        bl_result = update_backlinks(client, old_name, new_name)

    if json_mode:
        data = {"ok": True, "moved": f"{path} -> {to_path}"}
        if bl_result:
            data["backlinks"] = bl_result
        output(data, json_mode=True)
    else:
        click.echo(f"Moved: {path} -> {to_path}")
        if bl_result and bl_result["total_links"] > 0:
            _echo_backlink_report(bl_result)
        elif name_changed and not no_backlinks:
            click.echo("No backlink updates needed.")


@click.command()
@click.option("--file", "file_name", required=True, help="Note name")
@click.option("--name", "new_name", required=True, help="New name")
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON")
@click.option("--dry-run", is_flag=True, help="Show what would happen without renaming")
@click.option(
    "--no-backlinks", is_flag=True, help="Skip backlink rewriting (legacy behaviour)"
)
def rename(file_name, new_name, json_mode, dry_run, no_backlinks):
    """Rename a note (keeps same folder). Rewrites backlinks across the vault."""
    client = get_client()
    path = resolve_file(client, file_name)

    # Keep the same folder, change the filename
    if "/" in path:
        folder = path.rsplit("/", 1)[0]
        new_path = f"{folder}/{new_name}"
    else:
        new_path = new_name

    if not new_path.endswith(".md"):
        new_path += ".md"

    old_name = _basename_no_ext(path)

    if dry_run:
        click.echo(f"Would rename: {path} -> {new_path}")
        if not no_backlinks:
            bl = update_backlinks(client, old_name, new_name, dry_run=True)
            _echo_backlink_report(bl, dry_run=True)
        return

    result = client.move_note(path, new_path)

    bl_result = None
    if not no_backlinks:
        bl_result = update_backlinks(client, old_name, new_name)

    if json_mode:
        data = {"ok": True, "renamed": f"{path} -> {new_path}"}
        if bl_result:
            data["backlinks"] = bl_result
        output(data, json_mode=True)
    else:
        click.echo(f"Renamed: {path} -> {new_path}")
        if bl_result:
            _echo_backlink_report(bl_result)


# ---------------------------------------------------------------------------
# Helpers for backlink reporting
# ---------------------------------------------------------------------------


def _basename_no_ext(path):
    """Extract basename without .md extension from a vault path."""
    basename = os.path.basename(path)
    if basename.lower().endswith(".md"):
        return basename[:-3]
    return basename


def _echo_backlink_report(bl_result, dry_run=False):
    """Print a human-readable backlink update report."""
    total = bl_result["total_links"]
    notes = bl_result["total_notes"]
    details = bl_result.get("details", [])

    if total == 0:
        if dry_run:
            click.echo("No backlinks to update.")
        return

    prefix = "Would update" if dry_run else "Updated"
    link_word = "backlink" if total == 1 else "backlinks"
    note_word = "note" if notes == 1 else "notes"
    click.echo(f"{prefix} {total} {link_word} in {notes} {note_word}:")
    for detail in details:
        count = detail["count"]
        link_label = "link" if count == 1 else "links"
        click.echo(f"  - {detail['path']} ({count} {link_label})")
