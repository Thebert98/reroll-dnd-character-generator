import type { ReactNode } from "react";

export type BadgeKind =
  | "new"
  | "popular"
  | "ai"
  | "homebrew"
  | "official"
  | "neutral";

// Style-book tag set: New, Popular, AI Generated, Homebrew, Official.
const KINDS: Record<BadgeKind, string> = {
  new: "bg-brand-sky/15 text-brand-sky border-brand-sky/30",
  popular: "bg-brand-gold/15 text-brand-gold border-brand-gold/30",
  ai: "bg-brand-arcane/15 text-brand-arcane border-brand-arcane/30",
  homebrew: "bg-brand-ember/15 text-brand-ember border-brand-ember/30",
  official: "bg-brand-green/15 text-brand-green border-brand-green/30",
  neutral: "bg-ink-600/60 text-brand-stone/80 border-ink-500",
};

const LABELS: Partial<Record<BadgeKind, string>> = {
  new: "New",
  popular: "Popular",
  ai: "AI Generated",
  homebrew: "Homebrew",
  official: "Official",
};

export function Badge({
  kind = "neutral",
  children,
  className = "",
}: {
  kind?: BadgeKind;
  children?: ReactNode;
  className?: string;
}) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide ${KINDS[kind]} ${className}`}
    >
      {children ?? LABELS[kind]}
    </span>
  );
}
