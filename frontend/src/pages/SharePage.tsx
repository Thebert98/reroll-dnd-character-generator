import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../lib/api";
import type { SharedVersion } from "../types";
import { SheetView } from "../components/SheetView";

/** Public, read-only page for a single character version. No auth required. */
export function SharePage() {
  const { versionId } = useParams<{ versionId: string }>();
  const [data, setData] = useState<SharedVersion | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!versionId) return;
    api.getShared(versionId).then(setData).catch(() => setError(true));
  }, [versionId]);

  if (error)
    return <div className="p-8 text-slate-400">This shared link was not found.</div>;
  if (!data) return <div className="p-8">Loading…</div>;

  return (
    <div className="mx-auto max-w-4xl p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-arcane">{data.character_name}</h1>
        <p className="text-sm text-slate-500">
          Shared character · version {data.version_number}
        </p>
      </div>
      <SheetView sheet={data.sheet} />
      <footer className="mt-8 text-center text-xs text-slate-500">
        Made with Arcane Architect · SRD 5.1 (CC-BY-4.0)
      </footer>
    </div>
  );
}
