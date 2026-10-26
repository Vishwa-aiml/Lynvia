# Lynvia — India-first Creative Services Marketplace

## Monorepo Structure

```
lynvia/
├── apps/
│   ├── api/          # NestJS backend (Node.js + TypeScript)
│   └── web/          # Next.js frontend (App Router + TypeScript)
├── packages/         # Shared types, utilities (future)
├── package.json      # Workspace root
└── .gitignore
```

## Tech Stack
- **Backend:** NestJS + TypeScript + Prisma + PostgreSQL (Neon)
- **Frontend:** Next.js (App Router) + TypeScript + Tailwind CSS + shadcn/ui
- **Auth:** Clerk (JWT + Webhooks)
- **Storage:** Amazon S3 (ap-southeast-2)
- **ORM:** Prisma (migrations only, never hand-edit DB)

## Development

```bash
# API (from root)
npm run dev:api

# Web (from root)
npm run dev:web

# Database
npm run db:migrate   # Run migrations
npm run db:generate  # Generate Prisma client
npm run db:studio    # Open Prisma Studio
```

## Environment Setup
- Copy `apps/api/.env.example` → `apps/api/.env`
- Copy `apps/web/.env.example` → `apps/web/.env.local`

## Key Rules (do not bypass)
- Role is NEVER set from client input — only via `/auth/onboarding` endpoint
- All file URLs are signed S3 URLs (never public)
- All money is stored as integer paise (never float)
- Clerk webhook is the ONLY place a `users` row is created
- Admin role (`deepikshas@lynvia.in`) is set manually in DB only
