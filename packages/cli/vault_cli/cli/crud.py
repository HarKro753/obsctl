"""CRUD commands: read, create, write, append, prepend, delete, move, rename."""

import click

from vault_cli.cli.helpers import get_client, output, resolve_file


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

    note = client.read_note(path)
    if note is None:
        click.echo(f"Note not found: {path}", err=True)
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
def create(name, content, folder, template, json_mode):
    """Create a new note."""
    client = get_client()

    # Build path
    if not name.endswith(".md"):
        name = name + ".md"
    if folder:
        path = f"{folder}/{name}"
    else:
        path = name

    # If template specified, read it and use as base content
    if template:
        from vault_cli.config import load_config

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

    result = client.write_note(path, content)

    if json_mode:
        output(result, json_mode=True)
    else:
        click.echo(f"Created: {path}")


@click.command("write")
@click.option("--path", "file_path", required=True, help="Exact path from vault root")
@click.option("--content", required=True, help="Note content")
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON")
def write_cmd(file_path, content, json_mode):
    """Write content to a note (create or overwrite)."""
    client = get_client()
    result = client.write_note(file_path, content)

    if json_mode:
        output(result, json_mode=True)
    else:
        click.echo(f"Written: {file_path}")


@click.command()
@click.option("--file", "file_name", required=True, help="Note name")
@click.option("--content", required=True, help="Content to append")
@click.option("--inline", is_flag=True, help="No newline separator")
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON")
def append(file_name, content, inline, json_mode):
    """Append content to an existing note."""
    client = get_client()
    path = resolve_file(client, file_name)

    note = client.read_note(path)
    if note is None:
        click.echo(f"Note not found: {path}", err=True)
        raise SystemExit(1)

    separator = "" if inline else "\n"
    new_content = note["content"] + separator + content
    result = client.write_note(path, new_content)

    if json_mode:
        output(result, json_mode=True)
    else:
        click.echo(f"Appended to: {path}")


@click.command()
@click.option("--file", "file_name", required=True, help="Note name")
@click.option("--content", required=True, help="Content to prepend")
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON")
def prepend(file_name, content, json_mode):
    """Prepend content to an existing note."""
    client = get_client()
    path = resolve_file(client, file_name)

    note = client.read_note(path)
    if note is None:
        click.echo(f"Note not found: {path}", err=True)
        raise SystemExit(1)

    new_content = content + "\n" + note["content"]
    result = client.write_note(path, new_content)

    if json_mode:
        output(result, json_mode=True)
    else:
        click.echo(f"Prepended to: {path}")


@click.command("delete")
@click.option("--file", "file_name", required=True, help="Note name")
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON")
def delete_cmd(file_name, json_mode):
    """Delete a note (soft-delete, LiveSync compatible)."""
    client = get_client()
    path = resolve_file(client, file_name)

    result = client.delete_note(path)

    if json_mode:
        output(result, json_mode=True)
    else:
        click.echo(f"Deleted: {path}")


@click.command()
@click.option("--file", "file_name", required=True, help="Source note name")
@click.option("--to", "to_path", required=True, help="Destination path")
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON")
def move(file_name, to_path, json_mode):
    """Move a note to a new path."""
    client = get_client()
    path = resolve_file(client, file_name)

    result = client.move_note(path, to_path)

    if json_mode:
        output(result, json_mode=True)
    else:
        click.echo(f"Moved: {path} -> {to_path}")


@click.command()
@click.option("--file", "file_name", required=True, help="Note name")
@click.option("--name", "new_name", required=True, help="New name")
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON")
def rename(file_name, new_name, json_mode):
    """Rename a note (keeps same folder)."""
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

    result = client.move_note(path, new_path)

    if json_mode:
        output(result, json_mode=True)
    else:
        click.echo(f"Renamed: {path} -> {new_path}")
