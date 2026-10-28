import { QueryClientProvider, type QueryClient } from "@tanstack/react-query";
import type { i18n as I18n } from "i18next";
import type { ReactNode } from "react";
import { I18nextProvider } from "react-i18next";

import type { ApiClient } from "@empire-t/api-client";

import { ApiContext } from "../lib/api";
import { HeadContext, type HeadCollector } from "../lib/seo";

interface AppProvidersProps {
  queryClient: QueryClient;
  i18n: I18n;
  api: ApiClient;
  /** Present only while pre-rendering; collects the page's <head>. */
  head?: HeadCollector | null;
  children: ReactNode;
}

export function AppProviders({ queryClient, i18n, api, head = null, children }: AppProvidersProps) {
  return (
    <I18nextProvider i18n={i18n}>
      <QueryClientProvider client={queryClient}>
        <ApiContext.Provider value={api}>
          <HeadContext.Provider value={head}>{children}</HeadContext.Provider>
        </ApiContext.Provider>
      </QueryClientProvider>
    </I18nextProvider>
  );
}
