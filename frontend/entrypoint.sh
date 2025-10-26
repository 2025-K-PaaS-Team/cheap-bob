#!/bin/sh
set -e

export CI=true

echo "Starting frontend production server..."
echo "Environment variables loaded:"
echo "VITE_API_BASE_URL=${VITE_API_BASE_URL}"
echo "VITE_IS_DEV=${VITE_IS_DEV}"
echo "VITE_IS_LOCAL=${VITE_IS_LOCAL}"
echo "VITE_KAKAO_REST_API=${VITE_KAKAO_REST_API:+[SET]}"
echo "VITE_NAVER_MAP_CLIENT_ID=${VITE_NAVER_MAP_CLIENT_ID:+[SET]}"

echo "Installing dependencies..."
pnpm install --frozen-lockfile

echo "Starting Vite production server on port 5172..."
exec pnpm build --host 0.0.0.0 --port 5172