# Plugin

The obsctl plugin is a fork of [obsidian-livesync](https://github.com/vrtmrz/obsidian-livesync) with a single change: the manual CouchDB configuration screen is replaced with a **Sign in with Google** button.

All sync logic — conflict resolution, chunking, E2E encryption, delta sync, P2P — is unchanged from upstream.

---

## Installation

The plugin is not yet listed in the Obsidian community plugin directory. Install manually:

1. Download the latest release from [Releases](https://github.com/HarKro753/obsctl/releases)
2. Copy `main.js`, `manifest.json`, and `styles.css` into your vault's `.obsidian/plugins/obsctl/` directory
3. Enable the plugin in **Settings → Community Plugins**

---

## Sign in with Google

1. Open **Settings → obsctl**
2. Click **Sign in with Google**
3. Complete sign-in in your browser
4. The plugin receives your credentials automatically and begins syncing

That's it. No server URLs, no username/password fields, no CouchDB documentation required.

---

## Self-hosted backend

If you're running your own backend (see [self-hosting.md](self-hosting.md)):

1. Open **Settings → obsctl**
2. Enable **Use custom server**
3. Enter your backend URL
4. Click **Sign in with Google** — the OAuth flow targets your server

---

## Manual CouchDB (advanced)

For direct CouchDB access without the backend:

1. Open **Settings → obsctl**
2. Enable **Use custom server**
3. Enable **Direct CouchDB connection**
4. Enter your CouchDB URL, database, username, and password

This is the original LiveSync flow, preserved for self-hosters and power users.

---

## Building from source

```bash
cd packages/plugin
bun install
bun run build    # outputs main.js
bun run dev      # watch mode
```

Requires [Bun](https://bun.sh) and Node.js.

---

## OAuth callback

The plugin registers the `obsidian://obsctl-auth` URI scheme. After Google OAuth completes, the backend redirects to this URI with a JWT token. The plugin:

1. Receives the token via the URI handler
2. Calls `/credentials` on the backend
3. Applies the returned CouchDB credentials to its settings
4. Begins syncing

No token is ever stored in plaintext outside Obsidian's encrypted plugin data.
