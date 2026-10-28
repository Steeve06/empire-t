import type { QueryClient } from "@tanstack/react-query";
import type { Params, RouteObject } from "react-router";

import type { ApiClient, Lang } from "@empire-t/api-client";

import { DEFAULT_LANG, LANGS } from "../i18n";
import { queries } from "../lib/api";
import { PAGE_SEGMENTS, type PageId } from "../lib/paths";
import NotFoundPage from "../pages/NotFoundPage";
import { RouteErrorBoundary, ServerErrorPage } from "../pages/ServerErrorPage";
import { LanguageRedirect } from "./LanguageRedirect";
import { RootLayout } from "./RootLayout";

export interface PrefetchContext {
  queryClient: QueryClient;
  api: ApiClient;
  lang: Lang;
  params: Params;
}

/**
 * `prefetch` lists the queries a page renders. The pre-renderer awaits them so the
 * static HTML contains real content; in the browser, components fetch on their own
 * and show skeletons instead of blocking navigation on a slow network.
 */
export type Prefetch = (context: PrefetchContext) => Promise<unknown>[];

export interface RouteHandle {
  page?: PageId;
  prefetch?: Prefetch;
}

type PageModule = Promise<{ default: React.ComponentType }>;

function page(
  lang: Lang,
  id: PageId,
  load: () => PageModule,
  prefetch: Prefetch | undefined,
  subPath?: string,
): RouteObject {
  const segment = PAGE_SEGMENTS[id][lang];
  const handle: RouteHandle = prefetch ? { page: id, prefetch } : { page: id };
  const lazy = async () => ({ Component: (await load()).default });
  if (!segment) return { index: true, handle, lazy };
  return { path: subPath ? `${segment}/${subPath}` : segment, handle, lazy };
}

function pageRoutes(lang: Lang): RouteObject[] {
  return [
    page(
      lang,
      "home",
      () => import("../pages/HomePage"),
      ({ queryClient, api }) => [
        queryClient.query(queries.featuredGallery(api, lang)),
        queryClient.query(queries.testimonials(api, lang)),
      ],
    ),
    { path: "*", Component: NotFoundPage },
  ];
}

const layoutPrefetch: Prefetch = ({ queryClient, api, lang }) => [
  queryClient.query(queries.site(api, lang)),
  queryClient.query(queries.categories(api, lang)),
];

export function buildRoutes({ statusPages = false } = {}): RouteObject[] {
  return [
    { path: "/", Component: LanguageRedirect },
    ...LANGS.map((lang): RouteObject => ({
      path: `/${lang}`,
      element: <RootLayout lang={lang} />,
      handle: { prefetch: layoutPrefetch } satisfies RouteHandle,
      children: [
        {
          errorElement: <RouteErrorBoundary />,
          children: [
            ...pageRoutes(lang),
            // Rendered to the static 500.html by the pre-renderer only.
            ...(statusPages ? [{ path: "__500", Component: ServerErrorPage }] : []),
          ],
        },
      ],
    })),
    {
      element: <RootLayout lang={DEFAULT_LANG} />,
      handle: { prefetch: layoutPrefetch } satisfies RouteHandle,
      children: [{ path: "*", Component: NotFoundPage }],
    },
  ];
}
