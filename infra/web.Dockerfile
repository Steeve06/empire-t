# syntax=docker/dockerfile:1.7
# Multi-stage image for the React site.
#   target "dev"       : Vite dev server with hot reload (source bind-mounted by compose)
#   target "prerender" : production build plus the pre-renderer; at start it renders every
#                        page from the live API into the shared volume that nginx serves

ARG NODE_VERSION=22

FROM node:${NODE_VERSION}-slim AS base
ENV PNPM_HOME=/pnpm PATH=/pnpm:$PATH CI=true
RUN corepack enable && corepack prepare pnpm@10.28.0 --activate
WORKDIR /repo

# ---- Dependencies, cached until a manifest or the lockfile changes ----------
FROM base AS deps
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/web/package.json apps/web/
COPY packages/api-client/package.json packages/api-client/
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile

# ---- Development -----------------------------------------------------------
FROM deps AS dev
COPY . .
RUN chown -R node:node /repo
USER node
EXPOSE 5173
CMD ["pnpm", "--filter", "@empire-t/web", "exec", "vite", "--host", "0.0.0.0"]

# ---- Production build ------------------------------------------------------
FROM deps AS build
COPY tsconfig.base.json ./
COPY packages/api-client packages/api-client
COPY apps/web apps/web
# The public origin is baked into canonical URLs, Open Graph tags and the sitemap.
ARG VITE_SITE_URL
RUN test -n "$VITE_SITE_URL" || (echo "Build argument VITE_SITE_URL is required" && exit 1)
ENV VITE_SITE_URL=$VITE_SITE_URL
RUN pnpm --filter @empire-t/web build

# ---- Pre-renderer (one-shot job) ---------------------------------------------
# The SSR bundle is self-contained (ssr.noExternal), so no node_modules are shipped.
FROM node:${NODE_VERSION}-slim AS prerender
WORKDIR /app
COPY --from=build --chown=node:node /repo/apps/web/dist ./dist
COPY --from=build --chown=node:node /repo/apps/web/dist-ssr ./dist-ssr
USER node
ENV PRERENDER_API_URL=http://api:8000 SITE_OUTPUT_DIR=/site
CMD ["node", "dist-ssr/run.js"]
