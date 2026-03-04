"""VaultClient — CouchDB/LiveSync CRUD operations for Obsidian vaults."""

import hashlib
import re
import time

import requests


def sanitize_unicode(text):
    """Strip dangerous control characters while preserving normal whitespace and Unicode."""
    if not isinstance(text, str):
        return str(text or "")
    return re.sub(r"[\x00-\x08\x0e-\x1f]", "", text)


class VaultClient:
    """Python client for Obsidian vault data stored in CouchDB via LiveSync."""

    def __init__(
        self,
        host="localhost",
        port=5984,
        database="obsidian",
        username="",
        password="",
        protocol="http",
    ):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.protocol = protocol
        self.base_url = f"{protocol}://{host}:{port}/{database}"

        self.session = requests.Session()
        if username:
            self.session.auth = (username, password)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _path_to_id(self, path):
        """Convert a note path to a CouchDB document ID."""
        doc_id = path.lower()
        if doc_id.startswith("_"):
            doc_id = "/" + doc_id
        return doc_id

    def _create_chunks(self, content, chunk_size=50000):
        """Split content into chunks of chunk_size characters."""
        if not content:
            return [""]
        chunks = []
        for i in range(0, len(content), chunk_size):
            chunks.append(content[i : i + chunk_size])
        return chunks if chunks else [""]

    def _create_chunk_id(self, data):
        """Generate a content-addressed chunk ID: h: + first 12 chars of SHA-256."""
        h = hashlib.sha256(data.encode("utf-8")).hexdigest()
        return f"h:{h[:12]}"

    # ------------------------------------------------------------------
    # Connectivity
    # ------------------------------------------------------------------

    def ping(self):
        """Check CouchDB connectivity. Returns dict with ok=True or raises."""
        try:
            resp = self.session.get(self.base_url)
        except Exception as e:
            raise ConnectionError(
                "CouchDB unavailable — is the server running? (Connection refused)"
            ) from e

        if resp.status_code == 401:
            raise PermissionError(
                "CouchDB authentication failed — check credentials in config"
            )
        if resp.status_code == 404:
            raise LookupError("CouchDB database not found — check 'database' in config")

        resp.raise_for_status()
        return {"ok": True}

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def list_notes(self):
        """List all notes, filtering out chunks, system docs, deleted docs."""
        resp = self.session.get(
            f"{self.base_url}/_all_docs", params={"include_docs": "true"}
        )
        resp.raise_for_status()
        data = resp.json()

        notes = []
        for row in data.get("rows", []):
            row_id = row.get("id", "")
            doc = row.get("doc", {})

            # Filter out chunk documents
            if row_id.startswith("h:"):
                continue
            # Filter out system documents
            if row_id.startswith("_"):
                continue
            # Filter out LiveSync version doc
            if row_id == "obsydian_livesync_version":
                continue
            # Filter out deleted docs
            if doc.get("deleted"):
                continue

            notes.append(
                {
                    "path": doc.get("path", ""),
                    "id": row_id,
                    "mtime": doc.get("mtime", 0),
                    "size": doc.get("size", 0),
                }
            )
        return notes

    def read_note(self, path):
        """Read a note by path. Returns dict with content, path, ctime, mtime or None."""
        doc_id = self._path_to_id(path)
        url = f"{self.base_url}/{requests.utils.quote(doc_id, safe='')}"

        resp = self.session.get(url)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()

        metadata = resp.json()

        # Fetch content chunks
        children = metadata.get("children", [])
        chunks = []
        for chunk_id in children:
            chunk_url = f"{self.base_url}/{requests.utils.quote(chunk_id, safe='')}"
            chunk_resp = self.session.get(chunk_url)
            chunk_resp.raise_for_status()
            chunk_data = chunk_resp.json()
            chunks.append(chunk_data.get("data", ""))

        content = "".join(chunks)

        return {
            "path": metadata.get("path", path),
            "content": content,
            "ctime": metadata.get("ctime"),
            "mtime": metadata.get("mtime"),
            "metadata": metadata,
        }

    def write_note(self, path, content, **options):
        """Write or update a note. Returns dict with ok, id, rev."""
        safe_content = sanitize_unicode(content)
        doc_id = self._path_to_id(path)
        now = int(time.time() * 1000)

        # Check if doc already exists
        doc_url = f"{self.base_url}/{requests.utils.quote(doc_id, safe='')}"
        existing_doc = None
        resp = self.session.get(doc_url)
        if resp.status_code == 200:
            existing_doc = resp.json()

        # Create chunks
        chunk_data_list = self._create_chunks(safe_content)
        chunk_ids = []

        for chunk_data in chunk_data_list:
            chunk_id = self._create_chunk_id(chunk_data)
            chunk_ids.append(chunk_id)

            # Check if chunk already exists
            chunk_url = f"{self.base_url}/{requests.utils.quote(chunk_id, safe='')}"
            chunk_resp = self.session.get(chunk_url)
            if chunk_resp.status_code == 404:
                # Create the chunk
                self.session.put(
                    chunk_url,
                    json={"_id": chunk_id, "type": "leaf", "data": chunk_data},
                )

        # Build metadata document
        metadata = {
            "_id": doc_id,
            "children": chunk_ids,
            "path": path,
            "ctime": existing_doc["ctime"] if existing_doc else now,
            "mtime": now,
            "size": len(safe_content.encode("utf-8")),
            "type": options.get("type", "plain"),
            "eden": {},
        }
        if existing_doc:
            metadata["_rev"] = existing_doc["_rev"]

        result_resp = self.session.put(doc_url, json=metadata)
        result_resp.raise_for_status()
        result = result_resp.json()

        return {
            "ok": True,
            "id": result.get("id", doc_id),
            "rev": result.get("rev", ""),
        }

    def delete_note(self, path):
        """Soft-delete a note (LiveSync-compatible)."""
        doc_id = self._path_to_id(path)
        doc_url = f"{self.base_url}/{requests.utils.quote(doc_id, safe='')}"

        resp = self.session.get(doc_url)
        resp.raise_for_status()
        doc = resp.json()

        doc["deleted"] = True
        doc["data"] = ""
        doc["children"] = []
        doc["mtime"] = int(time.time() * 1000)

        put_resp = self.session.put(doc_url, json=doc)
        put_resp.raise_for_status()
        return {"ok": True}

    def move_note(self, from_path, to_path):
        """Move a note from one path to another."""
        note = self.read_note(from_path)
        if not note:
            raise FileNotFoundError(f"Note not found: {from_path}")
        self.write_note(to_path, note["content"])
        self.delete_note(from_path)
        return {"ok": True}

    def search_notes(self, query):
        """Search notes by path (case-insensitive substring match)."""
        notes = self.list_notes()
        lower = query.lower()
        return [note for note in notes if note.get("path", "").lower().find(lower) >= 0]
