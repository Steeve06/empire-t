import { useQuery } from "@tanstack/react-query";
import { useEffect, useRef } from "react";
import { Outlet, useLocation } from "react-router";

import type { Lang } from "@empire-t/api-client";

import { Footer } from "../components/layout/Footer";
import { Header } from "../components/layout/Header";
import { TopBar } from "../components/layout/TopBar";
import { WhatsAppFab } from "../components/layout/WhatsAppFab";
import { queries, useApi } from "../lib/api";
import { LangContext, useT } from "../lib/lang";
import { useJsonLd } from "../lib/seo";
import { localBusinessJsonLd } from "../lib/structuredData";

/** Chrome shared by every page of one language: top bar, header, footer, WhatsApp button. */
export function RootLayout({ lang }: { lang: Lang }) {
  return (
    <LangContext.Provider value={lang}>
      <Shell lang={lang} />
    </LangContext.Provider>
  );
}

function Shell({ lang }: { lang: Lang }) {
  const t = useT();
  const api = useApi();
  const site = useQuery(queries.site(api, lang)).data;
  const categories = useQuery(queries.categories(api, lang)).data;
  useJsonLd(site ? localBusinessJsonLd(site, categories, lang) : null);
  useRouteFocus();

  return (
    <>
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:bg-gold focus:px-4 focus:py-3 focus:font-bold focus:text-night"
      >
        {t("a11y.skipToContent")}
      </a>
      <TopBar site={site} />
      <Header
        name={site?.business_name ?? "Empire T"}
        subtitle={site?.business_subtitle ?? "Barbershop & Beauty"}
        categories={categories ?? []}
        recruitmentOpen={site?.recruitment_open ?? false}
      />
      <main id="main" tabIndex={-1} className="outline-none">
        <Outlet />
      </main>
      <Footer site={site} categories={categories ?? []} />
      <WhatsAppFab />
    </>
  );
}

/**
 * After client-side navigation, move focus to the new page and scroll to the top,
 * so keyboard and screen-reader users start reading the new content (WCAG 2.4.3).
 * Changing only the services tab keeps the scroll position.
 */
function useRouteFocus(): void {
  const { pathname } = useLocation();
  const previous = useRef(pathname);

  useEffect(() => {
    const before = previous.current;
    previous.current = pathname;
    if (before === pathname) return;
    const sameSection =
      before.split("/").slice(0, 3).join("/") === pathname.split("/").slice(0, 3).join("/");
    if (sameSection) return;
    window.scrollTo({ top: 0 });
    document.getElementById("main")?.focus({ preventScroll: true });
  }, [pathname]);
}
