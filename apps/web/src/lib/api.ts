import { infiniteQueryOptions, queryOptions, QueryClient } from "@tanstack/react-query";
import { createContext, useContext } from "react";

import {
  ApiError,
  createApiClient,
  type ApiClient,
  type GalleryCategory,
  type Lang,
} from "@empire-t/api-client";

/** Same origin in the browser (nginx in production, the Vite proxy in development). */
export const browserApi: ApiClient = createApiClient({ baseUrl: "" });

export const ApiContext = createContext<ApiClient>(browserApi);

export function useApi(): ApiClient {
  return useContext(ApiContext);
}

/**
 * Every read the site makes, as query definitions shared by components and the
 * pre-renderer. Keys include the language because content is translated.
 */
export const queries = {
  site: (api: ApiClient, lang: Lang) =>
    queryOptions({ queryKey: ["site", lang], queryFn: () => api.site(lang) }),
  categories: (api: ApiClient, lang: Lang) =>
    queryOptions({ queryKey: ["categories", lang], queryFn: () => api.categories(lang) }),
  supplements: (api: ApiClient, lang: Lang) =>
    queryOptions({ queryKey: ["supplements", lang], queryFn: () => api.supplements(lang) }),
  /** Gallery pages of 24 photos, loaded one page at a time ("Voir plus de photos"). */
  galleryPages: (api: ApiClient, lang: Lang, category?: GalleryCategory) =>
    infiniteQueryOptions({
      queryKey: ["gallery", lang, category ?? "all"],
      queryFn: ({ pageParam }) =>
        api.gallery(lang, category ? { category, page: pageParam } : { page: pageParam }),
      initialPageParam: 1,
      getNextPageParam: (last, _pages, page) => (last.next ? page + 1 : undefined),
    }),
  featuredGallery: (api: ApiClient, lang: Lang) =>
    queryOptions({
      queryKey: ["gallery", lang, "featured"],
      queryFn: () => api.gallery(lang, { featured: true }),
    }),
  testimonials: (api: ApiClient, lang: Lang) =>
    queryOptions({ queryKey: ["testimonials", lang], queryFn: () => api.testimonials(lang) }),
  team: (api: ApiClient, lang: Lang) =>
    queryOptions({ queryKey: ["team", lang], queryFn: () => api.team(lang) }),
  openings: (api: ApiClient, lang: Lang) =>
    queryOptions({ queryKey: ["openings", lang], queryFn: () => api.openings(lang) }),
  /** Start times still open on a day; short-lived because they depend on the clock. */
  slots: (api: ApiClient, date: string, service: string | undefined) =>
    queryOptions({
      queryKey: ["slots", date, service ?? ""],
      queryFn: ({ signal }) => api.slots(date, service, signal),
      staleTime: 60_000,
    }),
};

const MAX_RETRIES = 2;

export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // Content changes a few times a week. Pre-rendered data is older than this,
        // so the browser refreshes it once in the background after hydration.
        staleTime: 5 * 60_000,
        gcTime: 30 * 60_000,
        // Saves data on mobile plans: no refetch when the user switches apps.
        refetchOnWindowFocus: false,
        // Retry flaky mobile networks and 5xx; a 4xx will not get better by retrying.
        retry: (failureCount, error) =>
          failureCount < MAX_RETRIES &&
          (!(error instanceof ApiError) || error.isNetworkError || error.status >= 500),
        retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 8000),
      },
      mutations: { retry: false },
    },
  });
}
