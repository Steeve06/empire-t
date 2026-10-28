import type { ReactNode } from "react";

/** Centred message used by the 404 and error pages. */
export function StatusPage({
  code,
  title,
  text,
  children,
}: {
  code: string;
  title: string;
  text: string;
  children: ReactNode;
}) {
  return (
    <section className="container-site flex min-h-[60vh] flex-col items-center justify-center py-20 text-center">
      <p className="font-display text-[88px] leading-none font-semibold text-gold-ink sm:text-[120px]">
        {code}
      </p>
      <h1 className="mt-4 text-[clamp(32px,4vw,46px)]">{title}</h1>
      <p className="mt-3 max-w-[480px] text-muted">{text}</p>
      <div className="mt-8 flex flex-wrap justify-center gap-3">{children}</div>
    </section>
  );
}
