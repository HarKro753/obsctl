import { Setting } from "@/deps.ts";
import { openSignInPage } from "../auth/oauth";
import { isTokenExpired } from "../auth/credentials";
import { type StoredAuth } from "../auth/types";

export interface AuthScreenOptions {
    containerEl: HTMLElement;
    plugin: any; // plugin instance with plugin.settings and plugin.saveSettings()
    backendUrl: string;
    onCredentialsApplied: () => void;
}

export function renderAuthScreen(opts: AuthScreenOptions): void {
    const { containerEl, plugin, backendUrl, onCredentialsApplied } = opts;
    const storedAuth: StoredAuth | null = (plugin.settings as any)._managedAuth ?? null;
    const isSignedIn = storedAuth !== null && !isTokenExpired(storedAuth);

    containerEl.createEl("h3", { text: "Managed Sync" });

    if (isSignedIn) {
        new Setting(containerEl)
            .setName("Connected")
            .setDesc(`Signed in as ${storedAuth.email}`)
            .addButton((btn) =>
                btn.setButtonText("Sign out").onClick(async () => {
                    delete (plugin.settings as any)._managedAuth;
                    await plugin.saveSettings();
                    onCredentialsApplied();
                })
            );
    } else {
        new Setting(containerEl)
            .setName("Sign in with Google")
            .setDesc("One click — vault syncs automatically. No server setup required.")
            .addButton((btn) =>
                btn
                    .setButtonText("Sign in with Google")
                    .setCta()
                    .onClick(() => {
                        openSignInPage(backendUrl);
                        new Setting(containerEl)
                            .setName("Waiting for sign-in...")
                            .setDesc(
                                "Complete sign-in in your browser. The plugin will update automatically."
                            );
                    })
            );
    }

    containerEl.createEl("hr");

    new Setting(containerEl)
        .setName("Use custom server")
        .setDesc("Advanced: configure your own CouchDB or self-hosted backend instead.")
        .addToggle((toggle) => {
            toggle.setValue(!isSignedIn);
            toggle.onChange((val) => {
                const manualPanel = containerEl
                    .closest(".vertical-tab-content")
                    ?.querySelector(".oms-manual-couchdb") as HTMLElement | null;
                if (manualPanel) manualPanel.style.display = val ? "" : "none";
            });
        });
}
