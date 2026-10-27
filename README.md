# Lynvia — India-first Creative Services Marketplace

Lynvia is an India-first curated creative-services marketplace connecting verified clients with India's best vetted graphic and brand designers.

For an in-depth architectural breakdown and tech stack details, see [TECH_STACK.md](file:///d:/LYNNNN/TECH_STACK.md). For the master execution plan, see [ANTIGRAVITY_MASTER_PROMPT.md](file:///d:/LYNNNN/ANTIGRAVITY_MASTER_PROMPT.md). For the Phase 0 audit findings, see [docs/audit-phase0.md](file:///d:/LYNNNN/docs/audit-phase0.md).

---

## Monorepo Structure

```
lynvia/
├── api/                  # NestJS REST API (TypeScript + Prisma + PostgreSQL)
│   ├── prisma/           # Prisma schema & migration history
│   ├── src/              # Application modules, guards, decorators, services
│   └── test/             # Test setup & specs
├── web/                  # Next.js 16 Web Application (App Router + React 19 + Tailwind CSS)
│   └── src/              # App router pages, UI components, client libraries
├── docs/                 # Audit reports & architecture decision records
├── .github/workflows/    # GitHub Actions CI pipelines
├── package.json          # Workspace root (orchestrates api and web)
└── .gitignore            # Monorepo-wide secrets & artifact exclusions
```

---

## Tech Stack Summary

- **Backend:** [NestJS 12](https://nestjs.com/) + TypeScript + [Prisma ORM](https://www.prisma.io/) + [Neon Serverless PostgreSQL](https://neon.tech/)
- **Frontend:** [Next.js 16](https://nextjs.org/) (App Router + Turbopack) + React 19 + [Tailwind CSS v4](https://tailwindcss.com/)
- **Authentication:** [Google Firebase Auth](https://firebase.google.com/products/auth) (Client SDK + Firebase Admin SDK v14) with Google OAuth and Email/Password *(transitioning to self-hosted Better Auth in Phase 1)*
- **Object Storage:** [Amazon S3](https://aws.amazon.com/s3/) with private, short-lived pre-signed URLs *(transitioning to Backblaze B2 in Phase 2)*
- **Security:** Global rate limiting (100 req/min/IP), Helmet security headers, strict CORS origin allowlist, and class-validator DTOs with whitelist/forbidNonWhitelisted validation

---

## Getting Started

### Prerequisites

- **Node.js:** v20.x or higher
- **npm:** v10.x or higher
- **PostgreSQL Database:** Neon Serverless Postgres instance (or local PostgreSQL 16+)
- **Cloud Storage:** S3-compatible bucket (AWS S3 / Backblaze B2)
- **Auth Credentials:** Firebase project (or local mock for testing)

### Environment Configuration

1. **API Environment (`api/.env`):**
   ```bash
   cp api/.env.example api/.env
   ```
   Fill in your `DATABASE_URL`, Firebase Admin credentials, AWS S3 keys, and `FRONTEND_URL`.

2. **Web Environment (`web/.env.local`):**
   ```bash
   cp web/.env.example web/.env.local
   ```
   Fill in your Firebase web client configuration and `NEXT_PUBLIC_API_URL` (`http://localhost:3001/api`).

### Database Setup

Run database migrations and generate the Prisma Client from the monorepo root:

```bash
# Generate Prisma Client
npm run db:generate

# Apply database migrations
npm run db:migrate

# (Optional) Launch Prisma Studio GUI
npm run db:studio
```

---

## Development Scripts

All scripts are cross-platform and run seamlessly on Windows (PowerShell), macOS, and Linux:

| Command | Description |
|---|---|
| `npm run dev:api` | Starts the NestJS API server in watch mode (`http://localhost:3001/api`) |
| `npm run dev:web` | Starts the Next.js frontend in development mode (`http://localhost:3000`) |
| `npm run build` | Builds both `api` and `web` projects for production |
| `npm run build:api` | Builds the NestJS API bundle |
| `npm run build:web` | Builds the Next.js web application |
| `npm run lint` | Runs ESLint across both workspaces |
| `npm run lint:api` | Lints the `api` workspace |
| `npm run lint:web` | Lints the `web` workspace |
| `npm test` | Runs the test suites across all workspaces |
| `npm run test:api` | Runs Vitest unit & integration tests in `api` |
| `npm run db:migrate` | Deploys pending Prisma database migrations |
| `npm run db:generate` | Regenerates Prisma Client types |
| `npm run db:studio` | Launches Prisma Studio visual database inspector |

---

## Key Invariants & Security Architecture

1. **Integer-Paise Monetary Values:** All financial figures (`budgetPaise`, `bidPaise`, `amountPaise`) are strictly stored as integer paise (never float) to prevent rounding errors and financial discrepancies.
2. **Server-Enforced Roles:** User roles (`CLIENT`, `DESIGNER`, `ADMIN`) are strictly sourced from the database on every authenticated request. Roles are never accepted from client input.
3. **Admin Privilege Protection:** The `ADMIN` role can never be self-assigned or acquired during onboarding; it must be provisioned via database seed scripts or manual administrative action.
4. **Proposal Isolation & IDOR Protection:** Designers can only inspect their own submitted bids on open projects. Competing designer proposals and bids remain strictly confidential until acceptance.
5. **Private Object Storage:** S3 buckets reject public read access. All file uploads and previews use short-lived, pre-signed URLs generated server-side after verifying authorization.
