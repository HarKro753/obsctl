import type { VaultCredentials, StoredAuth } from "./types";

export async function fetchCredentials(backendUrl: string, token: string): Promise<VaultCredentials> {
    const response = await fetch(`${backendUrl}/credentials`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
    if (!response.ok) {
        throw new Error(`Failed to fetch credentials: ${response.status} ${response.statusText}`);
    }
    const data = (await response.json()) as VaultCredentials;
    return data;
}

export function applyCredentialsToSettings(
    credentials: VaultCredentials,
    settings: any // ObsidianLiveSyncSettings — use `any` to avoid deep type imports
): void {
    settings.couchDB_URI = credentials.couchdb_url;
    settings.couchDB_USERNAME = credentials.username;
    settings.couchDB_PASSWORD = credentials.password;
    settings.remoteType = "couchdb";
}

export function isTokenExpired(storedAuth: StoredAuth): boolean {
    return Date.now() > storedAuth.expiresAt - 60_000;
}
