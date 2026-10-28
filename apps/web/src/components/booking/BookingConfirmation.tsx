import { useEffect, useRef } from "react";

import type { BookingCreated } from "@empire-t/api-client";

import { formatDate, formatTime } from "../../lib/format";
import { useLang, useT } from "../../lib/lang";
import { Button } from "../ui/Button";
import { buttonClass } from "../ui/buttonStyles";
import { ChatIcon, CheckIcon } from "../ui/Icons";
import { QrCode } from "../ui/QrCode";

const REDIRECT_DELAY_MS = 900;

/**
 * Shown once the request is stored. Phones go straight to WhatsApp with the
 * prefilled message (the app opens on top); computers keep this screen, where the
 * QR code moves the message to a phone. Either way the button stays available.
 */
export function BookingConfirmation({
  booking,
  onReset,
}: {
  booking: BookingCreated;
  onReset: () => void;
}) {
  const t = useT();
  const lang = useLang();
  const headingRef = useRef<HTMLHeadingElement>(null);
  const autoRedirect =
    typeof window !== "undefined" && window.matchMedia("(pointer: coarse)").matches;

  useEffect(() => {
    headingRef.current?.focus({ preventScroll: true });
    if (!autoRedirect) return;
    const timer = window.setTimeout(() => {
      window.location.assign(booking.whatsapp_url);
    }, REDIRECT_DELAY_MS);
    return () => {
      window.clearTimeout(timer);
    };
  }, [autoRedirect, booking.whatsapp_url]);

  return (
    <div className="border border-gold bg-card p-6 sm:p-8">
      <p className="flex size-12 items-center justify-center rounded-full bg-gold text-night">
        <CheckIcon width={26} height={26} />
      </p>
      <h2 ref={headingRef} tabIndex={-1} className="mt-4 text-[34px] outline-none">
        {t("booking.confirmed.title")}
      </h2>
      <p className="mt-1 text-sm font-semibold tracking-[0.08em] text-gold-ink uppercase">
        {t("booking.confirmed.reference", { reference: booking.reference })}
      </p>
      <p className="mt-4">
        {t("booking.confirmed.summary", {
          service: booking.service_name,
          date: formatDate(booking.date, lang, { weekday: "long" }),
          time: formatTime(booking.time_slot, lang),
        })}
      </p>
      <p className="mt-2 text-muted">{t("booking.confirmed.next")}</p>
      {autoRedirect ? (
        <p className="mt-2 text-sm text-muted" role="status">
          {t("booking.confirmed.redirecting")}
        </p>
      ) : null}

      <div className="mt-6 flex flex-wrap gap-3">
        <a href={booking.whatsapp_url} className={buttonClass("gold")}>
          <ChatIcon />
          {t("booking.confirmed.openWhatsapp")}
        </a>
        <Button variant="outline" onClick={onReset}>
          {t("booking.confirmed.another")}
        </Button>
      </div>

      <div className="mt-8 hidden items-center gap-5 border-t border-line pt-6 md:flex">
        <QrCode value={booking.whatsapp_url} label={t("booking.confirmed.qrAlt")} />
        <p className="max-w-[260px] text-sm text-muted">{t("booking.confirmed.qr")}</p>
      </div>
    </div>
  );
}
