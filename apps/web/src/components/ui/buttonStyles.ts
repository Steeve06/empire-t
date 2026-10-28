import { cx } from "../../lib/cx";

export type ButtonVariant = "gold" | "outline" | "outline-night" | "ink";

const base =
  "inline-flex min-h-11 items-center justify-center gap-2 px-6 py-3 text-[13px] font-bold tracking-[0.12em] uppercase transition-[background-color,color,border-color,transform] duration-200 select-none active:translate-y-px disabled:cursor-not-allowed disabled:opacity-60";

const variants: Record<ButtonVariant, string> = {
  gold: "bg-gold text-night hover:bg-[color-mix(in_oklab,var(--c-gold)_88%,white)]",
  outline: "border border-gold-ink text-gold-ink hover:bg-gold hover:text-night hover:border-gold",
  "outline-night": "border border-brand-gold text-brand-gold hover:bg-brand-gold hover:text-night",
  ink: "bg-ink text-page hover:bg-[color-mix(in_oklab,var(--c-ink)_85%,var(--c-gold))]",
};

export function buttonClass(variant: ButtonVariant = "gold", className?: string): string {
  return cx(base, variants[variant], className);
}
