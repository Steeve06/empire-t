import { Link } from "react-router";

import { useLang } from "../../lib/lang";
import { pathFor } from "../../lib/paths";

/**
 * Typographic wordmark until the owner's logo arrives (assumption A17). Then put the
 * SVG in `public/logo.svg` and render it here as an <img> with width and height set,
 * keeping the business name as its alt text.
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
