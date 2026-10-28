import type { GalleryImage } from "@empire-t/api-client";

import { useT } from "../../lib/lang";
import { Skeleton } from "../ui/Skeleton";

const SIZES = "(min-width: 1024px) 380px, (min-width: 640px) 33vw, 50vw";

/**
 * Masonry grid with CSS columns: photos keep their natural proportions and the
 * browser reserves their space from the width and height the API returns.
 */
export function GalleryGrid({
  images,
  onOpen,
}: {
  images: GalleryImage[];
  onOpen?: (index: number) => void;
}) {
  const t = useT();
  return (
    <ul className="columns-2 gap-3 sm:columns-3 lg:gap-4">
      {images.map((item, index) => {
        if (!item.image) return null;
        const picture = (
          <img
            src={item.image.src}
            srcSet={item.image.srcset}
            sizes={SIZES}
            width={item.image.width}
            height={item.image.height}
            alt={item.alt_text}
            loading="lazy"
            decoding="async"
            className="h-auto w-full transition-transform duration-500 group-hover:scale-[1.03]"
          />
        );
        return (
          <li key={item.id} className="mb-3 break-inside-avoid lg:mb-4">
            <figure className="group relative overflow-hidden bg-line">
              {onOpen ? (
                <button
                  type="button"
                  onClick={() => {
                    onOpen(index);
                  }}
                  aria-label={t("gallery.open", { alt: item.alt_text })}
                  className="block w-full cursor-zoom-in"
                >
                  {picture}
                </button>
              ) : (
                picture
              )}
              {item.caption ? (
                <figcaption className="pointer-events-none absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/70 to-transparent px-3 pt-8 pb-2 text-xs text-white">
                  {item.caption}
                </figcaption>
              ) : null}
            </figure>
          </li>
        );
      })}
    </ul>
  );
}

const SKELETON_HEIGHTS = ["h-64", "h-44", "h-52", "h-40", "h-60", "h-48"];

export function GallerySkeleton() {
  return (
    <div className="columns-2 gap-3 sm:columns-3 lg:gap-4" aria-hidden="true">
      {SKELETON_HEIGHTS.map((height) => (
        <Skeleton key={height} className={`mb-3 w-full break-inside-avoid lg:mb-4 ${height}`} />
      ))}
    </div>
  );
}
