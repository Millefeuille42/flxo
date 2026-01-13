FROM node:22.20-slim AS builder


ARG VITE_COMPANY_NAME
ARG VITE_APPLICATION_NAME
ARG VITE_BACKEND_URL

ENV VITE_COMPANY_NAME=$VITE_COMPANY_NAME
ENV VITE_APPLICATION_NAME=$VITE_APPLICATION_NAME
ENV VITE_BACKEND_URL=$VITE_BACKEND_URL
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
