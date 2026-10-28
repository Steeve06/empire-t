/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Public origin of the site, used for canonical URLs, sitemap and social previews. */
  readonly VITE_SITE_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
