import type { ReactNode } from "react";

/** Form-level message (server refusal, network failure), announced when it appears. */
export function FormAlert({ children }: { children: ReactNode }) {
  if (!children) return null;
  return (
    <div role="alert" className="border-l-4 border-danger bg-card px-4 py-3 text-sm text-danger">
      {children}
    </div>
  );
}
