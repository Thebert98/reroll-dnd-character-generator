import type { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger" | "magic";
type Size = "sm" | "md";

const BASE =
  "inline-flex items-center justify-center gap-2 rounded-lg font-heading font-semibold " +
  "transition-colors disabled:cursor-not-allowed disabled:opacity-50 focus:outline-none " +
  "focus-visible:ring-2 focus-visible:ring-brand-gold/60";

const VARIANTS: Record<Variant, string> = {
  // Dragon Red — primary action.
  primary: "bg-brand-red text-white hover:bg-[#d12222] shadow-ember",
  // Deep Slate outline — secondary.
  secondary:
    "border border-ink-500 bg-ink-700 text-brand-stone hover:border-brand-gold hover:text-brand-gold",
  // Text only.
  ghost: "text-brand-stone/70 hover:text-brand-gold",
  // Destructive.
  danger:
    "border border-brand-red/60 text-brand-red hover:bg-brand-red/10",
  // AI / re-roll — arcane→ember gradient for the "magic" moment.
  magic:
    "bg-gradient-to-r from-brand-arcane to-brand-ember text-white shadow-gold hover:brightness-110",
};

const SIZES: Record<Size, string> = {
  sm: "px-3 py-1.5 text-xs",
  md: "px-4 py-2 text-sm",
};

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
}

export function Button({
  variant = "primary",
  size = "md",
  className = "",
  ...props
}: Props) {
  return (
    <button
      className={`${BASE} ${VARIANTS[variant]} ${SIZES[size]} ${className}`}
      {...props}
    />
  );
}
