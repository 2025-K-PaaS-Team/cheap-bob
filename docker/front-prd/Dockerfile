FROM node:20-alpine

WORKDIR /frontend

RUN corepack enable
RUN corepack prepare pnpm@latest --activate

COPY package.json pnpm-lock.yaml ./

RUN pnpm install

COPY entrypoint.sh /frontend/
RUN chmod +x /frontend/entrypoint.sh

COPY . .

EXPOSE 5172

ENTRYPOINT ["/frontend/entrypoint.sh"]