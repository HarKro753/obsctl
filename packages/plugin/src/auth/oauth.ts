import { MANAGED_BACKEND_URL } from "./types";

export function openSignInPage(backendUrl = MANAGED_BACKEND_URL): void {
    (window as any).open(`${backendUrl}/auth/google`, "_blank");
}

export function parseCallbackToken(callbackParams: URLSearchParams): string | null {
    return callbackParams.get("token");
}

export function decodeTokenEmail(token: string): string {
    try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        return payload.email ?? "unknown";
    } catch {
        return "unknown";
    }
}

export function getTokenExpiry(token: string): number {
    try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        return (payload.exp ?? 0) * 1000;
    } catch {
        return 0;
    }
}
