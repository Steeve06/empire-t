import type { Lang, ServiceCategory, SiteSettings } from "@empire-t/api-client";

import { pathFor } from "./paths";
import { SITE_URL } from "./seo";

/** schema.org HairSalon (a LocalBusiness subtype) for Google's local results. */
export function localBusinessJsonLd(
  site: SiteSettings,
  categories: ServiceCategory[] | undefined,
  lang: Lang,
): Record<string, unknown> {
  const prices = (categories ?? [])
    .flatMap((category) => category.services.map((service) => service.price))
    .filter((price): price is number => typeof price === "number");
  const sameAs = Object.values(site.social).filter(Boolean);

  return {
    "@context": "https://schema.org",
    "@type": "HairSalon",
    "@id": `${SITE_URL}/#business`,
    name: `${site.business_name} ${site.business_subtitle}`,
    slogan: site.tagline,
    url: `${SITE_URL}${pathFor("home", lang)}`,
    image: `${SITE_URL}/og-default.jpg`,
    telephone: site.whatsapp_number,
    email: site.email,
    address: {
      "@type": "PostalAddress",
      streetAddress: site.address_line,
      addressLocality: site.city,
      addressCountry: site.country_code,
    },
    geo: { "@type": "GeoCoordinates", latitude: site.latitude, longitude: site.longitude },
    ...(site.maps_url ? { hasMap: site.maps_url } : {}),
    openingHours: site.opening_hours.schema_org,
    ...(prices.length ? { priceRange: `${Math.min(...prices)} - ${Math.max(...prices)} XAF` } : {}),
    currenciesAccepted: "XAF",
    paymentAccepted: site.accepts_mobile_money ? "Cash, Mobile Money" : "Cash",
    ...(sameAs.length ? { sameAs } : {}),
  };
}
