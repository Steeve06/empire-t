import { Link } from "react-router";

import type { ServiceCategory, SiteSettings } from "@empire-t/api-client";

import { useLang, useT } from "../../lib/lang";
import { pathFor, servicesPath, type PageId } from "../../lib/paths";

const SOCIAL_LABELS = { instagram: "Instagram", facebook: "Facebook", tiktok: "TikTok" } as const;

const linkClass = "inline-flex min-h-11 items-center hover:text-brand-gold sm:min-h-9";

export function Footer({
  site,
  categories,
}: {
  site: SiteSettings | undefined;
  categories: ServiceCategory[];
}) {
  const t = useT();
  const lang = useLang();
  const pages: PageId[] = ["about", "services", "gallery", "careers", "contact"];
  const navPages = pages.filter((page) => page !== "careers" || site?.recruitment_open);
  const socials = site
    ? (Object.keys(SOCIAL_LABELS) as (keyof typeof SOCIAL_LABELS)[]).filter(
        (key) => site.social[key],
      )
    : [];

  return (
    <footer className="on-night bg-night pt-14 pb-24 text-sm text-on-night-muted sm:pt-16">
      <div className="container-site grid gap-10 sm:grid-cols-2 lg:grid-cols-[1.4fr_1fr_1fr_1.2fr]">
        <div>
          <p className="font-display text-[22px] font-semibold tracking-[0.12em] text-on-night uppercase">
            {site?.business_name ?? "Empire T"}
          </p>
          <p className="mt-3 max-w-[320px]">{t("footer.blurb")}</p>
        </div>

        <nav aria-label={t("a11y.footerNav")}>
          <h2 className="mb-3 text-xl text-on-night">{t("footer.navigation")}</h2>
          <ul>
            {navPages.map((page) => (
              <li key={page}>
                <Link to={pathFor(page, lang)} className={linkClass}>
                  {t(`nav.${page}`)}
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        <div>
          <h2 className="mb-3 text-xl text-on-night">{t("footer.services")}</h2>
          <ul>
            {categories.map((category) => (
              <li key={category.slug}>
                <Link to={servicesPath(lang, category.slug)} className={linkClass}>
                  {category.name}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h2 className="mb-3 text-xl text-on-night">{t("footer.contact")}</h2>
          {site ? (
            <ul>
              <li>
                <a href={site.whatsapp_url} className={linkClass}>
                  WhatsApp {site.whatsapp_display}
                </a>
              </li>
              <li>
                <a href={`mailto:${site.email}`} className={linkClass}>
                  {site.email}
                </a>
              </li>
              <li className="py-2">
                {site.address_line}, {site.city}
              </li>
              {socials.map((key) => (
                <li key={key}>
                  <a href={site.social[key]} rel="noopener" target="_blank" className={linkClass}>
                    {SOCIAL_LABELS[key]}
                    <span className="sr-only"> {t("a11y.newTab")}</span>
                  </a>
                </li>
              ))}
            </ul>
          ) : null}
        </div>
      </div>
      <p className="container-site mt-10 border-t border-night-line pt-5 text-center text-xs">
        © <span suppressHydrationWarning>{new Date().getFullYear()}</span>{" "}
        {site ? `${site.business_name} ${site.business_subtitle}` : "Empire T"}.{" "}
        {t("footer.rights")}
      </p>
    </footer>
  );
}
