import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import type { Character } from "../types";

export function CharacterList() {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);
  const nav = useNavigate();

  async function refresh() {
    setCharacters(await api.listCharacters());
    setLoading(false);
  }
  useEffect(() => {
    refresh();
  }, []);

  async function create() {
    const c = await api.createCharacter("Untitled");
    nav(`/characters/${c.id}`);
  }

  if (loading) return <div>Loading characters…</div>;

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-2xl font-bold">Your characters</h2>
        <button
          className="rounded bg-arcane px-4 py-2 font-medium"
          onClick={create}
        >
          + New character
        </button>
      </div>
      {characters.length === 0 ? (
        <p className="text-slate-400">
          No characters yet. Create one to get started.
        </p>
      ) : (
        <ul className="grid gap-3 sm:grid-cols-2">
          {characters.map((c) => (
            <li
              key={c.id}
              className="rounded-lg border border-slate-800 p-4 hover:border-arcane"
            >
              <Link to={`/characters/${c.id}`} className="block">
                <div className="font-semibold">{c.name}</div>
                <div className="text-xs text-slate-500">
                  {(c.sheet.char_class?.value as string) || "—"} ·{" "}
                  {(c.sheet.race?.value as string) || "—"}
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
