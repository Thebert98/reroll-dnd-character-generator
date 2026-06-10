import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import type { Character } from "../types";
import { Button } from "./ui/Button";
import { Badge } from "./ui/Badge";
import { runWithToast, useToast } from "./ui/Toaster";

// A character counts as "AI generated" once any field carries a source note.
function isGenerated(c: Character): boolean {
  return Object.values(c.sheet || {}).some(
    (f) => f && typeof f === "object" && "source" in f && (f as { source?: string }).source
  );
}

export function CharacterList() {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const nav = useNavigate();
  const toaster = useToast();

  async function refresh() {
    setLoadError(null);
    try {
      setCharacters(await api.listCharacters());
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      setLoadError(msg.replace(/^\d{3}:\s*/, ""));
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => {
    refresh();
  }, []);

  async function create() {
    setCreating(true);
    const c = await runWithToast(
      toaster,
      api.createCharacter("Untitled"),
      { failure: "Could not create character" },
    );
    setCreating(false);
    if (c) nav(`/characters/${c.id}`);
  }

  if (loading) return <div className="text-brand-stone/60">Loading characters…</div>;
  if (loadError)
    return (
      <div className="rounded-xl border border-brand-red/40 bg-brand-red/10 p-4 text-sm text-brand-red">
        Could not load characters — {loadError}{" "}
        <button
          onClick={refresh}
          className="ml-2 underline hover:text-brand-stone"
        >
          Retry
        </button>
      </div>
    );

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h2 className="font-heading text-2xl font-bold text-brand-stone">
          Your characters
        </h2>
        <Button variant="primary" onClick={create} disabled={creating}>
          {creating ? "Creating…" : "+ New character"}
        </Button>
      </div>
      {characters.length === 0 ? (
        <div className="rounded-xl border border-dashed border-ink-600 p-10 text-center text-brand-stone/50">
          No characters yet. Create one and roll your legend.
        </div>
      ) : (
        <ul className="grid gap-3 sm:grid-cols-2">
          {characters.map((c) => (
            <li
              key={c.id}
              className="rounded-xl border border-ink-600/80 bg-ink-700/60 p-4 shadow-card transition-colors hover:border-brand-gold/70"
            >
              <Link to={`/characters/${c.id}`} className="block">
                <div className="flex items-center justify-between">
                  <div className="font-heading font-semibold text-brand-stone">
                    {c.name}
                  </div>
                  {isGenerated(c) && <Badge kind="ai" />}
                </div>
                <div className="mt-2 flex flex-wrap gap-1">
                  {(c.sheet.char_class?.value as string) && (
                    <Badge kind="neutral">
                      {c.sheet.char_class.value as string}
                    </Badge>
                  )}
                  {(c.sheet.race?.value as string) && (
                    <Badge kind="neutral">{c.sheet.race.value as string}</Badge>
                  )}
                  {(c.sheet.level?.value as number) && (
                    <Badge kind="neutral">
                      Level {c.sheet.level.value as number}
                    </Badge>
                  )}
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
