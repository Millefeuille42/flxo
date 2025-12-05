FROM node:22.20-slim AS builder

ENV NODE_ENV=production

WORKDIR /app
COPY . /app

RUN --mount=type=cache,target=/root/.cache/yarn \
    yarn install --immutable

RUN --mount=type=cache,target=/root/.cache/yarn \
    yarn build

FROM nginx:stable-alpine

COPY --from=builder --chown=app:app /app/dist /var/www/app
COPY nginx.conf /etc/nginx/nginx.conf
