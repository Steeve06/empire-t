import { useQuery } from "@tanstack/react-query";
import type { ReactNode } from "react";

import { ContactForm } from "../components/contact/ContactForm";
import { MapEmbed } from "../components/MapEmbed";
import { buttonClass } from "../components/ui/buttonStyles";
import { ErrorState } from "../components/ui/ErrorState";
import { ChatIcon, ClockIcon, MailIcon, MapPinIcon } from "../components/ui/Icons";
import { PageHeader } from "../components/ui/PageHeader";
import { Skeleton } from "../components/ui/Skeleton";
import { queries, useApi } from "../lib/api";
import { formatTime } from "../lib/format";
import { useLang, useT } from "../lib/lang";
import { useSeo } from "../lib/seo";

/** One label/value pair; only <dt> and <dd> sit inside the wrapper, as HTML requires. */
function InfoRow({
  icon,
  label,
  children,
}: {
  icon: ReactNode;
  label: string;
  children: ReactNode;
}) {
  return (
    <div className="relative border-b border-line py-4 pl-10">
      <dt className="text-xs font-semibold tracking-[0.1em] text-muted uppercase">
        <span aria-hidden="true" className="absolute top-4 left-0 text-gold-ink">
          {icon}
        </span>
        {label}
      </dt>
      <dd className="mt-1">{children}</dd>
    </div>
  );
}

export default function ContactPage() {
  const t = useT();
  const lang = useLang();
  const api = useApi();
  const siteQuery = useQuery(queries.site(api, lang));
  const site = siteQuery.data;
  useSeo({
    title: t("contact.title"),
    description: site
      ? `${t("contact.subtitle")} ${site.address_line}, ${site.city}. WhatsApp ${site.whatsapp_display}.`
      : t("contact.subtitle"),
  });

  return (
    <>
      <PageHeader title={t("contact.title")}>{t("contact.subtitle")}</PageHeader>
      <section className="container-site grid items-start gap-12 py-12 sm:py-16 md:grid-cols-2 md:gap-14">
        <div>
          <h2 className="text-[clamp(30px,4vw,40px)]">{t("contact.visitTitle")}</h2>
          {site ? (
            <>
              <dl className="mt-4">
                <InfoRow icon={<MapPinIcon />} label={t("contact.address")}>
                  {site.address_line}, {site.city}
                </InfoRow>
                <InfoRow icon={<ClockIcon />} label={t("contact.hours")}>
                  {t("topBar.hours", {
                    days: site.opening_hours.days_label,
                    opens: formatTime(site.opening_hours.opens, lang),
                    closes: formatTime(site.opening_hours.closes, lang),
                  })}
                </InfoRow>
                <InfoRow icon={<ChatIcon />} label={t("contact.whatsapp")}>
                  <a
                    href={site.whatsapp_url}
                    className="font-semibold text-gold-ink hover:underline"
                  >
                    {site.whatsapp_display}
                  </a>
                </InfoRow>
                <InfoRow icon={<MailIcon />} label={t("contact.email")}>
                  <a
                    href={`mailto:${site.email}`}
                    className="font-semibold text-gold-ink hover:underline"
                  >
                    {site.email}
                  </a>
                </InfoRow>
              </dl>
              <a href={site.whatsapp_url} className={buttonClass("gold", "mt-6")}>
                <ChatIcon />
                {t("contact.writeWhatsapp")}
              </a>
              <MapEmbed site={site} className="mt-8 min-h-[300px]" />
            </>
          ) : siteQuery.isError ? (
            <ErrorState
              error={siteQuery.error}
              onRetry={() => void siteQuery.refetch()}
              className="mt-6"
            />
          ) : (
            <div aria-hidden="true" className="mt-6 space-y-4">
              {[1, 2, 3, 4].map((row) => (
                <Skeleton key={row} className="h-12 w-full" />
              ))}
            </div>
          )}
        </div>
        <div className="border border-line bg-card p-5 sm:p-7">
          <ContactForm />
        </div>
      </section>
    </>
  );
}
