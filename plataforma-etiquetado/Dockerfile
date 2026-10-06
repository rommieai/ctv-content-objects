FROM node:22-bookworm-slim AS web
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
RUN npm run check && npm run build

FROM node:22-bookworm-slim AS server
WORKDIR /app
COPY server/package.json server/package-lock.json ./
RUN npm ci
COPY server/ ./
RUN npm run build && npm prune --omit=dev

FROM node:22-bookworm-slim
ENV NODE_ENV=production PORT=3000 DB_PATH=/data/etiquetas.db PUBLIC_DIR=/app/public IAB_DIR=/app/iab
WORKDIR /app
COPY --from=server /app/package.json ./
COPY --from=server /app/node_modules ./node_modules
COPY --from=server /app/dist ./dist
COPY iab ./iab
COPY --from=web /web/dist ./public
EXPOSE 3000
CMD ["node", "dist/index.js"]
