import type { SiteSettings } from "@empire-t/api-client";

/** The owner's Google Maps share link when set, otherwise a search on the pin's coordinates. */
export function mapsLink(site: SiteSettings): string {
  // An empty string means "not set" (the admin field is optional), so `??` would not do.
  if (site.maps_url) return site.maps_url;
  return `https://www.google.com/maps/search/?api=1&query=${site.latitude},${site.longitude}`;
}
