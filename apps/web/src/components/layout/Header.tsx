import { useEffect, useId, useRef, useState } from "react";
import { Link, NavLink, useLocation } from "react-router";

import type { ServiceCategory } from "@empire-t/api-client";

import { cx } from "../../lib/cx";
import { useLang, useT } from "../../lib/lang";
import { pathFor, servicesPath, type PageId } from "../../lib/paths";
import { ButtonLink } from "../ui/Button";
import { ChevronDownIcon, CloseIcon, MenuIcon } from "../ui/Icons";
import { LanguageToggle } from "./LanguageToggle";
import { Logo } from "./Logo";

interface HeaderProps {
  name: string;
  subtitle: string;
  categories: ServiceCategory[];
  recruitmentOpen: boolean;
}

const linkClass = ({ isActive }: { isActive: boolean }) =>
  cx(
    "flex min-h-11 items-center rounded-[3px] px-3 text-sm font-medium tracking-[0.04em] hover:text-gold-ink",
    isActive && "text-gold-ink",
  );

export function Header({ name, subtitle, categories, recruitmentOpen }: HeaderProps) {
  const t = useT();
  const lang = useLang();
  const { pathname } = useLocation();
  // Each menu remembers the path it was opened on: navigating elsewhere closes it.
  const [menuPath, setMenuPath] = useState<string | null>(null);
  const [servicesMenuPath, setServicesPath] = useState<string | null>(null);
  const menuOpen = menuPath === pathname;
  const servicesOpen = servicesMenuPath === pathname;
  const servicesRef = useRef<HTMLLIElement>(null);
  const burgerRef = useRef<HTMLButtonElement>(null);
  const panelId = useId();
  const servicesId = useId();

  useEffect(() => {
    if (!menuOpen && !servicesOpen) return;
    const close = () => {
      setMenuPath(null);
      setServicesPath(null);
    };
    const onKey = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      if (menuOpen) burgerRef.current?.focus();
      close();
    };
    const onPointer = (event: PointerEvent) => {
      if (servicesOpen && !servicesRef.current?.contains(event.target as Node)) close();
    };
    document.addEventListener("keydown", onKey);
    document.addEventListener("pointerdown", onPointer);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.removeEventListener("pointerdown", onPointer);
    };
  }, [menuOpen, servicesOpen]);

  const pages: PageId[] = ["home", "about", "services", "gallery", "careers", "contact"];
  const visible = pages.filter((page) => page !== "careers" || recruitmentOpen);

  const servicesLinks = (
    <>
      {categories.map((category) => (
        <li key={category.slug}>
          <Link
            to={servicesPath(lang, category.slug)}
            className="flex min-h-11 items-center px-3 text-sm hover:text-gold-ink"
          >
            {category.title}
          </Link>
        </li>
      ))}
      <li>
        <Link
          to={servicesPath(lang)}
          className="flex min-h-11 items-center px-3 text-sm font-semibold text-gold-ink"
        >
          {t("nav.allServices")}
        </Link>
      </li>
    </>
  );

  return (
    <header className="sticky top-0 z-40 border-b border-line bg-page/95 backdrop-blur-sm supports-[backdrop-filter]:bg-page/85">
      <div className="container-site flex h-[68px] items-center gap-2 sm:h-[76px] sm:gap-4">
        <Logo name={name} subtitle={subtitle} />

        <nav aria-label={t("a11y.mainNav")} className="hidden lg:block">
          <ul className="flex items-center gap-1">
            {visible.map((page) =>
              page === "services" ? (
                <li key={page} ref={servicesRef} className="group relative">
                  <div className="flex items-center">
                    <NavLink to={servicesPath(lang)} className={linkClass}>
                      {t("nav.services")}
                    </NavLink>
                    <button
                      type="button"
                      aria-expanded={servicesOpen}
                      aria-controls={servicesId}
                      aria-label={t("a11y.showServices")}
                      onClick={() => {
                        setServicesPath(servicesOpen ? null : pathname);
                      }}
                      className="-ml-2 flex size-11 items-center justify-center hover:text-gold-ink"
                    >
                      <ChevronDownIcon
                        className={cx("transition-transform", servicesOpen && "rotate-180")}
                      />
                    </button>
                  </div>
                  <ul
                    id={servicesId}
                    className={cx(
                      "invisible absolute top-full left-0 z-10 min-w-[240px] border border-line bg-card p-2 opacity-0 shadow-[0_12px_30px_rgb(0_0_0/0.12)] transition-[opacity,visibility] duration-150",
                      "group-focus-within:visible group-focus-within:opacity-100 group-hover:visible group-hover:opacity-100",
                      servicesOpen && "visible opacity-100",
                    )}
                  >
                    {servicesLinks}
                  </ul>
                </li>
              ) : (
                <li key={page}>
                  <NavLink to={pathFor(page, lang)} end={page === "home"} className={linkClass}>
                    {t(`nav.${page}`)}
                  </NavLink>
                </li>
              ),
            )}
          </ul>
        </nav>

        <LanguageToggle />
        <div className="hidden sm:block">
          <ButtonLink to={pathFor("book", lang)}>{t("nav.book")}</ButtonLink>
        </div>
        <button
          ref={burgerRef}
          type="button"
          aria-expanded={menuOpen}
          aria-controls={panelId}
          aria-label={menuOpen ? t("a11y.closeMenu") : t("a11y.openMenu")}
          onClick={() => {
            setMenuPath(menuOpen ? null : pathname);
          }}
          className="flex size-11 items-center justify-center lg:hidden"
        >
          {menuOpen ? <CloseIcon width={26} height={26} /> : <MenuIcon width={26} height={26} />}
        </button>
      </div>

      <nav
        id={panelId}
        aria-label={t("a11y.mainNav")}
        hidden={!menuOpen}
        className="max-h-[calc(100dvh-68px)] overflow-y-auto border-t border-line bg-page pb-4 lg:hidden"
      >
        <ul className="container-site py-2">
          {visible.map((page) => (
            <li key={page} className="border-b border-line last:border-b-0">
              <NavLink to={pathFor(page, lang)} end={page !== "services"} className={linkClass}>
                {t(`nav.${page}`)}
              </NavLink>
              {page === "services" ? <ul className="pb-2 pl-4">{servicesLinks}</ul> : null}
            </li>
          ))}
        </ul>
        <div className="container-site sm:hidden">
          <ButtonLink to={pathFor("book", lang)} className="w-full">
            {t("nav.book")}
          </ButtonLink>
        </div>
      </nav>
    </header>
  );
}
