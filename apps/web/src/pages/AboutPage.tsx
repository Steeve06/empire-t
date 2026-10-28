import { useQuery } from "@tanstack/react-query";

import { ButtonLink } from "../components/ui/Button";
import { ErrorState } from "../components/ui/ErrorState";
import { CheckIcon } from "../components/ui/Icons";
import { PageHeader } from "../components/ui/PageHeader";
import { Photo } from "../components/ui/Photo";
import { Reveal } from "../components/ui/Reveal";
import { SectionHeading } from "../components/ui/SectionHeading";
import { Skeleton } from "../components/ui/Skeleton";
import { queries, useApi } from "../lib/api";
import { useLang, useT } from "../lib/lang";
import { pathFor } from "../lib/paths";
import { useSeo } from "../lib/seo";

export default function AboutPage() {
  const t = useT();
  const lang = useLang();
  const api = useApi();
  const siteQuery = useQuery(queries.site(api, lang));
  const team = useQuery(queries.team(api, lang)).data;
  const site = siteQuery.data;
  const paragraphs = site?.story.split(/\n\s*\n/).filter(Boolean) ?? [];
  useSeo({
    title: t("about.title"),
    description: paragraphs[0]?.slice(0, 160),
    image: site?.about_image?.src,
  });

  return (
    <>
      <PageHeader title={t("about.title")}>{t("about.subtitle")}</PageHeader>

      <section className="container-site py-16 sm:py-20" aria-labelledby="story-title">
        <div className="grid items-center gap-10 md:grid-cols-2 md:gap-14">
          <Photo
            image={site?.about_image}
            alt={site ? `${site.business_name} ${site.business_subtitle}` : ""}
            placeholder={t("photo.about")}
            sizes="(min-width: 768px) 560px, 100vw"
            priority
            className="aspect-[4/5] w-full md:min-h-[420px]"
          />
          <div>
            <p className="eyebrow">{t("about.storyEyebrow")}</p>
            <h2 id="story-title" className="mt-3 mb-4 text-[clamp(32px,4vw,46px)]">
              {t("about.storyTitle")}
            </h2>
            {site ? (
              paragraphs.map((paragraph) => (
                <p key={paragraph.slice(0, 32)} className="mb-4 text-muted">
                  {paragraph}
                </p>
              ))
            ) : siteQuery.isError ? (
              <ErrorState error={siteQuery.error} onRetry={() => void siteQuery.refetch()} />
            ) : (
              <div aria-hidden="true" className="space-y-3">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-11/12" />
                <Skeleton className="h-4 w-4/5" />
              </div>
            )}
            <ButtonLink to={pathFor("book", lang)} className="mt-4">
              {t("about.book")}
            </ButtonLink>
          </div>
        </div>
      </section>

      {team?.length ? (
        <section className="bg-card py-16 sm:py-20" aria-labelledby="team-title">
          <div className="container-site">
            <SectionHeading id="team-title" title={t("about.teamTitle")} />
            <ul className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
              {team.map((member) => (
                <Reveal as="li" key={member.id} className="border border-line bg-page">
                  <Photo
                    image={member.photo}
                    alt={member.name}
                    placeholder={t("photo.team")}
                    sizes="(min-width: 1024px) 280px, (min-width: 640px) 50vw, 100vw"
                    className="aspect-[4/5] w-full"
                  />
                  <div className="p-5">
                    <h3 className="text-[26px]">{member.name}</h3>
                    <p className="text-sm font-semibold text-gold-ink">{member.role}</p>
                    {member.bio ? <p className="mt-2 text-sm text-muted">{member.bio}</p> : null}
                  </div>
                </Reveal>
              ))}
            </ul>
          </div>
        </section>
      ) : null}

      {site?.amenities.length ? (
        <section className="container-site py-16 sm:py-20" aria-labelledby="amenities-title">
          <SectionHeading
            id="amenities-title"
            eyebrow={t("about.amenitiesEyebrow")}
            title={t("about.amenitiesTitle")}
          />
          <ul className="mx-auto grid max-w-[760px] gap-x-8 sm:grid-cols-2">
            {site.amenities.map((amenity) => (
              <li key={amenity} className="flex items-center gap-3 border-b border-line py-4">
                <CheckIcon className="shrink-0 text-gold-ink" />
                {amenity}
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </>
  );
}
