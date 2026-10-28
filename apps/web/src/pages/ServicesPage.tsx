import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router";

import { PriceMenu, PriceMenuSkeleton } from "../components/catalog/PriceMenu";
import { ErrorState } from "../components/ui/ErrorState";
import { PageHeader } from "../components/ui/PageHeader";
import { cx } from "../lib/cx";
import { formatPrice } from "../lib/format";
import { queries, useApi } from "../lib/api";
import { useLang, useT } from "../lib/lang";
import { servicesPath } from "../lib/paths";
import { useSeo } from "../lib/seo";

export default function ServicesPage() {
  const t = useT();
  const lang = useLang();
  const api = useApi();
  const { category: slug } = useParams();
  const categoriesQuery = useQuery(queries.categories(api, lang));
  const supplements = useQuery(queries.supplements(api, lang)).data;
  const categories = categoriesQuery.data;
  // No tab in the URL shows the first category (Hommes).
  const active =
    categories?.find((category) => category.slug === slug) ?? (slug ? undefined : categories?.[0]);
  const unknown = Boolean(categories && slug && !active);

  useSeo({
    title: active ? `${active.title} · ${t("services.title")}` : t("services.title"),
    description: active
      ? `${active.tagline} ${active.services.map((service) => service.name).join(", ")}.`
      : t("services.subtitle"),
    noindex: unknown,
  });

  return (
    <>
      <PageHeader title={t("services.title")}>{t("services.subtitle")}</PageHeader>
      <section className="container-site py-12 sm:py-16">
        {categories ? (
          <nav aria-label={t("services.tabs")} className="mb-10">
            <ul className="flex flex-wrap justify-center gap-2">
              {categories.map((category) => {
                const current = category.slug === active?.slug;
                return (
                  <li key={category.slug}>
                    <Link
                      to={servicesPath(lang, category.slug)}
                      aria-current={current ? "page" : undefined}
                      preventScrollReset
                      className={cx(
                        "inline-flex min-h-11 items-center rounded-full border px-5 text-[13px] font-semibold transition-colors",
                        current
                          ? "border-ink bg-ink text-page"
                          : "border-line hover:border-gold-ink",
                        category.accent === "rose" && !current && "hover:border-rose",
                      )}
                    >
                      {category.name}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>
        ) : null}

        {active ? (
          <div>
            <h2 className="sr-only">{active.title}</h2>
            {active.tagline || active.booking_note ? (
              <p className="mx-auto mb-4 max-w-[760px] text-center text-muted">
                {active.tagline}
                {active.booking_note ? (
                  <span className="ml-2 inline-block rounded-full border border-gold-ink px-3 py-0.5 text-xs font-semibold text-gold-ink">
                    {active.booking_note}
                  </span>
                ) : null}
              </p>
            ) : null}
            {active.services.length ? (
              <PriceMenu services={active.services} showDescriptions />
            ) : (
              <p className="text-center text-muted">{t("services.empty")}</p>
            )}
          </div>
        ) : unknown ? (
          <p role="alert" className="text-center text-muted">
            {t("services.notFound")}
          </p>
        ) : categoriesQuery.isError ? (
          <ErrorState
            error={categoriesQuery.error}
            onRetry={() => void categoriesQuery.refetch()}
          />
        ) : (
          <PriceMenuSkeleton rows={6} />
        )}

        {supplements?.length ? (
          <p className="mx-auto mt-8 max-w-[760px] text-sm text-muted">
            <strong className="font-semibold text-ink">{t("services.supplements")}</strong>{" "}
            {supplements
              .map((supplement) => `${supplement.name} ${formatPrice(supplement, lang, t)}`)
              .join(", ")}
            .
          </p>
        ) : null}
      </section>
    </>
  );
}
