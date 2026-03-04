export const MANAGED_BACKEND_URL = "https://sync.harrokrog.com";

export interface AuthState {
    isAuthenticated: boolean;
    token: string | null;
    user: AuthUser | null;
}

export interface AuthUser {
    id: string;
    email: string;
}

export interface VaultCredentials {
    couchdb_url: string;
    username: string;
    password: string;
}

export interface AuthConfig {
    backendUrl: string;
}

export interface StoredAuth {
    token: string;
    email: string;
    expiresAt: number;
}