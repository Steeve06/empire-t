import { cx } from "../../lib/cx";

/** Neutral shimmer block shown while content loads. Hidden from screen readers. */
export function Skeleton({ className }: { className?: string }) {
  return (
    <span
      aria-hidden="true"
      className={cx(
        "block animate-pulse rounded-[2px] bg-line/70 motion-reduce:animate-none",
        className,
      )}
    />
  );
}

/** Announces loading once for assistive technology while skeletons are on screen. */
export function LoadingRegion({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div role="status" aria-live="polite" aria-busy="true">
      <span className="sr-only">{label}</span>
      {children}
    </div>
  );
}
