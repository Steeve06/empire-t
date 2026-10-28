import { isRouteErrorResponse, useRouteError } from "react-router";

import { Button, ButtonLink } from "../components/ui/Button";
import { StatusPage } from "../components/ui/StatusPage";
import { useLang, useT } from "../lib/lang";
import { pathFor } from "../lib/paths";
import { useSeo } from "../lib/seo";
import NotFoundPage from "./NotFoundPage";

/** Shown when a page fails to render (also pre-rendered as the static 500.html). */
export function ServerErrorPage() {
  const t = useT();
  const lang = useLang();
  useSeo({ title: t("serverError.title"), description: t("serverError.text"), noindex: true });

  return (
    <StatusPage code="500" title={t("serverError.title")} text={t("serverError.text")}>
      <Button
        onClick={() => {
          window.location.reload();
        }}
      >
        {t("serverError.reload")}
      </Button>
      <ButtonLink to={pathFor("home", lang)} variant="outline">
        {t("notFound.home")}
      </ButtonLink>
    </StatusPage>
  );
}

/** Route error boundary: a 404 response renders the not-found page, anything else the 500 page. */
export function RouteErrorBoundary() {
  const error = useRouteError();
  if (isRouteErrorResponse(error) && error.status === 404) return <NotFoundPage />;
  console.error("Route render failed", error);
  return <ServerErrorPage />;
}
