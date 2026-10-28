import { Link, useLocation } from "react-router";

import { useLang, useT } from "../../lib/lang";
import { pathFor } from "../../lib/paths";
import { ChatIcon } from "../ui/Icons";

/** Floating green button on every page, leading to the booking form. */
export function WhatsAppFab() {
  const t = useT();
  const lang = useLang();
  const { pathname } = useLocation();
  const bookPath = pathFor("book", lang);
  if (pathname === bookPath) return null;

  return (
    <Link
      to={bookPath}
      className="fixed right-4 bottom-[calc(16px+env(safe-area-inset-bottom,0px))] z-30 inline-flex min-h-12 items-center gap-2 rounded-full bg-whatsapp px-4 font-bold text-white shadow-[0_8px_20px_rgb(0_0_0/0.3)] transition-transform hover:-translate-y-0.5 sm:px-5"
    >
      <ChatIcon width={22} height={22} />
      <span className="sr-only sm:not-sr-only">{t("whatsappFab")}</span>
    </Link>
  );
}
