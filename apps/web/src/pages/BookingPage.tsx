import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { useSearchParams } from "react-router";

import type { BookingCreated } from "@empire-t/api-client";

import { BookingConfirmation } from "../components/booking/BookingConfirmation";
import { BookingForm } from "../components/booking/BookingForm";
import { ErrorState } from "../components/ui/ErrorState";
import { PageHeader } from "../components/ui/PageHeader";
import { Skeleton } from "../components/ui/Skeleton";
import { queries, useApi } from "../lib/api";
import { useLang, useT } from "../lib/lang";
import type { BookingPrefill } from "../lib/paths";
import { useSeo } from "../lib/seo";

export default function BookingPage() {
  const t = useT();
  const lang = useLang();
  const api = useApi();
  const [params] = useSearchParams();
  const siteQuery = useQuery(queries.site(api, lang));
  const categoriesQuery = useQuery(queries.categories(api, lang));
  const [booking, setBooking] = useState<BookingCreated | null>(null);
  // Remounts the form for "Faire une autre réservation" so it starts clean.
  const [formKey, setFormKey] = useState(0);
  useSeo({ title: t("booking.title"), description: t("booking.intro") });

  const prefill: BookingPrefill = {
    service: params.get("service") ?? undefined,
    date: params.get("date") ?? undefined,
    time: params.get("time") ?? undefined,
    phone: params.get("phone") ?? undefined,
    via: params.get("via") === "quick" ? "quick" : undefined,
  };
  const failed = [siteQuery, categoriesQuery].find((query) => query.isError && !query.data);

  return (
    <>
      <PageHeader title={t("booking.title")}>{t("booking.subtitle")}</PageHeader>
      <section className="container-site max-w-[680px] py-12 sm:py-16">
        {booking ? (
          <BookingConfirmation
            booking={booking}
            onReset={() => {
              setBooking(null);
              setFormKey((key) => key + 1);
            }}
          />
        ) : (
          <>
            <p className="mb-2">{t("booking.intro")}</p>
            <p className="mb-8 text-sm text-muted">{t("booking.walkIn")}</p>
            {siteQuery.data && categoriesQuery.data ? (
              <BookingForm
                key={formKey}
                site={siteQuery.data}
                categories={categoriesQuery.data}
                prefill={formKey === 0 ? prefill : {}}
                onBooked={(created) => {
                  setBooking(created);
                  window.scrollTo({ top: 0 });
                }}
              />
            ) : failed ? (
              <ErrorState
                error={failed.error}
                onRetry={() => {
                  void siteQuery.refetch();
                  void categoriesQuery.refetch();
                }}
              />
            ) : (
              <div aria-hidden="true" className="grid gap-5">
                {[1, 2, 3, 4].map((row) => (
                  <Skeleton key={row} className="h-12 w-full" />
                ))}
              </div>
            )}
          </>
        )}
      </section>
    </>
  );
}
