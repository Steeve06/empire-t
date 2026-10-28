import { Link, useLocation } from "react-router";

import { cx } from "../../lib/cx";
import { useLang, useT } from "../../lib/lang";
import { translatePath } from "../../lib/paths";

/** "FR | EN" pill. Links to the same page in the other language. */
export function LanguageToggle({ className }: { className?: string }) {
  const lang = useLang();
  const t = useT();
  const { pathname, search } = useLocation();
  const other = lang === "fr" ? "en" : "fr";
  return (
    <Link
      to={translatePath(pathname, search, other)}
      hrefLang={other}
      lang={other}
      aria-label={`${other.toUpperCase()} · ${t("a11y.languageSwitch")}`}
      className={cx(
        "inline-flex min-h-11 items-center gap-1.5 rounded-full border border-line px-3.5 text-xs font-semibold tracking-wide hover:border-gold",
        className,
      )}
    >
      <span className={lang === "fr" ? "text-ink" : "text-muted"}>FR</span>
      <span aria-hidden="true" className="text-line">
        |
      </span>
      <span className={lang === "en" ? "text-ink" : "text-muted"}>EN</span>
    </Link>
  );
}
