import type { ResponsiveImage } from "@empire-t/api-client";

import { cx } from "../../lib/cx";

interface PhotoProps {
  image: ResponsiveImage | null | undefined;
  alt: string;
  /** Label shown on the placeholder when the owner has not uploaded this photo yet. */
  placeholder: string;
  sizes: string;
  /** Above-the-fold images load eagerly with high priority (the LCP element). */
  priority?: boolean;
  tone?: "dark" | "rose" | "light";
  className?: string;
}

/**
 * Responsive WebP photo from the API (480/960/1600 px variants), with intrinsic
 * width and height so the browser reserves space and nothing jumps while it loads.
 */
export function Photo({
  image,
  alt,
  placeholder,
  sizes,
  priority = false,
  tone = "dark",
  className,
}: PhotoProps) {
  if (!image) {
    return (
      <div
        role="img"
        aria-label={placeholder}
        className={cx(
          "photo-placeholder",
          tone === "rose" && "is-rose",
          tone === "light" && "is-light",
          className,
        )}
      >
        <span aria-hidden="true">{placeholder}</span>
      </div>
    );
  }
  return (
    <img
      src={image.src}
      srcSet={image.srcset}
      sizes={sizes}
      width={image.width}
      height={image.height}
      alt={alt}
      loading={priority ? "eager" : "lazy"}
      decoding={priority ? "sync" : "async"}
      fetchPriority={priority ? "high" : "auto"}
      className={cx("object-cover", className)}
    />
  );
}
