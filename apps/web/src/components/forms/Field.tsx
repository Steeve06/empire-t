import { cloneElement, useId, type ReactElement, type ReactNode } from "react";

import { cx } from "../../lib/cx";

export const inputClass =
  "min-h-12 w-full rounded-[2px] border border-line bg-card px-3.5 py-3 text-[16px] text-ink placeholder:text-muted/80 focus:border-gold focus:outline-none focus-visible:outline-2 focus-visible:outline-gold aria-[invalid=true]:border-danger disabled:opacity-60";

interface FieldProps {
  label: string;
  error?: string | undefined;
  hint?: ReactNode;
  className?: string;
  /** A single input, select or textarea; it receives id and ARIA wiring. */
  children: ReactElement<Record<string, unknown>>;
}

/**
 * Label, control, hint and error, wired together for screen readers:
 * the error is announced and linked with aria-describedby and aria-invalid.
 * Font size stays at 16px so mobile browsers do not zoom on focus.
 */
export function Field({ label, error, hint, className, children }: FieldProps) {
  const id = useId();
  const hintId = hint ? `${id}-hint` : undefined;
  const errorId = error ? `${id}-error` : undefined;
  const describedBy = [hintId, errorId].filter(Boolean).join(" ") || undefined;

  return (
    <div className={cx("grid gap-1.5", className)}>
      <label htmlFor={id} className="text-xs font-semibold tracking-[0.1em] text-muted uppercase">
        {label}
      </label>
      {cloneElement(children, {
        id,
        "aria-invalid": error ? true : undefined,
        "aria-describedby": describedBy,
      })}
      {hint ? (
        <p id={hintId} className="text-[13px] text-muted">
          {hint}
        </p>
      ) : null}
      {error ? (
        <p id={errorId} role="alert" className="text-[13px] font-medium text-danger">
          {error}
        </p>
      ) : null}
    </div>
  );
}
