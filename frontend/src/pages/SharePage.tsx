import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../lib/api";
import type { SharedVersion } from "../types";
import { SheetView } from "../components/SheetView";
import { Logo } from "../components/brand/Logo";

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
    return <div className="p-8 text-brand-stone/60">This shared link was not found.</div>;
  if (!data) return <div className="p-8">Loading…</div>;

  return (
    <div className="mx-auto max-w-4xl p-6">
      <div className="mb-8 flex items-end justify-between border-b border-ink-600/70 pb-4">
        <div>
          <h1 className="font-heading text-3xl font-bold text-brand-gold">
            {data.character_name}
          </h1>
          <p className="text-sm text-brand-stone/50">
            Shared character · version {data.version_number}
          </p>
        </div>
        <Logo size="sm" to="/" />
      </div>
      <SheetView sheet={data.sheet} />
      <footer className="mt-10 flex flex-col items-center gap-2 text-center text-xs text-brand-stone/40">
        <Logo size="sm" showSubtitle={false} />
        <span>Made with Re:Roll · SRD 5.1 (CC-BY-4.0)</span>
      </footer>
    </div>
  );
}
