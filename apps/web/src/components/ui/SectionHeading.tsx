import type { ReactNode } from "react";

import { cx } from "../../lib/cx";

interface SectionHeadingProps {
  id?: string;
  eyebrow?: string | undefined;
  title: string;
  children?: ReactNode;
  align?: "center" | "left";
  className?: string;
}

/** Gold uppercase eyebrow, serif title and an optional intro paragraph. */
export function SectionHeading({
  id,
  eyebrow,
  title,
  children,
  align = "center",
  className,
}: SectionHeadingProps) {
  return (
    <header
      className={cx(
        "mb-10 max-w-[620px] sm:mb-12",
        align === "center" ? "mx-auto text-center" : "",
        className,
      )}
    >
      {eyebrow ? <p className="eyebrow mb-3">{eyebrow}</p> : null}
      <h2 id={id} className="text-[clamp(32px,4vw,46px)]">
        {title}
      </h2>
      {children ? <div className="mt-3 text-muted">{children}</div> : null}
    </header>
  );
}
