import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { useEditor } from "../store";
import type { CharacterVersion } from "../types";

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

  if (versions.length === 0)
    return <p className="text-sm text-slate-400">No versions yet.</p>;

  return (
    <ul className="space-y-2">
      {versions.map((v) => (
        <li
          key={v.id}
          className="flex items-center justify-between rounded border border-slate-800 px-3 py-2 text-sm"
        >
          <div>
            <span className="font-medium">v{v.version_number}</span>{" "}
            <span className="text-slate-500">
              {(v.sheet.char_class?.value as string) || "—"} ·{" "}
              {(v.sheet.race?.value as string) || "—"} · L
              {(v.sheet.level?.value as number) || "?"}
            </span>
            <div className="text-xs text-slate-600">
              {v.created_at?.slice(0, 19).replace("T", " ")}
            </div>
          </div>
          <button
            className="rounded border border-slate-700 px-2 py-1 text-xs hover:border-arcane"
            onClick={() => restore(v.version_number)}
          >
            Restore
          </button>
        </li>
      ))}
    </ul>
  );
}
