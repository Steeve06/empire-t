import { Link } from "react-router";

import type { Service, ServiceInCategory } from "@empire-t/api-client";

import { cx } from "../../lib/cx";
import { formatDuration, formatPrice } from "../../lib/format";
import { useLang, useT } from "../../lib/lang";
import { bookingPath } from "../../lib/paths";
import { Skeleton } from "../ui/Skeleton";

type MenuService = Service | ServiceInCategory;

/** Classic price list: name and duration, dotted leader, gold serif price, "Réserver" link. */
export function PriceMenu({
  services,
  showDescriptions = false,
  className,
}: {
  services: MenuService[];
  showDescriptions?: boolean;
  className?: string;
}) {
  const t = useT();
  const lang = useLang();
  return (
    <ul className={cx("mx-auto max-w-[760px]", className)}>
      {services.map((service) => (
        <li
          key={service.slug}
          className="grid grid-cols-[1fr_auto] items-baseline gap-x-3 border-b border-line py-4 sm:flex sm:gap-3"
        >
          <div className="min-w-0">
            <p className="font-bold">{service.name}</p>
            <p className="text-[13px] text-muted">
              {formatDuration(service.duration_min, service.duration_max, t)}
              {showDescriptions && service.description ? ` · ${service.description}` : null}
            </p>
          </div>
          <span
            aria-hidden="true"
            className="hidden flex-1 -translate-y-1 border-b border-dotted border-muted/60 sm:block"
          />
          <div className="flex flex-col items-end gap-1 sm:flex-row sm:items-baseline sm:gap-3">
            <span className="font-display text-[22px] font-bold whitespace-nowrap text-gold-ink">
              {formatPrice(service, lang, t)}
            </span>
            <Link
              to={bookingPath(lang, { service: service.slug })}
              aria-label={t("services.bookService", { name: service.name })}
              className="inline-flex min-h-11 items-center text-xs font-bold tracking-[0.1em] text-gold-ink uppercase hover:underline sm:min-h-0"
            >
              {t("services.book")}
            </Link>
          </div>
        </li>
      ))}
    </ul>
  );
}

export function PriceMenuSkeleton({ rows = 4 }: { rows?: number }) {
  return (
    <ul className="mx-auto max-w-[760px]" aria-hidden="true">
      {Array.from({ length: rows }, (_, index) => (
        <li key={index} className="flex items-center gap-4 border-b border-line py-5">
          <Skeleton className="h-5 w-1/2" />
          <span className="flex-1" />
          <Skeleton className="h-6 w-20" />
        </li>
      ))}
    </ul>
  );
}
