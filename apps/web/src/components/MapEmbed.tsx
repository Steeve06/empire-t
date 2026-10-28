import { useState } from "react";

import type { SiteSettings } from "@empire-t/api-client";

import { cx } from "../lib/cx";
import { mapsLink } from "../lib/maps";
import { useT } from "../lib/lang";
import { Button } from "./ui/Button";
import { MapPinIcon } from "./ui/Icons";

/**
 * Google Maps behind a click-to-load facade. The embed weighs over 1 MB of
 * script; loading it only on request keeps the page fast on mobile data.
 */
export function MapEmbed({ site, className }: { site: SiteSettings; className?: string }) {
  const t = useT();
  const [loaded, setLoaded] = useState(false);
  const src = `https://maps.google.com/maps?q=${site.latitude},${site.longitude}&z=16&output=embed`;

  return (
    <div className={cx("relative min-h-[300px] overflow-hidden border border-line", className)}>
      {loaded ? (
        <iframe
          title={t("map.title")}
          src={src}
          className="absolute inset-0 size-full border-0"
          loading="lazy"
          referrerPolicy="no-referrer-when-downgrade"
          allowFullScreen
        />
      ) : (
        <div className="photo-placeholder is-light absolute inset-0 flex-col items-center justify-center gap-4 p-6 text-center tracking-normal normal-case">
          <MapPinIcon width={36} height={36} className="text-gold-ink" />
          <p className="max-w-[280px] text-sm text-ink">
            {site.address_line}, {site.city}
          </p>
          <Button
            variant="outline"
            onClick={() => {
              setLoaded(true);
            }}
          >
            {t("map.load")}
          </Button>
          <p className="max-w-[300px] text-xs text-muted">{t("map.loadHint")}</p>
        </div>
      )}
      <a
        href={mapsLink(site)}
        target="_blank"
        rel="noopener"
        className="absolute right-2 bottom-2 z-10 inline-flex min-h-11 items-center bg-card/95 px-3 text-xs font-bold tracking-[0.08em] text-gold-ink uppercase shadow-sm"
      >
        {t("map.open")}
        <span className="sr-only"> {t("a11y.newTab")}</span>
      </a>
    </div>
  );
}
