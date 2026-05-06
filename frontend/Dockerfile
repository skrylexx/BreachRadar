# ─── Frontend Next.js — Dockerfile ──────────────────────────────────────────
# Build multi-étapes : builder + runner léger

FROM node:20-alpine AS base

# ─── Étape 1 : Installation des dépendances ───────────────────────────────────
FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
# npm install recrée le lock si besoin (dotenv-cli peut ne pas être dans le lock)
RUN npm install

# ─── Étape 2 : Build de l'application ────────────────────────────────────────
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# S'assurer que le dossier public existe (même vide) pour la copie dans le runner
RUN mkdir -p public

ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Domaine cible — seule variable à remplir dans le .env racine
ARG TARGET_DOMAIN=""
ENV TARGET_DOMAIN=$TARGET_DOMAIN

ENV NEXT_TELEMETRY_DISABLED=1

# Appel direct à next build : contourne dotenv-cli (inutile en Docker,
# les variables sont déjà injectées via ARG/ENV ci-dessus)
RUN ./node_modules/.bin/next build

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
