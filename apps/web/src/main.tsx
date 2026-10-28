import "./styles/fonts.css";
import "./styles/index.css";

import { hydrate } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot, hydrateRoot } from "react-dom/client";
import { createBrowserRouter } from "react-router";
import { RouterProvider } from "react-router/dom";

import { AppProviders } from "./app/AppProviders";
import { preloadMatchedRoutes, readAppState } from "./app/hydration";
import { buildRoutes } from "./app/routes";
import { DEFAULT_LANG, createI18n, isLang } from "./i18n";
import { browserApi, createQueryClient } from "./lib/api";

const container = document.getElementById("root");
if (!container) throw new Error("Missing #root element");

const queryClient = createQueryClient();
const state = readAppState(document);
if (state) hydrate(queryClient, state.queries);

const firstSegment = window.location.pathname.split("/")[1];
const i18n = createI18n(isLang(firstSegment) ? firstSegment : DEFAULT_LANG);

const routes = buildRoutes();
await preloadMatchedRoutes(routes, window.location.pathname);
const router = createBrowserRouter(routes);

const app = (
  <StrictMode>
    <AppProviders queryClient={queryClient} i18n={i18n} api={browserApi}>
      <RouterProvider router={router} />
    </AppProviders>
  </StrictMode>
);

// The SPA shell holds only a placeholder comment; pre-rendered pages hold real elements.
if (container.firstElementChild) {
  hydrateRoot(container, app, {
    onRecoverableError: (error) => {
      console.warn("Hydration recovered", error);
    },
  });
} else {
  createRoot(container).render(app);
}
