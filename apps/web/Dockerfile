FROM node:24-bookworm-slim AS build

WORKDIR /workspace
COPY package.json package-lock.json ./
COPY apps/web/package.json apps/web/package.json
RUN npm ci --no-audit --no-fund
COPY apps/web ./apps/web
ARG API_INTERNAL_URL=http://api:8000
ENV API_INTERNAL_URL=${API_INTERNAL_URL} NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:24-bookworm-slim AS runtime

WORKDIR /workspace
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1
COPY package.json package-lock.json ./
COPY apps/web/package.json apps/web/package.json
RUN npm ci --omit=dev --no-audit --no-fund
COPY --chown=node:node --from=build /workspace/apps/web/.next ./apps/web/.next
COPY apps/web/next.config.mjs ./apps/web/next.config.mjs
USER node
EXPOSE 3000
CMD ["npm", "run", "start", "--workspace", "@elp/web", "--", "--hostname", "0.0.0.0"]
