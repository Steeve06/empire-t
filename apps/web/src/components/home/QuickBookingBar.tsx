import { useId, type SubmitEvent } from "react";
import { useNavigate } from "react-router";

import type { ServiceCategory, SiteSettings } from "@empire-t/api-client";

import { formatTime } from "../../lib/format";
import { dayTimes } from "../../lib/hours";
import { useLang, useT } from "../../lib/lang";
import { bookingPath } from "../../lib/paths";
import { useToday } from "../../lib/useToday";
import { buttonClass } from "../ui/buttonStyles";

const fieldClass =
  "min-h-11 w-full border-0 bg-transparent py-1 text-[15px] font-medium tracking-normal text-ink normal-case outline-none focus-visible:outline-none";

/**
 * Overlaps the hero. Nothing is sent from here: the values open the booking page
 * prefilled, where availability is checked and the request is confirmed.
 */
export function QuickBookingBar({
  site,
  categories,
}: {
  site: SiteSettings | undefined;
  categories: ServiceCategory[];
}) {
  const t = useT();
  const lang = useLang();
  const navigate = useNavigate();
  const id = useId();
  const today = useToday();

  function onSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const value = (name: string) => {
      const raw = data.get(name);
      return typeof raw === "string" && raw.trim() ? raw.trim() : undefined;
    };
    void navigate(
      bookingPath(lang, {
        service: value("service"),
        date: value("date"),
        time: value("time"),
        phone: value("phone"),
      }),
    );
  }

  const label =
    "grid border-line px-4 py-3 text-[11px] tracking-[0.14em] text-muted uppercase focus-within:bg-page";

  return (
    <form
      aria-label={t("home.quick.label")}
      onSubmit={onSubmit}
      className="relative z-10 mx-4 -mt-12 grid grid-cols-2 border border-line bg-card shadow-[0_18px_40px_rgb(0_0_0/0.18)] md:mx-auto md:max-w-[1000px] md:grid-cols-[1.3fr_1fr_0.8fr_1fr_auto]"
    >
      <label
        htmlFor={`${id}-service`}
        className={`${label} col-span-2 border-b md:col-span-1 md:border-r md:border-b-0`}
      >
        {t("home.quick.service")}
        <select id={`${id}-service`} name="service" className={fieldClass} defaultValue="">
          <option value="">{t("home.quick.chooseService")}</option>
          {categories.map((category) => (
            <optgroup key={category.slug} label={category.name}>
              {category.services.map((service) => (
                <option key={service.slug} value={service.slug}>
                  {service.name}
                </option>
              ))}
            </optgroup>
          ))}
        </select>
      </label>
      <label htmlFor={`${id}-date`} className={`${label} border-r border-b md:border-b-0`}>
        {t("home.quick.date")}
        <input id={`${id}-date`} name="date" type="date" min={today} className={fieldClass} />
      </label>
      <label htmlFor={`${id}-time`} className={`${label} border-b md:border-r md:border-b-0`}>
        {t("home.quick.time")}
        <select id={`${id}-time`} name="time" className={fieldClass} defaultValue="">
          <option value="">{t("home.quick.anyTime")}</option>
          {site
            ? dayTimes(site).map((time) => (
                <option key={time} value={time}>
                  {formatTime(time, lang)}
                </option>
              ))
            : null}
        </select>
      </label>
      <label htmlFor={`${id}-phone`} className={`${label} col-span-2 md:col-span-1 md:border-r`}>
        {t("home.quick.phone")}
        <input
          id={`${id}-phone`}
          name="phone"
          type="tel"
          inputMode="tel"
          autoComplete="tel"
          placeholder={t("home.quick.phonePlaceholder")}
          className={`${fieldClass} placeholder:text-muted/80`}
        />
      </label>
      <button type="submit" className={buttonClass("gold", "col-span-2 min-h-14 md:col-span-1")}>
        {t("home.quick.submit")}
      </button>
    </form>
  );
}
