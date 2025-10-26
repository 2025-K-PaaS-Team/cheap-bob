FROM node:20-alpine

WORKDIR /frontend

RUN corepack enable
RUN corepack prepare pnpm@latest --activate

COPY package.json pnpm-lock.yaml ./

RUN pnpm install

COPY entrypoint-dev.sh /frontend/
RUN chmod +x /frontend/entrypoint-dev.sh

COPY . .

EXPOSE 5173

ENTRYPOINT ["/frontend/entrypoint-dev.sh"]