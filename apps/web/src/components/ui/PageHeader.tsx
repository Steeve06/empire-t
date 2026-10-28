import type { ReactNode } from "react";

/** Dark band at the top of inner pages: serif title and a short line. */
export function PageHeader({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <header className="on-night bg-night px-4 py-14 text-center text-on-night sm:py-[70px]">
      <h1 className="text-[clamp(38px,5vw,64px)]">{title}</h1>
      {children ? (
        <p className="mx-auto mt-2 max-w-[620px] text-on-night-muted">{children}</p>
      ) : null}
    </header>
  );
}
