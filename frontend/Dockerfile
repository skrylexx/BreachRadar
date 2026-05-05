# ─── Frontend Next.js — Dockerfile ──────────────────────────────────────────
# Build multi-étapes : builder + runner léger

FROM node:20-alpine AS base

# ─── Étape 1 : Installation des dépendances ───────────────────────────────────
FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
# Si un package-lock.json est présent, on utilise npm ci (reproductible)
# Sinon, on fallback sur npm install pour éviter d'échouer au build
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# ─── Étape 2 : Build de l'application ────────────────────────────────────────
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# S'assurer que le dossier public existe (même vide) pour la copie dans le runner
RUN mkdir -p public

ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_TELEMETRY_DISABLED=1

RUN npm run build

# ─── Étape 3 : Runner de production ──────────────────────────────────────────
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Utilisateur non-root
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
