import { useInfiniteQuery } from "@tanstack/react-query";
import { useState } from "react";
import { useSearchParams } from "react-router";

import type { GalleryCategory } from "@empire-t/api-client";

import { GalleryGrid, GallerySkeleton } from "../components/gallery/GalleryGrid";
import { Lightbox } from "../components/gallery/Lightbox";
import { Button } from "../components/ui/Button";
import { ErrorState } from "../components/ui/ErrorState";
import { PageHeader } from "../components/ui/PageHeader";
import { queries, useApi } from "../lib/api";
import { cx } from "../lib/cx";
import { useLang, useT } from "../lib/lang";
import { useSeo } from "../lib/seo";

const GALLERY_CATEGORIES = [
  "cuts",
  "hairstyles",
  "beauty",
  "salon",
] as const satisfies readonly GalleryCategory[];

const isCategory = (value: string | null): value is GalleryCategory =>
  GALLERY_CATEGORIES.some((category) => category === value);

export default function GalleryPage() {
  const t = useT();
  const lang = useLang();
  const api = useApi();
  const [params, setParams] = useSearchParams();
  const raw = params.get("category");
  const category = isCategory(raw) ? raw : undefined;
  const gallery = useInfiniteQuery(queries.galleryPages(api, lang, category));
  const [openIndex, setOpenIndex] = useState<number | null>(null);
  const images = gallery.data?.pages.flatMap((page) => page.results) ?? [];
  useSeo({
    title: t("gallery.title"),
    description: t("gallery.subtitle"),
    image: images[0]?.image?.src,
  });

  const filters: (GalleryCategory | undefined)[] = [undefined, ...GALLERY_CATEGORIES];

  return (
    <>
      <PageHeader title={t("gallery.title")}>{t("gallery.subtitle")}</PageHeader>
      <section className="container-site py-12 sm:py-16">
        <div
          role="group"
          aria-label={t("gallery.filters")}
          className="mb-10 flex flex-wrap justify-center gap-2"
        >
          {filters.map((value) => {
            const current = value === category;
            return (
              <button
                key={value ?? "all"}
                type="button"
                aria-pressed={current}
                onClick={() => {
                  setOpenIndex(null);
                  setParams(value ? { category: value } : {}, {
                    replace: true,
                    preventScrollReset: true,
                  });
                }}
                className={cx(
                  "inline-flex min-h-11 items-center rounded-full border px-5 text-[13px] font-semibold transition-colors",
                  current ? "border-ink bg-ink text-page" : "border-line hover:border-gold-ink",
                )}
              >
                {value ? t(`gallery.categories.${value}`) : t("gallery.all")}
              </button>
            );
          })}
        </div>

        {gallery.isPending ? (
          <GallerySkeleton />
        ) : gallery.isError && !images.length ? (
          <ErrorState error={gallery.error} onRetry={() => void gallery.refetch()} />
        ) : images.length ? (
          <>
            <GalleryGrid images={images} onOpen={setOpenIndex} />
            {gallery.hasNextPage ? (
              <p className="mt-8 text-center">
                <Button
                  variant="outline"
                  disabled={gallery.isFetchingNextPage}
                  onClick={() => void gallery.fetchNextPage()}
                >
                  {gallery.isFetchingNextPage ? t("status.loading") : t("gallery.loadMore")}
                </Button>
              </p>
            ) : null}
          </>
        ) : (
          <p className="mx-auto max-w-[520px] text-center text-muted">{t("gallery.empty")}</p>
        )}
      </section>

      {openIndex !== null ? (
        <Lightbox
          images={images}
          index={openIndex}
          onIndexChange={setOpenIndex}
          onClose={() => {
            setOpenIndex(null);
          }}
        />
      ) : null}
    </>
  );
}
