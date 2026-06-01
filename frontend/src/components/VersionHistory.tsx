import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { useEditor } from "../store";
import type { CharacterVersion } from "../types";
import { Button } from "./ui/Button";

export function VersionHistory({ characterId }: { characterId: string }) {
  const [versions, setVersions] = useState<CharacterVersion[]>([]);
  const setCharacter = useEditor((s) => s.setCharacter);

  async function refresh() {
    setVersions(await api.listVersions(characterId));
  }
  useEffect(() => {
    refresh();
  }, [characterId]);

  async function restore(versionNumber: number) {
    const updated = await api.restoreVersion(characterId, versionNumber);
    setCharacter(updated);
  }

  function copyShareLink(versionId: string) {
    const url = `${window.location.origin}/share/${versionId}`;
    navigator.clipboard?.writeText(url);
  }

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
            <Button variant="secondary" size="sm" onClick={() => restore(v.version_number)}>
              Restore
            </Button>
          </div>
        </li>
      ))}
    </ul>
  );
}
