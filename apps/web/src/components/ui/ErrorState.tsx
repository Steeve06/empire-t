import { ApiError } from "@empire-t/api-client";

import { cx } from "../../lib/cx";
import { useT } from "../../lib/lang";
import { Button } from "./Button";

/** Explains a failed load in plain words and offers a retry. */
export function ErrorState({
  error,
  onRetry,
  className,
}: {
  error: unknown;
  onRetry?: () => void;
  className?: string;
}) {
  const t = useT();
  const network = error instanceof ApiError && error.isNetworkError;
  return (
    <div
      role="alert"
      className={cx("mx-auto max-w-[520px] border border-line bg-card p-6 text-center", className)}
    >
      <p className="font-display text-2xl font-semibold">{t("status.errorTitle")}</p>
      <p className="mt-2 text-muted">
        {network ? t("status.errorNetwork") : t("status.errorServer")}
      </p>
      {onRetry ? (
        <Button variant="outline" className="mt-5" onClick={onRetry}>
          {t("status.retry")}
        </Button>
      ) : null}
    </div>
  );
}
