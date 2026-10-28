import { Link } from "react-router";

import type {
  GalleryImage,
  ServiceCategory,
  SiteSettings,
  Testimonial,
} from "@empire-t/api-client";

import { cx } from "../../lib/cx";
import {
  formatAmount,
  formatDate,
  formatDuration,
  formatPrice,
  formatTime,
} from "../../lib/format";
import { useLang, useT } from "../../lib/lang";
import { bookingPath, pathFor, servicesPath } from "../../lib/paths";
import { PriceMenu, PriceMenuSkeleton } from "../catalog/PriceMenu";
import { GalleryGrid, GallerySkeleton } from "../gallery/GalleryGrid";
import { MapEmbed } from "../MapEmbed";
import { ButtonLink } from "../ui/Button";
import { StarIcon } from "../ui/Icons";
import { Photo } from "../ui/Photo";
import { Reveal } from "../ui/Reveal";
import { SectionHeading } from "../ui/SectionHeading";
import { Skeleton } from "../ui/Skeleton";

export function Hero({ site }: { site: SiteSettings | undefined }) {
  const t = useT();
  const lang = useLang();
  return (
    <section className="on-night bg-night text-on-night">
      <div className="container-site grid items-center gap-10 pt-12 pb-24 md:grid-cols-[1.05fr_1fr] md:pt-[70px] md:pb-[110px]">
        <div>
          <p className="eyebrow">{t("home.eyebrow")}</p>
          <h1 className="mt-4 mb-5 text-[clamp(44px,6.5vw,84px)]">
            {site?.tagline ?? t("meta.siteName")}
          </h1>
          <p className="max-w-[520px] text-on-night-muted">{t("home.intro")}</p>
          <div className="mt-8 flex flex-wrap gap-3">
            <ButtonLink to={pathFor("book", lang)}>{t("home.ctaBook")}</ButtonLink>
            <ButtonLink to={servicesPath(lang)} variant="outline-night">
              {t("home.ctaServices")}
            </ButtonLink>
          </div>
        </div>
        <Photo
          image={site?.hero_image}
          alt={site ? `${site.business_name} ${site.business_subtitle}` : ""}
          placeholder={t("photo.hero")}
          sizes="(min-width: 768px) 540px, 100vw"
          priority
          className="aspect-[4/5] w-full border border-night-line md:aspect-auto md:min-h-[460px]"
        />
      </div>
    </section>
  );
}

const VALUE_KEYS = ["quality", "cleanliness", "speed", "style"] as const;

export function ValuesStrip() {
  const t = useT();
  return (
    <section
      className="container-site pt-16 sm:pt-20"
      aria-label={VALUE_KEYS.map((key) => t(`home.values.${key}.title`)).join(", ")}
    >
      <ul className="grid grid-cols-2 border-y border-line lg:grid-cols-4">
        {VALUE_KEYS.map((key, index) => (
          <li
            key={key}
            className={cx(
              "border-line px-3 py-6 text-center sm:px-6 sm:py-7",
              index % 2 === 0 && "border-r",
              index < 2 && "border-b lg:border-b-0",
              index === 1 && "lg:border-r",
            )}
          >
            <p className="font-display text-[22px] font-semibold">
              {t(`home.values.${key}.title`)}
            </p>
            <p className="mt-1 text-sm text-muted">{t(`home.values.${key}.text`)}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}

export function Universes({ categories }: { categories: ServiceCategory[] | undefined }) {
  const t = useT();
  const lang = useLang();
  const shown = categories?.filter((category) => category.show_on_home);
  return (
    <section className="container-site py-16 sm:py-20" aria-labelledby="universes-title">
      <SectionHeading
        id="universes-title"
        eyebrow={t("home.universes.eyebrow")}
        title={t("home.universes.title")}
      />
      <ul className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {shown
          ? shown.map((category) => {
              const rose = category.accent === "rose";
              return (
                <Reveal
                  as="li"
                  key={category.slug}
                  className={cx(
                    "group relative flex flex-col border bg-card transition-[transform,box-shadow] duration-300 hover:-translate-y-1 hover:shadow-[0_14px_30px_rgb(0_0_0/0.1)]",
                    rose ? "border-rose/60" : "border-line",
                  )}
                >
                  <Photo
                    image={category.image}
                    alt={category.title}
                    placeholder={t("photo.category", { name: category.name })}
                    sizes="(min-width: 1024px) 280px, (min-width: 640px) 50vw, 100vw"
                    tone={rose ? "rose" : "dark"}
                    className="aspect-[4/3] w-full"
                  />
                  <div className="flex flex-1 flex-col p-5">
                    <h3 className="text-[28px]">{category.title}</h3>
                    <p className="mt-1.5 mb-4 flex-1 text-sm text-muted">
                      {category.tagline}
                      {category.starting_price != null ? (
                        <>
                          {" "}
                          {t("home.universes.startingAt", {
                            price: t("price.currency", {
                              amount: formatAmount(category.starting_price, lang),
                            }),
                          })}
                          .
                        </>
                      ) : null}
                    </p>
                    <Link
                      to={servicesPath(lang, category.slug)}
                      className={cx(
                        "inline-flex min-h-11 items-center text-[13px] font-bold tracking-[0.1em] uppercase after:absolute after:inset-0 hover:underline",
                        rose ? "text-rose-ink" : "text-gold-ink",
                      )}
                    >
                      {t("home.universes.seePrices")}
                      <span className="sr-only">: {category.title}</span>
                    </Link>
                  </div>
                </Reveal>
              );
            })
          : Array.from({ length: 4 }, (_, index) => (
              <li key={index} aria-hidden="true" className="border border-line bg-card">
                <Skeleton className="aspect-[4/3] w-full" />
                <div className="space-y-3 p-5">
                  <Skeleton className="h-7 w-2/3" />
                  <Skeleton className="h-4 w-full" />
                </div>
              </li>
            ))}
      </ul>
    </section>
  );
}

export function Signature({ site }: { site: SiteSettings | undefined }) {
  const t = useT();
  const lang = useLang();
  const service = site?.signature_service;
  if (!site || !service) return null;
  return (
    <section
      className="on-night bg-night py-16 text-on-night sm:py-20"
      aria-labelledby="signature-title"
    >
      <div className="container-site grid items-center gap-10 md:grid-cols-2 md:gap-14">
        <Photo
          image={site.signature_image}
          alt={service.name}
          placeholder={t("photo.signature")}
          sizes="(min-width: 768px) 560px, 100vw"
          className="aspect-[4/3] w-full border border-night-line md:min-h-[420px]"
        />
        <Reveal>
          <p className="eyebrow">{t("home.signature.eyebrow")}</p>
          <h2 id="signature-title" className="mt-3 mb-4 text-[clamp(32px,4vw,46px)]">
            {service.name}
          </h2>
          <p className="text-on-night-muted">{service.description}</p>
          <p className="mt-2 text-sm text-on-night-muted">
            {formatDuration(service.duration_min, service.duration_max, t)}
          </p>
          <p className="my-5 font-display text-[40px] font-bold text-brand-gold">
            {formatPrice(service, lang, t)}
          </p>
          <ButtonLink to={bookingPath(lang, { service: service.slug })}>
            {t("home.signature.book")}
          </ButtonLink>
        </Reveal>
      </div>
    </section>
  );
}

export function PopularPrices({ categories }: { categories: ServiceCategory[] | undefined }) {
  const t = useT();
  const lang = useLang();
  const popular = categories?.flatMap((category) =>
    category.services.filter((service) => service.is_popular),
  );
  if (popular?.length === 0) return null;
  return (
    <section className="container-site py-16 sm:py-20" aria-labelledby="popular-title">
      <SectionHeading
        id="popular-title"
        eyebrow={t("home.popular.eyebrow")}
        title={t("home.popular.title")}
      />
      {popular ? <PriceMenu services={popular} /> : <PriceMenuSkeleton />}
      <p className="mt-8 text-center">
        <ButtonLink to={servicesPath(lang)} variant="ink">
          {t("home.popular.all")}
        </ButtonLink>
      </p>
    </section>
  );
}

export function GalleryPreview({ images }: { images: GalleryImage[] | undefined }) {
  const t = useT();
  const lang = useLang();
  if (images?.length === 0) return null;
  return (
    <section className="bg-card py-16 sm:py-20" aria-labelledby="gallery-title">
      <div className="container-site">
        <SectionHeading
          id="gallery-title"
          eyebrow={t("home.gallery.eyebrow")}
          title={t("home.gallery.title")}
        />
        {images ? <GalleryGrid images={images.slice(0, 6)} /> : <GallerySkeleton />}
        <p className="mt-8 text-center">
          <ButtonLink to={pathFor("gallery", lang)} variant="outline">
            {t("home.gallery.all")}
          </ButtonLink>
        </p>
      </div>
    </section>
  );
}

export function Testimonials({ items }: { items: Testimonial[] | undefined }) {
  const t = useT();
  const [open, close] = useLang() === "fr" ? ["« ", " »"] : ["“", "”"];
  if (!items?.length) return null;
  return (
    <section className="container-site py-16 sm:py-20" aria-labelledby="testimonials-title">
      <SectionHeading
        id="testimonials-title"
        eyebrow={t("home.testimonials.eyebrow")}
        title={t("home.testimonials.title")}
      />
      <ul className="grid gap-5 md:grid-cols-3">
        {items.slice(0, 3).map((item) => (
          <Reveal as="li" key={item.id} className="border border-line bg-card p-7">
            <figure>
              {item.rating ? (
                <p
                  className="mb-3 flex gap-0.5 text-gold"
                  role="img"
                  aria-label={t("home.testimonials.rating", { count: item.rating })}
                >
                  {Array.from({ length: item.rating }, (_, index) => (
                    <StarIcon key={index} width={16} height={16} />
                  ))}
                </p>
              ) : null}
              <blockquote className="font-display text-[21px] leading-snug font-medium italic">
                <p>
                  {open}
                  {item.quote}
                  {close}
                </p>
              </blockquote>
              <figcaption className="mt-4 text-sm text-muted">
                {item.author_name}
                {item.author_location ? `, ${item.author_location}` : null}
              </figcaption>
            </figure>
          </Reveal>
        ))}
      </ul>
    </section>
  );
}

export function CareersBanner({ site }: { site: SiteSettings | undefined }) {
  const t = useT();
  const lang = useLang();
  if (!site?.recruitment_open || !site.recruitment_deadline) return null;
  return (
    <section className="on-night bg-gradient-to-br from-night to-[#2a2116] px-4 py-16 text-center text-on-night sm:py-[70px]">
      <h2 className="mb-3 text-[clamp(32px,4vw,46px)]">{t("home.careers.title")}</h2>
      <p className="mx-auto max-w-[560px] text-on-night-muted">
        {t("home.careers.text", { date: formatDate(site.recruitment_deadline, lang) })}
      </p>
      <ButtonLink to={pathFor("careers", lang)} className="mt-7">
        {t("home.careers.cta")}
      </ButtonLink>
    </section>
  );
}

export function FindUs({ site }: { site: SiteSettings | undefined }) {
  const t = useT();
  const lang = useLang();
  if (!site) return null;
  return (
    <section className="container-site py-16 sm:py-20" aria-labelledby="find-title">
      <div className="grid items-center gap-10 md:grid-cols-2 md:gap-14">
        <div>
          <p className="eyebrow">{t("home.find.eyebrow")}</p>
          <h2 id="find-title" className="mt-3 mb-4 text-[clamp(32px,4vw,46px)]">
            {site.address_line}
          </h2>
          <p className="text-muted">
            {site.city}.{" "}
            {t("home.find.walkIn", {
              days: site.opening_hours.days_label,
              opens: formatTime(site.opening_hours.opens, lang),
              closes: formatTime(site.opening_hours.closes, lang),
            })}
          </p>
          {site.amenities.length ? (
            <p className="mt-3 text-muted">{site.amenities.join(", ")}.</p>
          ) : null}
          <ButtonLink to={pathFor("contact", lang)} className="mt-7">
            {t("home.find.cta")}
          </ButtonLink>
        </div>
        <MapEmbed site={site} className="min-h-[340px]" />
      </div>
    </section>
  );
}
