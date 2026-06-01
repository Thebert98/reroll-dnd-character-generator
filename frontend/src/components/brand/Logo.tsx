import { Link } from "react-router-dom";
import { D20 } from "./D20";

type Size = "sm" | "md" | "lg";

const TEXT: Record<Size, string> = {
  sm: "text-xl",
  md: "text-3xl",
  lg: "text-5xl",
};
const DIE: Record<Size, number> = { sm: 22, md: 34, lg: 56 };
const SUB: Record<Size, string> = {
  sm: "text-[9px]",
  md: "text-xs",
  lg: "text-base",
};

/** The Re:Roll wordmark lockup: "Re" · d20 · "Roll" in tavern-serif amber, with an
 *  optional "Character Builder" subtitle. Rendered in pure SVG/text so it stays
 *  crisp at any size (the photographic dragon logo is an optional drop-in). */
export function Logo({
  size = "md",
  showSubtitle = true,
  to,
  className = "",
}: {
  size?: Size;
  showSubtitle?: boolean;
  to?: string;
  className?: string;
}) {
  const inner = (
    <span className={`inline-flex flex-col items-center ${className}`}>
      <span
        className={`flex items-center gap-1 font-display font-bold leading-none tracking-wide ${TEXT[size]}`}
      >
        <span className="bg-gradient-to-b from-tavern-hearth to-tavern-amber bg-clip-text text-transparent">
          Re
        </span>
        <D20 size={DIE[size]} className="drop-shadow-[0_0_6px_rgba(216,186,31,0.4)]" />
        <span className="bg-gradient-to-b from-tavern-hearth to-tavern-amber bg-clip-text text-transparent">
          Roll
        </span>
      </span>
      {showSubtitle && (
        <span
          className={`mt-1 font-heading font-semibold uppercase tracking-[0.4em] text-brand-stone/70 ${SUB[size]}`}
        >
          Character Builder
        </span>
      )}
    </span>
  );

  if (to) {
    return (
      <Link to={to} aria-label="Re:Roll Character Builder — home">
        {inner}
      </Link>
    );
  }
  return inner;
}
