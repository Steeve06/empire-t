import { useQuery } from "@tanstack/react-query";

import { ApplicationForm } from "../components/careers/ApplicationForm";
import { ButtonLink } from "../components/ui/Button";
import { ErrorState } from "../components/ui/ErrorState";
import { CheckIcon } from "../components/ui/Icons";
import { PageHeader } from "../components/ui/PageHeader";
import { Reveal } from "../components/ui/Reveal";
import { SectionHeading } from "../components/ui/SectionHeading";
import { Skeleton } from "../components/ui/Skeleton";
import { queries, useApi } from "../lib/api";
import { formatDate } from "../lib/format";
import { useLang, useT } from "../lib/lang";
import { pathFor } from "../lib/paths";
import { useSeo } from "../lib/seo";

export default function CareersPage() {
  const t = useT();
  const lang = useLang();
  const api = useApi();
  const siteQuery = useQuery(queries.site(api, lang));
  const openingsQuery = useQuery(queries.openings(api, lang));
  const site = siteQuery.data;
  const openings = openingsQuery.data;
  const deadline = site?.recruitment_deadline ? formatDate(site.recruitment_deadline, lang) : null;
  // The API returns no openings once the deadline has passed: the page then says so and leaves the index.
  const closed = Boolean(site && openings && (!site.recruitment_open || openings.length === 0));
  const failed = [siteQuery, openingsQuery].find((query) => query.isError && !query.data);

  useSeo({
    title: t("careers.title"),
    description: deadline ? t("home.careers.text", { date: deadline }) : t("careers.closed.text"),
    noindex: closed,
  });

  if (closed) {
    return (
      <>
        <PageHeader title={t("careers.closed.title")} />
        <section className="container-site max-w-[620px] py-16 text-center">
          <p className="text-muted">{t("careers.closed.text")}</p>
          <ButtonLink to={pathFor("home", lang)} variant="outline" className="mt-8">
            {t("notFound.home")}
          </ButtonLink>
        </section>
      </>
    );
  }

  return (
    <>
      <PageHeader title={t("careers.title")}>
        {deadline ? t("careers.subtitle", { date: deadline }) : null}
      </PageHeader>

      <section className="container-site py-12 sm:py-16" aria-labelledby="openings-title">
        <SectionHeading id="openings-title" title={t("careers.openingsTitle")} />
        {failed ? (
          <ErrorState
            error={failed.error}
            onRetry={() => {
              void siteQuery.refetch();
              void openingsQuery.refetch();
            }}
          />
        ) : (
          <ul className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {openings
              ? openings.map((opening) => (
                  <Reveal
                    as="li"
                    key={opening.slug}
                    className="flex flex-col border border-line bg-card p-6"
                  >
                    <p className="eyebrow">
                      {t("careers.positions", { count: opening.positions_count })}
                    </p>
                    <h3 className="mt-2 text-[26px]">{opening.title}</h3>
                    <p className="mt-2 text-sm text-muted">{opening.requirements}</p>
                    {opening.description ? (
                      <p className="mt-2 text-sm text-muted">{opening.description}</p>
                    ) : null}
                    {opening.deadline && opening.deadline !== site?.recruitment_deadline ? (
                      <p className="mt-auto pt-4 text-xs font-semibold text-gold-ink">
                        {t("careers.deadline", { date: formatDate(opening.deadline, lang) })}
                      </p>
                    ) : null}
                  </Reveal>
                ))
              : Array.from({ length: 4 }, (_, index) => (
                  <li
                    key={index}
                    aria-hidden="true"
                    className="space-y-3 border border-line bg-card p-6"
                  >
                    <Skeleton className="h-3 w-1/3" />
                    <Skeleton className="h-7 w-3/4" />
                    <Skeleton className="h-4 w-full" />
                  </li>
                ))}
          </ul>
        )}
      </section>

      <section className="bg-card py-12 sm:py-16" aria-labelledby="documents-title">
        <div className="container-site grid items-start gap-10 md:grid-cols-[1fr_1.2fr] md:gap-14">
          <div>
            <h2 id="documents-title" className="text-[clamp(32px,4vw,46px)]">
              {t("careers.documentsTitle")}
            </h2>
            <p className="mt-3 text-muted">{t("careers.documentsIntro")}</p>
            <ul className="mt-4">
              {site?.application_documents.map((document) => (
                <li key={document} className="flex items-start gap-3 border-b border-line py-3">
                  <CheckIcon className="mt-1 shrink-0 text-gold-ink" />
                  {document}
                </li>
              ))}
            </ul>
            {deadline ? (
              <p className="mt-5 font-semibold">{t("careers.subtitle", { date: deadline })}</p>
            ) : null}
          </div>
          <div className="border border-line bg-page p-5 sm:p-7">
            {openings?.length ? (
              <ApplicationForm openings={openings} />
            ) : (
              <Skeleton className="h-96 w-full" />
            )}
          </div>
        </div>
      </section>
    </>
  );
}
