import { useEffect, useRef } from "react";
import { Link } from "react-router";

import type { GalleryImage } from "@empire-t/api-client";

import { useLang, useT } from "../../lib/lang";
import { bookingPath } from "../../lib/paths";
import { buttonClass } from "../ui/buttonStyles";
import { ChevronLeftIcon, ChevronRightIcon, CloseIcon } from "../ui/Icons";

interface LightboxProps {
  images: GalleryImage[];
  index: number;
  onIndexChange: (index: number) => void;
  onClose: () => void;
}

const controlClass =
  "flex size-12 items-center justify-center rounded-full bg-black/60 text-white ring-1 ring-white/40 hover:bg-black/85";

/**
 * Full-screen viewer on the native <dialog>: focus is trapped and returned, Escape
 * closes, arrow keys browse. "Réserver ce style" opens the booking page with the
 * photo's service preselected when the owner linked one.
 */
export function Lightbox({ images, index, onIndexChange, onClose }: LightboxProps) {
  const t = useT();
  const lang = useLang();
  const dialogRef = useRef<HTMLDialogElement>(null);
  const item = images[index];
  const count = images.length;

  useEffect(() => {
    const dialog = dialogRef.current;
    if (dialog && !dialog.open) dialog.showModal();
  }, []);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "ArrowRight") onIndexChange((index + 1) % count);
      if (event.key === "ArrowLeft") onIndexChange((index - 1 + count) % count);
    };
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("keydown", onKey);
    };
  }, [index, count, onIndexChange]);

  if (!item?.image) return null;

  return (
    <dialog
      ref={dialogRef}
      aria-label={item.alt_text}
      onClose={onClose}
      className="m-0 h-dvh max-h-none w-screen max-w-none bg-black/95 p-0 text-white backdrop:bg-black/80"
    >
      <div className="flex h-full flex-col">
        <div className="flex items-center justify-between gap-3 p-3">
          <p className="text-sm text-white/80" aria-live="polite">
            {t("gallery.counter", { current: index + 1, total: count })}
          </p>
          <button
            type="button"
            className={controlClass}
            onClick={() => dialogRef.current?.close()}
            aria-label={t("gallery.close")}
          >
            <CloseIcon />
          </button>
        </div>

        <figure className="relative flex min-h-0 flex-1 flex-col items-center justify-center px-2">
          <img
            key={item.id}
            src={item.image.src}
            srcSet={item.image.srcset}
            sizes="100vw"
            width={item.image.width}
            height={item.image.height}
            alt={item.alt_text}
            className="max-h-full w-auto max-w-full object-contain"
          />
          {item.caption ? (
            <figcaption className="mt-3 px-4 text-center text-sm text-white/85">
              {item.caption}
            </figcaption>
          ) : null}
          {count > 1 ? (
            <>
              <button
                type="button"
                className={`${controlClass} absolute top-1/2 left-2 -translate-y-1/2`}
                onClick={() => {
                  onIndexChange((index - 1 + count) % count);
                }}
                aria-label={t("gallery.previous")}
              >
                <ChevronLeftIcon />
              </button>
              <button
                type="button"
                className={`${controlClass} absolute top-1/2 right-2 -translate-y-1/2`}
                onClick={() => {
                  onIndexChange((index + 1) % count);
                }}
                aria-label={t("gallery.next")}
              >
                <ChevronRightIcon />
              </button>
            </>
          ) : null}
        </figure>

        <div className="flex justify-center p-4 pb-[calc(16px+env(safe-area-inset-bottom,0px))]">
          <Link
            to={bookingPath(lang, { service: item.service ?? undefined })}
            className={buttonClass("gold")}
          >
            {t("gallery.bookStyle")}
          </Link>
        </div>
      </div>
    </dialog>
  );
}
