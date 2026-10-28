import { ButtonLink } from "../components/ui/Button";
import { StatusPage } from "../components/ui/StatusPage";
import { useLang, useT } from "../lib/lang";
import { pathFor } from "../lib/paths";
import { useSeo } from "../lib/seo";

export default function NotFoundPage() {
  const t = useT();
  const lang = useLang();
  useSeo({ title: t("notFound.title"), description: t("notFound.text"), noindex: true });

  return (
    <StatusPage code="404" title={t("notFound.title")} text={t("notFound.text")}>
      <ButtonLink to={pathFor("home", lang)}>{t("notFound.home")}</ButtonLink>
      <ButtonLink to={pathFor("services", lang)} variant="outline">
        {t("nav.services")}
      </ButtonLink>
    </StatusPage>
  );
}
