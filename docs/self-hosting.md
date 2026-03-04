# Self-Hosting

Run the full obsctl stack yourself. The backend, CouchDB, and plugin all support self-hosting. MIT license — no restrictions.

---

## Prerequisites

- Docker and Docker Compose
- A Google Cloud project with OAuth 2.0 credentials ([guide](https://console.cloud.google.com/apis/credentials))
- A domain or reverse proxy if you want HTTPS (recommended)

---

## Quickstart

```bash
git clone https://github.com/HarKro753/obsctl
cd obsctl

cp packages/backend/.env.example packages/backend/.env
```

Edit `packages/backend/.env`:

```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3001/auth/callback

JWT_SECRET=change-this-to-a-long-random-string

COUCHDB_URL=http://couchdb:5984
COUCHDB_ADMIN_USER=admin
COUCHDB_ADMIN_PASSWORD=change-this-too

DATABASE_PATH=./data/users.db
PORT=3001
```

Start the stack:

```bash
docker compose up -d
```

The backend is available at `http://localhost:3001`. CouchDB admin UI at `http://localhost:5984/_utils`.

---

## Google OAuth setup

1. Go to [Google Cloud Console → Credentials](https://console.cloud.google.com/apis/credentials)
2. Create an **OAuth 2.0 Client ID** (application type: **Web application**)
3. Add your redirect URI: `https://yourdomain.com/auth/callback`
4. Copy the client ID and secret into `.env`

---

## Production deployment

For production, the recommended path is:

- Kubernetes (see `deploy/` directory, Proxmox-compatible manifests)
- Or any Docker-capable host behind a TLS-terminating reverse proxy (nginx, Caddy, Cloudflare Tunnel)

The backend is stateless aside from SQLite. For multi-instance deployments, point `DATABASE_PATH` at a shared volume or swap SQLite for Postgres.

---

## Configuring the plugin

Once the backend is running:

1. In Obsidian, open **Settings → obsctl**
2. Enable **Use custom server**
3. Set the backend URL to your domain (e.g. `https://sync.yourdomain.com`)
4. Click **Sign in with Google**

---

## Data storage

| Data | Location |
|------|----------|
| User records | SQLite at `DATABASE_PATH` |
| Vault data | CouchDB, one database per user (`vault_<user_id>`) |
| Credentials | SQLite, associated to each user |
| JWTs | Stateless (HS256, 7-day expiry) — no server-side session store |

---

## Backup

Back up the SQLite database and CouchDB data directory. CouchDB stores data at `/opt/couchdb/data` inside the container, mounted to a named Docker volume by default.

```bash
# Backup CouchDB data
docker run --rm \
  -v obsctl_couchdb_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/couchdb-$(date +%Y%m%d).tar.gz /data
```

---

## Updating

```bash
git pull
docker compose pull
docker compose up -d
```
