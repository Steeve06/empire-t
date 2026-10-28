import { Link } from "react-router";

import { useLang } from "../../lib/lang";
import { pathFor } from "../../lib/paths";

/**
 * Typographic wordmark. When the owner's logo file arrives, place it at
 * `public/logo.svg` and replace the two spans with an <img> (see the owner guide).
 */
export function Logo({ name, subtitle }: { name: string; subtitle: string }) {
  const lang = useLang();
  return (
    <Link
      to={pathFor("home", lang)}
      className="mr-auto flex min-h-11 shrink-0 flex-col justify-center leading-none whitespace-nowrap"
    >
      <span className="font-display text-[24px] font-bold tracking-[0.14em] uppercase sm:text-[28px]">
        {name}
      </span>
      <span className="mt-1 text-[9px] tracking-[0.3em] text-gold-ink uppercase sm:text-[10px] sm:tracking-[0.38em]">
        {subtitle}
      </span>
    </Link>
  );
}
