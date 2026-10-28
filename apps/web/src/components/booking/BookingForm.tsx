import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useForm, useWatch } from "react-hook-form";
import { z } from "zod";

import type { BookingCreated, ServiceCategory, SiteSettings } from "@empire-t/api-client";

import { queries, useApi } from "../../lib/api";
import { formatPrice, formatTime } from "../../lib/format";
import { applyServerErrors, validators } from "../../lib/forms";
import { useLang, useT } from "../../lib/lang";
import type { BookingPrefill } from "../../lib/paths";
import { useToday } from "../../lib/useToday";
import { Field, inputClass } from "../forms/Field";
import { FormAlert } from "../forms/FormAlert";
import { Honeypot } from "../forms/Honeypot";
import { Button } from "../ui/Button";

const FIELDS = ["service", "date", "time_slot", "customer_name", "phone", "notes"] as const;

function addDays(iso: string, days: number): string {
  const date = new Date(`${iso}T00:00:00Z`);
  date.setUTCDate(date.getUTCDate() + days);
  return date.toISOString().slice(0, 10);
}

interface BookingFormProps {
  site: SiteSettings;
  categories: ServiceCategory[];
  prefill: BookingPrefill;
  onBooked: (booking: BookingCreated) => void;
}

export function BookingForm({ site, categories, prefill, onBooked }: BookingFormProps) {
  const t = useT();
  const lang = useLang();
  const api = useApi();
  const today = useToday();
  const [formError, setFormError] = useState<string | null>(null);
  const known = (slug: string | undefined) =>
    categories.some((category) => category.services.some((service) => service.slug === slug));

  const v = validators(t);
  const schema = z.object({
    service: v.required,
    date: v.required.refine((value) => !today || value >= today, t("validation.datePast")),
    time_slot: v.required,
    customer_name: v.name,
    phone: v.phone,
    notes: v.optionalText(500),
    website: v.honeypot,
  });
  type Values = z.infer<typeof schema>;

  const {
    register,
    handleSubmit,
    setError,
    setValue,
    control,
    getValues,
    formState: { errors },
  } = useForm<Values>({
    resolver: zodResolver(schema),
    defaultValues: {
      service: prefill.service && known(prefill.service) ? prefill.service : "",
      date: prefill.date ?? "",
      time_slot: prefill.time ?? "",
      customer_name: "",
      phone: prefill.phone ?? "",
      notes: "",
      website: "",
    },
  });

  const service = useWatch({ control, name: "service" });
  const date = useWatch({ control, name: "date" });
  const slots = useQuery({
    ...queries.slots(api, date, service || undefined),
    enabled: Boolean(date),
  });

  // Options arrive after the form mounts: re-apply a time chosen earlier (or carried from
  // the quick bar) so the select shows it, or clear it when that time is no longer offered.
  useEffect(() => {
    const chosen = getValues("time_slot");
    if (!slots.data || !chosen) return;
    setValue("time_slot", slots.data.slots.includes(chosen) ? chosen : "");
  }, [slots.data, getValues, setValue]);

  const booking = useMutation({
    mutationFn: (values: Values) =>
      api.createBooking(lang, {
        ...values,
        channel: prefill.via === "quick" ? "quick_bar" : "website",
      }),
    onSuccess: onBooked,
    onError: (error) => {
      setFormError(applyServerErrors(error, FIELDS, setError, t));
    },
  });

  const onSubmit = handleSubmit(
    (values) => {
      setFormError(null);
      booking.mutate(values);
    },
    () => {
      setFormError(t("validation.fixErrors"));
    },
  );

  const slotOptions = slots.data?.slots ?? [];
  const timeHint = !date
    ? t("booking.pickDateFirst")
    : slots.isFetching && !slots.data
      ? t("booking.loadingSlots")
      : slots.data && !slotOptions.length
        ? t("booking.noSlots")
        : undefined;

  return (
    <form noValidate onSubmit={(event) => void onSubmit(event)} className="relative grid gap-5">
      <Field label={t("booking.service")} error={errors.service?.message}>
        <select className={inputClass} {...register("service")}>
          <option value="">{t("booking.chooseService")}</option>
          {categories.map((category) => (
            <optgroup key={category.slug} label={category.name}>
              {category.services.map((item) => (
                <option key={item.slug} value={item.slug}>
                  {item.name} · {formatPrice(item, lang, t)}
                </option>
              ))}
            </optgroup>
          ))}
        </select>
      </Field>

      <div className="grid gap-5 sm:grid-cols-2">
        <Field label={t("booking.date")} error={errors.date?.message}>
          <input
            type="date"
            className={inputClass}
            min={today}
            max={today ? addDays(today, site.booking_horizon_days ?? 60) : undefined}
            {...register("date")}
          />
        </Field>
        <Field label={t("booking.time")} error={errors.time_slot?.message} hint={timeHint}>
          <select className={inputClass} disabled={!slotOptions.length} {...register("time_slot")}>
            <option value="">{t("booking.chooseTime")}</option>
            {slotOptions.map((slot) => (
              <option key={slot} value={slot}>
                {formatTime(slot, lang)}
              </option>
            ))}
          </select>
        </Field>
      </div>

      <div className="grid gap-5 sm:grid-cols-2">
        <Field label={t("booking.name")} error={errors.customer_name?.message}>
          <input
            type="text"
            autoComplete="name"
            className={inputClass}
            {...register("customer_name")}
          />
        </Field>
        <Field label={t("booking.phone")} error={errors.phone?.message}>
          <input
            type="tel"
            inputMode="tel"
            autoComplete="tel"
            placeholder={t("booking.phonePlaceholder")}
            className={inputClass}
            {...register("phone")}
          />
        </Field>
      </div>

      <Field label={t("booking.notes")} error={errors.notes?.message}>
        <textarea
          rows={3}
          placeholder={t("booking.notesPlaceholder")}
          className={inputClass}
          {...register("notes")}
        />
      </Field>

      <Honeypot registration={register("website")} />
      <FormAlert>{formError}</FormAlert>

      <div>
        <Button type="submit" disabled={booking.isPending} className="w-full sm:w-auto">
          {booking.isPending ? t("booking.submitting") : t("booking.submit")}
        </Button>
        <p className="mt-3 text-sm text-muted">{t("booking.noPayment")}</p>
      </div>
    </form>
  );
}
