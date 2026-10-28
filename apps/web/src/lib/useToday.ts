import { useSyncExternalStore } from "react";

import { todayInYaounde } from "./format";

const subscribe = () => () => undefined;

/**
 * Today's date in Yaoundé, known only in the browser. Pages are pre-rendered at
 * build time, so the server snapshot is `undefined` and hydration then fills in
 * the real date (a date computed during rendering would be stale on later days).
 */
export function useToday(): string | undefined {
  return useSyncExternalStore(subscribe, todayInYaounde, () => undefined);
}
