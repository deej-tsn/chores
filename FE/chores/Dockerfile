# --- Stage 1: Build the Vite app ---
FROM node:24-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build


# --- Stage 2: Serve with Nginx ---
FROM nginx:stable-alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Replace default Nginx config to support React Router (SPA routing)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]