FROM node:20-alpine
WORKDIR /app

# Copy package files (lockfile is optional)
COPY package.json ./
COPY package-lock.json* ./

# Use npm install (works even if no lockfile exists yet)
RUN npm install --no-audit --no-fund

# Copy the rest of the app
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1
EXPOSE 3000
CMD ["npm","run","dev"]
