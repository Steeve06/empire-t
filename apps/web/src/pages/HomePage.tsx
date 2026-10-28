import { useQuery } from "@tanstack/react-query";

import {
  CareersBanner,
  FindUs,
  GalleryPreview,
  Hero,
  PopularPrices,
  Signature,
  Testimonials,
  Universes,
  ValuesStrip,
} from "../components/home/HomeSections";
import { QuickBookingBar } from "../components/home/QuickBookingBar";
import { ErrorState } from "../components/ui/ErrorState";
import { queries, useApi } from "../lib/api";
import { useLang, useT } from "../lib/lang";
import { useSeo } from "../lib/seo";

export default function HomePage() {
  const api = useApi();
  const lang = useLang();
  const siteQuery = useQuery(queries.site(api, lang));
  const categoriesQuery = useQuery(queries.categories(api, lang));
  const site = siteQuery.data;
  const categories = categoriesQuery.data;
  const failed = [siteQuery, categoriesQuery].find((query) => query.isError && !query.data);
  const gallery = useQuery(queries.featuredGallery(api, lang)).data;
  const testimonials = useQuery(queries.testimonials(api, lang)).data;
  const t = useT();
  useSeo({ title: t("meta.homeTitle"), image: site?.hero_image?.src });

  return (
    <>
      <Hero site={site} />
      <QuickBookingBar site={site} categories={categories ?? []} />
      {failed ? (
        <div className="container-site pt-12">
          <ErrorState
            error={failed.error}
            onRetry={() => {
              void siteQuery.refetch();
              void categoriesQuery.refetch();
            }}
          />
        </div>
      ) : null}
      <ValuesStrip />
      <Universes categories={categories} />
      <Signature site={site} />
      <PopularPrices categories={categories} />
      <GalleryPreview images={gallery?.results} />
      <Testimonials items={testimonials} />
      <CareersBanner site={site} />
      <FindUs site={site} />
    </>
  );
}
