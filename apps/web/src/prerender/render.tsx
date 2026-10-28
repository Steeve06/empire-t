import { dehydrate } from "@tanstack/react-query";
import { renderToString } from "react-dom/server";
import {
  createStaticHandler,
  createStaticRouter,
  StaticRouterProvider,
  type RouteObject,
} from "react-router";

import type { ApiClient, Lang } from "@empire-t/api-client";

import { AppProviders } from "../app/AppProviders";
import type { AppState } from "../app/hydration";
import type { RouteHandle } from "../app/routes";
import { createI18n, DEFAULT_LANG, isLang } from "../i18n";
import { createQueryClient } from "../lib/api";
import { HeadCollector, type HeadData } from "../lib/seo";

export interface RenderedPage {
  html: string;
  head: HeadData;
  jsonLd: Record<string, unknown>[];
  state: AppState;
}

export class PrerenderError extends Error {
  override name = "PrerenderError";
}

/** Renders one URL to HTML with its data already fetched and serialised for hydration. */
export async function renderPage(
  routes: RouteObject[],
  api: ApiClient,
  url: string,
): Promise<RenderedPage> {
  const firstSegment = new URL(url).pathname.split("/")[1];
  const lang: Lang = isLang(firstSegment) ? firstSegment : DEFAULT_LANG;
  const handler = createStaticHandler(routes);
  const context = await handler.query(new Request(url));
  if (context instanceof Response) {
    throw new PrerenderError(
      `${url} answered with a redirect (${context.status}), nothing to render`,
    );
  }

  const queryClient = createQueryClient();
  const prefetches = context.matches.flatMap(({ route, params }) => {
    const handle = route.handle as RouteHandle | undefined;
    return handle?.prefetch?.({ queryClient, api, lang, params }) ?? [];
  });
  // Failures are inspected below from the query cache, with their query keys.
  await Promise.allSettled(prefetches);

  // A page built from failed requests would freeze an error into static HTML.
  const failed = queryClient
    .getQueryCache()
    .getAll()
    .filter((query) => query.state.status === "error");
  if (failed.length) {
    const reasons = failed.map(
      (query) => `${JSON.stringify(query.queryKey)}: ${String(query.state.error)}`,
    );
    throw new PrerenderError(`API requests failed for ${url}\n  ${reasons.join("\n  ")}`);
  }

  const collector = new HeadCollector();
  const router = createStaticRouter(handler.dataRoutes, context);
  const html = renderToString(
    <AppProviders queryClient={queryClient} i18n={createI18n(lang)} api={api} head={collector}>
      <StaticRouterProvider router={router} context={context} hydrate={false} />
    </AppProviders>,
  );
  if (!collector.head) throw new PrerenderError(`${url} rendered without calling useSeo()`);

  const state: AppState = { queries: dehydrate(queryClient) };
  // Drop cached queries and their garbage-collection timers, which would keep Node alive.
  queryClient.clear();
  return { html, head: collector.head, jsonLd: collector.jsonLd, state };
}
