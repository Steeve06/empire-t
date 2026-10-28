import type { SiteSettings } from "@empire-t/api-client";

const toMinutes = (hhmm: string) => {
  const [hours = "0", minutes = "0"] = hhmm.split(":");
  return Number(hours) * 60 + Number(minutes);
};

const toHhmm = (minutes: number) =>
  `${String(Math.floor(minutes / 60)).padStart(2, "0")}:${String(minutes % 60).padStart(2, "0")}`;

/** Start times from opening to closing at the shop's slot interval ("07:00", "07:30"...). */
export function dayTimes(site: SiteSettings): string[] {
  const step = Math.max(site.slot_interval_minutes ?? 30, 5);
  const times: string[] = [];
  for (
    let minute = toMinutes(site.opening_hours.opens);
    minute < toMinutes(site.opening_hours.closes);
    minute += step
  ) {
    times.push(toHhmm(minute));
  }
  return times;
}
