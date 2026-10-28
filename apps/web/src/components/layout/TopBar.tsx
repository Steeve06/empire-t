import type { SiteSettings } from "@empire-t/api-client";

import { formatTime } from "../../lib/format";
import { useLang, useT } from "../../lib/lang";

export function TopBar({ site }: { site: SiteSettings | undefined }) {
  const t = useT();
  const lang = useLang();
  return (
    <div className="bg-night text-[13px] text-on-night-muted">
      <div className="container-site flex min-h-9 flex-wrap items-center justify-between gap-x-4 gap-y-1 py-2">
        {site ? (
          <>
            <p>
              {site.address_line.split(",")[0]}, {site.city}
              <span aria-hidden="true"> · </span>
              <span className="text-brand-gold">
                {t("topBar.hours", {
                  days: site.opening_hours.days_label,
                  opens: formatTime(site.opening_hours.opens, lang),
                  closes: formatTime(site.opening_hours.closes, lang),
                })}
              </span>
            </p>
            <p className="hidden sm:block">
              <a href={site.whatsapp_url} className="hover:text-on-night">
                {t("topBar.whatsapp")}{" "}
                <span className="text-brand-gold">{site.whatsapp_display}</span>
              </a>
              {site.accepts_mobile_money ? (
                <>
                  <span aria-hidden="true"> · </span>
                  {t("topBar.mobileMoney")}
                </>
              ) : null}
            </p>
          </>
        ) : null}
      </div>
    </div>
  );
}
