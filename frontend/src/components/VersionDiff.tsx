import { useEffect, useState } from "react";
import { api } from "../lib/api";
import type { CharacterVersion } from "../types";
import { SHEET_FIELDS, FIELD_LABELS } from "../types";

function format(value: unknown): string {
  if (value == null || value === "") return "—";
  if (Array.isArray(value)) return value.length ? value.join(", ") : "—";
  if (typeof value === "object")
    return Object.entries(value as Record<string, unknown>)
      .map(([k, v]) => `${k.toUpperCase()} ${v}`)
      .join(" ");
  return String(value);
}

/** Field-by-field before/after diff between two versions. */
export function VersionDiff({ characterId }: { characterId: string }) {
  const [versions, setVersions] = useState<CharacterVersion[]>([]);
  const [fromN, setFromN] = useState<number | null>(null);
  const [toN, setToN] = useState<number | null>(null);

  useEffect(() => {
    api.listVersions(characterId).then((vs) => {
      setVersions(vs);
      if (vs.length >= 2) {
        setToN(vs[0].version_number);
        setFromN(vs[1].version_number);
      }
    });
  }, [characterId]);

  if (versions.length < 2)
    return (
      <p className="text-sm text-brand-stone/60">
        Need at least two versions to compare.
      </p>
    );

  const from = versions.find((v) => v.version_number === fromN);
  const to = versions.find((v) => v.version_number === toN);

  return (
    <div>
      <div className="mb-4 flex items-center gap-2 text-sm">
        <Select label="From" value={fromN} versions={versions} onChange={setFromN} />
        <span className="text-brand-stone/50">→</span>
        <Select label="To" value={toN} versions={versions} onChange={setToN} />
      </div>
      {from && to && (
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-brand-stone/50">
              <th className="py-1">Field</th>
              <th className="py-1">v{from.version_number}</th>
              <th className="py-1">v{to.version_number}</th>
            </tr>
          </thead>
          <tbody>
            {SHEET_FIELDS.map((f) => {
              const a = format(from.sheet[f]?.value);
              const b = format(to.sheet[f]?.value);
              const changed = a !== b;
              return (
                <tr
                  key={f}
                  className={changed ? "bg-brand-gold/5" : "text-brand-stone/50"}
                >
                  <td className="py-1 font-medium">{FIELD_LABELS[f]}</td>
                  <td className="py-1">{a}</td>
                  <td className={`py-1 ${changed ? "text-brand-gold" : ""}`}>{b}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}

function Select({
  label,
  value,
  versions,
  onChange,
}: {
  label: string;
  value: number | null;
  versions: CharacterVersion[];
  onChange: (n: number) => void;
}) {
  return (
    <label className="flex items-center gap-1">
      <span className="text-brand-stone/60">{label}</span>
      <select
        className="rounded bg-ink-900 px-2 py-1"
        value={value ?? ""}
        onChange={(e) => onChange(Number(e.target.value))}
      >
        {versions.map((v) => (
          <option key={v.id} value={v.version_number}>
            v{v.version_number}
          </option>
        ))}
      </select>
    </label>
  );
}
