import type { DehydratedState } from "@tanstack/react-query";
import { matchRoutes, type RouteObject } from "react-router";

export const STATE_ELEMENT_ID = "__EMPIRE_STATE__";

/** Serialized into the pre-rendered page as inert JSON (no inline script: strict CSP). */
export interface AppState {
  queries: DehydratedState;
}

export function readAppState(doc: Document): AppState | null {
  const element = doc.getElementById(STATE_ELEMENT_ID);
  if (!element?.textContent) return null;
  try {
    return JSON.parse(element.textContent) as AppState;
  } catch (error) {
    console.error("Ignoring unreadable pre-rendered state", error);
    return null;
  }
}

/**
 * Lazy route modules for the current URL must be loaded before hydrating,
 * otherwise React Router renders nothing on the first pass and the
 * pre-rendered HTML would be thrown away (a flash and a layout shift).
 */
export async function preloadMatchedRoutes(routes: RouteObject[], pathname: string): Promise<void> {
  const matches = matchRoutes(routes, pathname) ?? [];
  await Promise.all(
    matches.map(async ({ route }) => {
      if (typeof route.lazy !== "function") return;
      const resolved = await route.lazy();
      Object.assign(route, { ...resolved, lazy: undefined });
    }),
  );
}
