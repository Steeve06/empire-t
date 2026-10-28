import { render } from "@testing-library/react";
import { createMemoryRouter, RouterProvider } from "react-router";
import { vi } from "vitest";

import { createApiClient } from "@empire-t/api-client";

import { AppProviders } from "../app/AppProviders";
import { buildRoutes } from "../app/routes";
import { createI18n, isLang } from "../i18n";
import { createQueryClient } from "../lib/api";
import * as fixtures from "./fixtures";

type Responder = (request: Request) => unknown;

/** Responses keyed by API path (without query string). A function receives the request. */
export type ApiRoutes = Record<string, unknown>;

const defaults: ApiRoutes = {
  "/api/v1/site/": fixtures.site,
  "/api/v1/categories/": fixtures.categories,
  "/api/v1/supplements/": fixtures.supplements,
  "/api/v1/careers/openings/": fixtures.openings,
  "/api/v1/gallery/": { count: 0, next: null, previous: null, results: [] },
  "/api/v1/testimonials/": [],
  "/api/v1/team/": [],
};

export class HttpResponse {
  constructor(
    readonly status: number,
    readonly body: unknown,
  ) {}
}

/** A fetch that serves fixtures, so tests exercise the real typed client end to end. */
export function fakeFetch(overrides: ApiRoutes = {}) {
  const routes = { ...defaults, ...overrides };
  return vi.fn<typeof globalThis.fetch>((input) => {
    const request = input instanceof Request ? input : new Request(String(input));
    const { pathname } = new URL(request.url);
    if (!(pathname in routes)) {
      return Promise.resolve(
        new Response(JSON.stringify({ detail: "Not found" }), { status: 404 }),
      );
    }
    const entry = routes[pathname];
    const value = typeof entry === "function" ? (entry as Responder)(request) : entry;
    const { status, body } = value instanceof HttpResponse ? value : new HttpResponse(200, value);
    return Promise.resolve(
      new Response(JSON.stringify(body), {
        status,
        headers: { "Content-Type": "application/json" },
      }),
    );
  });
}

/** Renders the whole app (layout and routing included) at `path`. */
export function renderApp(path: string, overrides: ApiRoutes = {}) {
  const fetch = fakeFetch(overrides);
  const api = createApiClient({ baseUrl: "http://api.test", fetch });
  const queryClient = createQueryClient();
  queryClient.setDefaultOptions({
    queries: { ...queryClient.getDefaultOptions().queries, retry: false },
  });
  const router = createMemoryRouter(buildRoutes(), { initialEntries: [path] });
  const first = path.split("/")[1];
  const utils = render(
    <AppProviders
      queryClient={queryClient}
      i18n={createI18n(isLang(first) ? first : "fr")}
      api={api}
    >
      <RouterProvider router={router} />
    </AppProviders>,
  );
  return { ...utils, router, fetch, queryClient };
}
