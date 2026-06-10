import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { useEditor } from "../store";
import type { CharacterVersion } from "../types";
import { Button } from "./ui/Button";
import { ConfirmDialog } from "./ui/ConfirmDialog";
import { runWithToast, useToast } from "./ui/Toaster";

export function VersionHistory({ characterId }: { characterId: string }) {
  const [versions, setVersions] = useState<CharacterVersion[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [pendingRestore, setPendingRestore] = useState<number | null>(null);
  const setCharacter = useEditor((s) => s.setCharacter);
  const dirty = useEditor((s) => s.dirty);
  const toaster = useToast();

  async function refresh() {
    setLoadError(null);
    try {
      setVersions(await api.listVersions(characterId));
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      setLoadError(msg.replace(/^\d{3}:\s*/, ""));
    }
  }
  useEffect(() => {
    refresh();
  }, [characterId]);

  async function restore(versionNumber: number) {
    const updated = await runWithToast(
      toaster,
      api.restoreVersion(characterId, versionNumber),
      { success: `Restored v${versionNumber}`, failure: "Restore failed" },
    );
    if (updated) setCharacter(updated);
  }

  function requestRestore(versionNumber: number) {
    // Only ask for confirmation when there's something the player would lose.
    if (dirty) {
      setPendingRestore(versionNumber);
    } else {
      restore(versionNumber);
    }
  }

  async function copyShareLink(versionId: string) {
    const url = `${window.location.origin}/share/${versionId}`;
    try {
      await navigator.clipboard.writeText(url);
      toaster.toast("success", "Share link copied");
    } catch {
      toaster.toast("error", "Couldn't reach the clipboard — copy manually");
    }
  }

  if (loadError)
    return (
      <p className="text-sm text-brand-red">
        Could not load version history — {loadError}
      </p>
    );
  if (versions.length === 0)
    return <p className="text-sm text-brand-stone/60">No versions yet.</p>;

  return (
    <ul className="space-y-2">
      {versions.map((v) => (
        <li
          key={v.id}
          className="flex items-center justify-between rounded-lg border border-ink-600/80 bg-ink-700/40 px-3 py-2 text-sm"
        >
          <div>
            <span className="font-heading font-semibold text-brand-gold">
              v{v.version_number}
            </span>{" "}
            <span className="text-brand-stone/60">
              {(v.sheet.char_class?.value as string) || "—"} ·{" "}
              {(v.sheet.race?.value as string) || "—"} · L
              {(v.sheet.level?.value as number) || "?"}
            </span>
            <div className="text-xs text-brand-stone/35">
              {v.created_at?.slice(0, 19).replace("T", " ")}
            </div>
          </div>
          <div className="flex gap-2">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => copyShareLink(v.id)}
              title="Copy a public read-only link to this version"
            >
              Share
            </Button>
            <Button variant="secondary" size="sm" onClick={() => requestRestore(v.version_number)}>
              Restore
            </Button>
          </div>
        </li>
      ))}
      <ConfirmDialog
        open={pendingRestore !== null}
        title={`Restore v${pendingRestore ?? ""}?`}
        body="You have unsaved changes. Restoring will discard them."
        confirmLabel="Restore"
        onConfirm={() => {
          if (pendingRestore !== null) restore(pendingRestore);
          setPendingRestore(null);
        }}
        onCancel={() => setPendingRestore(null)}
      />
    </ul>
  );
}
