# Architecture Decision Record: Auth Migration (Firebase → Better Auth) — v2

- **Status:** Proposed (v2 — Revised per Review, Awaiting Approval)
- **Phase:** Phase 1 (P1-1)
- **Document Path:** `docs/auth-design.md`
- **Pinned Version:** `better-auth@1.7.14` (Latest Stable on npm; v1.8 is in beta `1.8.0-beta.3`)
- **Adapter Import:** `better-auth/adapters/prisma` (Official export built into `better-auth`)
- **Target Runtime:** NestJS 12 + Express 5 (API) + Next.js 16 App Router (Web) + Neon Serverless PostgreSQL + Node.js 22 LTS

---

## 1. Context & Objectives

Lynvia currently uses Google Firebase Auth (Client SDK + Firebase Admin SDK v14) with a custom `FirebaseAuthGuard` that lazily upserts user records into PostgreSQL. Our Phase 0 audit ([`docs/audit-phase0.md`](./audit-phase0.md)) uncovered severe architectural liabilities:

1. **Account Takeover Vulnerability:** The legacy guard auto-upserted users by email without verifying `decoded.email_verified`. Any unverified identity provider account could hijack existing database users.
2. **Scattered Identity Source of Truth:** Identity data was split between Google's servers and our Postgres database, preventing atomic transactional onboarding, role enforcement, and relational consistency.
3. **Dead Session Proxy:** Next.js middleware checked for a non-existent `__firebase_session` cookie.

### Goals of Better Auth Migration:
- **Self-Hosted Identity:** Users, accounts, sessions, and verification tokens live directly in our Neon PostgreSQL database via Prisma ORM.
- **Strict Email Verification:** Zero application access without confirmed email verification (`emailVerified === true`).
- **Server-Controlled Roles:** The `role` column (`CLIENT`, `DESIGNER`, `ADMIN`) is nullable upon registration, immutable from client input (`input: false`), and assigned strictly via a dedicated onboarding endpoint.
- **Pre-Account Takeover Defense:** Explicit verification and linking rules preventing attackers from pre-registering a victim's email.
- **Session Cookie Architecture:** Shared parent-domain cookies in production (`.lynvia.in`) with `__Secure-` prefixing, and standards-compliant localhost credentials in local development.
- **Single Connection Pool:** Shared `PrismaClient` instance between NestJS and Better Auth to prevent database connection exhaustion.

---

## 2. ESM/CJS Runtime Analysis & Package Selection

### 2.1 The ESM/CJS Dilemma
- `better-auth@1.7.14` is distributed **exclusively as ECMAScript Modules (ESM)**. Its `package.json` exports `.mjs` entrypoints (`./dist/index.mjs`) and `.d.mts` type declarations. It does **not** ship CommonJS (`.cjs`) builds.
- NestJS projects conventionally compile TypeScript to CommonJS (`"module": "commonjs"`, `"target": "ES2021"`).
- In TypeScript, when `"module": "commonjs"`, even dynamic `await import('better-auth')` is transpiled into `Promise.resolve().then(() => require('better-auth'))`.
- In Node.js versions <= 20.x, executing `require()` on an ESM-only package throws `ERR_REQUIRE_ESM`.

### 2.2 Spike Results & Proof of Concept (Branch: `spike/better-auth-esm`)
We executed an isolated spike compiling and executing `better-auth@1.7.14` inside our `api` build:
1. **Node.js 22 LTS Synchronous `require(esm)`:**
   Node.js v22.12.0+ (and Node.js 23+) natively enables synchronous `require(esm)` by default for ES modules that do not contain top-level `await`.
2. **Better Auth Execution:**
   `better-auth` contains **no top-level `await`**. When compiled by NestJS/TypeScript (`"module": "commonjs"`), Node.js v22.12.0+ and Node.js v25+ load `require("better-auth")` synchronously, initialize the handler, and bind the Prisma adapter without error (`Better Auth initialized successfully: function`).
3. **Node.js <= 20 Incompatibility:**
   Running on Node 20.x without `--experimental-require-module` fails immediately with `ERR_REQUIRE_ESM`.

### 2.3 Architectural Decision: Node 22 LTS + Official Core Integration
We evaluated two integration paths:

1. **Community Wrapper Packages (e.g., `@lygos/nestjs-better-auth`):**
   - *Audit:* Published by an external cryptocurrency startup (`lygos.finance`, v2.0.8, last updated Dec 2025). It introduces an unvetted third-party supply-chain dependency, lags behind Better Auth core releases, and obscures request lifecycle order.
2. **Official Core Integration (`better-auth` + `toNodeHandler`):**
   - *Audit:* Maintained directly by the Better Auth core team. Zero version lag. Full control over the Express HTTP pipeline and raw request stream. Direct typed API (`auth.api.*`).

**Decision:** We select the **official Better Auth core package (`better-auth@1.7.14`)** and standardize the monorepo runtime on **Node.js 22 LTS (Active LTS, >=22.12.0)**:
- Monorepo `package.json` engines enforced: `"node": ">=22.12.0"`.
- GitHub Actions CI workflow updated to `node-version: 22`.
- Production container / Railway / Fly runners standardized on Node.js 22 LTS.
- This unlocks native synchronous `require(esm)` with zero runtime wrappers or hacks.

### 2.4 Adapter Import Resolution
In Better Auth v1.x, the Prisma adapter is exported directly from the primary package:
```typescript
import { prismaAdapter } from 'better-auth/adapters/prisma';
```
While `@better-auth/prisma-adapter@1.7.14` exists on npm, it is a thin re-export of `better-auth/adapters/prisma`. Using the built-in subpath import eliminates a redundant dependency.

---

## 3. Express 5 Mounting, Middleware Pipeline & Route Collision Prevention

### 3.1 Express 5 Wildcard Splat Path
Our API workspace uses NestJS 12 over Express 5 (`@nestjs/platform-express` with `"express": "5.3.0"` and `"path-to-regexp": "8.4.2"`).
In Express 5 / `path-to-regexp` v8+, bare wildcards like `/api/auth/*` are invalid and throw syntax exceptions.
**Required Path:** The Better Auth catch-all must be mounted using a named splat parameter:
```typescript
expressApp.all('/api/auth/*splat', toNodeHandler(auth));
```

### 3.2 Strict Middleware Pipeline Order
Mounting Better Auth before NestJS creates a critical security risk if Express-level middleware is omitted: requests to `/api/auth/*` would bypass security headers (Helmet), CORS, and reverse-proxy IP trust.

The application bootstrap must follow this strict sequential pipeline:

```
[Incoming Request]
       │
       ▼
1. expressApp.set('trust proxy', 1) ────────── Reverse proxy IP / Protocol resolution
       │
       ▼
2. expressApp.use(helmet(...)) ─────────────── Security headers on ALL routes
       │
       ▼
3. expressApp.use(cors(...)) ───────────────── CORS headers & preflight on ALL routes
       │
       ▼
4. expressApp.all('/api/auth/*splat', ──────── Better Auth (reads raw body stream)
     toNodeHandler(auth))                      [STOPS HERE for /api/auth/*]
       │
       ▼ (All non-auth routes continue)
5. expressApp.use(express.json()) ──────────── Body parsing for NestJS
   expressApp.use(express.urlencoded())
       │
       ▼
6. NestJS Application Pipeline ─────────────── ValidationPipes, Guards, Controllers
```

#### Bootstrap Implementation:
```typescript
// api/src/main.ts
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { toNodeHandler } from 'better-auth/node';
import { getAuthInstance } from './auth/auth';
import { PrismaService } from './prisma/prisma.service';
import express from 'express';
import helmet from 'helmet';
import cors from 'cors';

async function bootstrap() {
  // 1. Disable NestJS automatic body parser to preserve raw stream for Better Auth
  const app = await NestFactory.create(AppModule, { bodyParser: false });
  const expressApp = app.getHttpAdapter().getInstance();

  // 2. Trust reverse proxy (Railway, Fly.io, Vercel)
  expressApp.set('trust proxy', 1);

  // 3. Global Express-level Security Headers (applies to /api/auth/*splat and Nest routes)
  expressApp.use(
    helmet({
      crossOriginResourcePolicy: { policy: 'same-site' },
      contentSecurityPolicy: process.env.NODE_ENV === 'production' ? undefined : false,
    }),
  );

  // 4. Global Express-level CORS
  const allowedOrigins = [
    process.env.FRONTEND_URL ?? 'http://localhost:3000',
    'https://lynvia.in',
    'https://www.lynvia.in',
  ];
  expressApp.use(
    cors({
      origin: (origin, callback) => {
        if (!origin || allowedOrigins.includes(origin)) {
          callback(null, true);
        } else {
          callback(new Error('Blocked by CORS'));
        }
      },
      credentials: true,
      allowedHeaders: ['Content-Type', 'Authorization', 'Cookie'],
      methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    }),
  );

  // 5. Mount Better Auth with shared PrismaService BEFORE body parsers
  const prismaService = app.get(PrismaService);
  const auth = getAuthInstance(prismaService);
  expressApp.all('/api/auth/*splat', toNodeHandler(auth));

  // 6. Attach body parsers for all remaining NestJS routes
  expressApp.use(express.json({ limit: '10mb' }));
  expressApp.use(express.urlencoded({ extended: true, limit: '10mb' }));

  await app.listen(process.env.PORT ?? 3001);
}
```

### 3.3 Persistent Rate Limiting
Better Auth’s built-in rate limiter must **never** use in-memory storage, which resets across server restarts and does not scale horizontally.
We configure `rateLimit` backed by persistent storage (PostgreSQL table `rateLimit` or Redis):
- **Sign-In (`/sign-in/email`):** 5 attempts per 60 seconds per IP/email.
- **Sign-Up (`/sign-up/email`):** 3 attempts per 60 seconds per IP.
- **Password Reset (`/forget-password`):** 3 requests per 60 seconds.
- **Verification Resend (`/send-verification-email`):** 2 requests per 60 seconds.

### 3.4 Route Collision Audit
Because `/api/auth/*splat` consumes all requests prefixed with `/api/auth/`, **no custom NestJS controller may mount under `/api/auth/`**. Any custom route placed under `/api/auth/` (such as the legacy `POST /api/auth/onboard`) is swallowed by Better Auth and rejected with `404 Unknown Action`.

#### Route Allocation:
| Endpoint | Controller / Module | Handled By | Purpose |
|---|---|---|---|
| `/api/auth/*splat` | Express Mount | Better Auth | Sign-in, sign-up, sign-out, OAuth callbacks, email verify |
| `POST /api/onboarding` | `OnboardingController` | NestJS | Assign role (`CLIENT`/`DESIGNER`), create profile, complete onboarding |
| `GET /api/users/me` | `UsersController` | NestJS | Retrieve authenticated user profile and session state |
| `GET /api/designers` | `DesignersController` | NestJS | Public directory of vetted designers |
| `POST /api/projects` | `ProjectsController` | NestJS | Client project creation |
| `POST /api/proposals` | `ProposalsController` | NestJS | Designer proposal submission |
| `GET /api/health` | `AppController` | NestJS | Liveness and database connectivity probe |

---

## 4. Database Schema: Tables, Shared PrismaClient & ID Strategy

### 4.1 Shared PrismaClient Instance (Single Connection Pool)
Creating `const prisma = new PrismaClient()` inside `auth.ts` would spawn a second connection pool, rapidly exhausting Neon’s transaction pool limit.
Instead, Better Auth is instantiated via a factory function `getAuthInstance(prisma: PrismaService)` that receives NestJS’s existing `PrismaService` singleton. Both NestJS and Better Auth share **one connection pool**.

### 4.2 ID Strategy & Foreign Key Mapping
- Better Auth creates text-based identifiers (cuid/nanoid/UUID strings) for `user.id`, `session.id`, `account.id`, and `verification.id`.
- Our existing Prisma schema defines `User.id` as `String @id @default(cuid())`.
- This maps seamlessly: Better Auth generates the `id` string on record creation; all foreign keys across `ClientProfile.userId`, `DesignerProfile.userId`, `Project.clientId`, and `Proposal.designerId` reference `User.id String`.

### 4.3 Prisma Schema Models
Better Auth requires four core models:

```prisma
// api/prisma/schema.prisma

model User {
  id                 String           @id @default(cuid())
  name               String
  email              String           @unique
  emailVerified      Boolean          @default(false) @map("email_verified")
  image              String?
  role               Role?            // Nullable until onboarding; non-client-settable
  onboardingComplete Boolean          @default(false) @map("onboarding_complete")
  createdAt          DateTime         @default(now()) @map("created_at")
  updatedAt          DateTime         @updatedAt @map("updated_at")

  sessions           Session[]
  accounts           Account[]
  clientProfile      ClientProfile?
  designerProfile    DesignerProfile?
  projectsAsClient   Project[]        @relation("ClientProjects")
  proposals          Proposal[]

  @@map("user")
}

model Session {
  id        String   @id @default(cuid())
  userId    String   @map("user_id")
  token     String   @unique
  expiresAt DateTime @map("expires_at")
  ipAddress String?  @map("ip_address")
  userAgent String?  @map("user_agent")
  createdAt DateTime @default(now()) @map("created_at")
  updatedAt DateTime @updatedAt @map("updated_at")

  user      User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId])
  @@map("session")
}

model Account {
  id                    String    @id @default(cuid())
  userId                String    @map("user_id")
  accountId             String    @map("account_id")
  providerId            String    @map("provider_id")
  accessToken           String?   @map("access_token")
  refreshToken          String?   @map("refresh_token")
  idToken               String?   @map("id_token")
  accessTokenExpiresAt  DateTime? @map("access_token_expires_at")
  refreshTokenExpiresAt DateTime? @map("refresh_token_expires_at")
  scope                 String?
  password              String?   // Hashed password for email provider
  createdAt             DateTime  @default(now()) @map("created_at")
  updatedAt             DateTime  @updatedAt @map("updated_at")

  user                  User      @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([providerId, accountId])
  @@index([userId])
  @@map("account")
}

model Verification {
  id         String   @id @default(cuid())
  identifier String
  value      String
  expiresAt  DateTime @map("expires_at")
  createdAt  DateTime @default(now()) @map("created_at")
  updatedAt  DateTime @updatedAt @map("updated_at")

  @@unique([identifier, value])
  @@map("verification")
}
```

---

## 5. Non-Client-Settable Role & Onboarding State Machine

### 5.1 Role Security Policy
- **No Default Privileges:** User is created with `role: null` and `onboardingComplete: false`.
- **`input: false` Enforcement:** Configured via `user.additionalFields` in Better Auth. The library strips `role` and `onboardingComplete` from all client sign-up and update payloads.
- **Server-Side Assignment Only:** Role is assigned exclusively by `POST /api/onboarding`. Users may select `CLIENT` or `DESIGNER`. Any attempt to request `ADMIN` is rejected.
- **Admin Assignment:** `ADMIN` role is granted solely via seed scripts (`npm run seed:admin`) or manual database intervention.

### 5.2 Better Auth Server Configuration (`api/src/auth/auth.ts`)
```typescript
// api/src/auth/auth.ts
import { betterAuth } from 'better-auth';
import { prismaAdapter } from 'better-auth/adapters/prisma';
import { PrismaService } from '../prisma/prisma.service';

export function getAuthInstance(prisma: PrismaService) {
  const isProd = process.env.NODE_ENV === 'production';

  return betterAuth({
    database: prismaAdapter(prisma, {
      provider: 'postgresql',
    }),
    secret: process.env.BETTER_AUTH_SECRET,
    baseURL: process.env.BETTER_AUTH_URL, // e.g. https://api.lynvia.in or http://localhost:3001
    trustedOrigins: [
      process.env.FRONTEND_URL ?? 'http://localhost:3000',
      'https://lynvia.in',
      'https://www.lynvia.in',
    ],
    emailAndPassword: {
      enabled: true,
      requireEmailVerification: true,
      minPasswordLength: 8,
      maxPasswordLength: 128,
      revokeOtherSessionsOnPasswordReset: true, // Revokes attacker sessions on password reset
    },
    user: {
      additionalFields: {
        role: {
          type: 'string',
          required: false,
          defaultValue: null,
          input: false,    // Stripped from client requests
          returned: true,  // Present in session
        },
        onboardingComplete: {
          type: 'boolean',
          required: false,
          defaultValue: false,
          input: false,    // Stripped from client requests
          returned: true,
        },
      },
    },
    account: {
      accountLinking: {
        enabled: true,
        trustedProviders: ['google'], // Only link verified social identities
      },
    },
    advanced: {
      crossSubdomainCookies: {
        enabled: isProd,
        domain: isProd ? '.lynvia.in' : undefined, // RFC 6265 forbids Domain=localhost
      },
    },
    rateLimit: {
      enabled: true,
      storage: 'database',
      window: 60,
      max: 100,
      customRules: {
        '/sign-in/email': { window: 60, max: 5 },
        '/sign-up/email': { window: 60, max: 3 },
        '/forget-password': { window: 60, max: 3 },
        '/send-verification-email': { window: 60, max: 2 },
      },
    },
  });
}

export type Auth = ReturnType<typeof getAuthInstance>;
```

### 5.3 Guard Execution Logic (`SessionAuthGuard`)
The NestJS `SessionAuthGuard` enforces identity, verification, and onboarding:
1. Extracts session token from cookie (`__Secure-better-auth.session_token` in prod, `better-auth.session_token` in dev) or `Authorization: Bearer <token>`.
2. Validates session via `auth.api.getSession({ headers: req.headers })`.
3. Verifies `user.emailVerified === true`. Throws `403 Forbidden` (`EMAIL_NOT_VERIFIED`) if false.
4. If endpoint requires completed onboarding: verifies `user.role !== null && user.onboardingComplete === true`. Throws `403 Forbidden` (`ONBOARDING_INCOMPLETE`) if false.
5. If endpoint has `@Roles(Role.DESIGNER)`: verifies `user.role === 'DESIGNER'`. Throws `403 Forbidden` (`INSUFFICIENT_PERMISSIONS`) if false.

---

## 6. Pre-Account Takeover Defense & Test Specification

### 6.1 Attack Vector
1. **Unverified Registration:** Attacker signs up with `victim@example.com` and sets password `attackerPass123`. The attacker cannot verify the email (`emailVerified: false`).
2. **Legitimate OAuth Sign-In:** The true owner of `victim@example.com` visits Lynvia and signs in using Google OAuth. Google cryptographically confirms email ownership (`email_verified: true`).
3. **Takeover Threat:** If an authentication system silently links the unverified email/password account to the Google account without invalidating or isolating the attacker's unverified credentials, the attacker can later sign in with `attackerPass123` and access the victim's profile and data.

### 6.2 Better Auth Protection Mechanism
1. **Unverified Accounts Cannot Authenticate:** With `requireEmailVerification: true`, the attacker cannot establish a valid session or access protected routes using the unverified password credential.
2. **Account Linking Isolation:** When Google OAuth authenticates, Better Auth links the Google account because Google is declared in `trustedProviders`.
3. **Session Revocation:** On credential linking and password reset, `revokeOtherSessionsOnPasswordReset: true` ensures any dangling sessions are destroyed.
4. **Integration Test Requirement:** An automated integration test must execute this exact sequence:
   - Step A: Attacker registers `victim@example.com` with password.
   - Step B: Assert `user.emailVerified === false`; assert login attempt fails or session access is blocked.
   - Step C: Mock Google OAuth sign-in for `victim@example.com`.
   - Step D: Assert victim receives valid authenticated session with `emailVerified === true`.
   - Step E: Attacker attempts sign-in with `attackerPass123`. Assert attacker cannot access victim's session.

---

## 7. Cookie Architecture & Edge Proxy (`proxy.ts`)

### 7.1 Production vs. Development Cookies
Better Auth applies the `__Secure-` prefix under HTTPS environments:
- **Production (`https://*.lynvia.in`):**
  - Cookie Name: `__Secure-better-auth.session_token`
  - Domain: `.lynvia.in` (shared across `lynvia.in` and `api.lynvia.in`)
  - Flags: `HttpOnly; Secure; SameSite=Lax`
- **Development (`http://localhost:3000` / `localhost:3001`):**
  - Cookie Name: `better-auth.session_token`
  - Domain: `undefined` (unset per RFC 6265, which strictly forbids `Domain=localhost`)
  - Flags: `HttpOnly; SameSite=Lax`

### 7.2 Frontend Edge Proxy (`web/src/proxy.ts`)
Next.js middleware cannot make blocking database calls. It inspects session cookies for optimistic client routing:
```typescript
// web/src/proxy.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Better Auth prefixes cookies with __Secure- in production
  const isProd = process.env.NODE_ENV === 'production';
  const cookieName = isProd
    ? '__Secure-better-auth.session_token'
    : 'better-auth.session_token';

  const sessionToken = request.cookies.get(cookieName)?.value;
  const { pathname } = request.nextUrl;

  const isAuthRoute = pathname.startsWith('/sign-in') || pathname.startsWith('/sign-up');
  const isDashboardRoute = pathname.startsWith('/dashboard');

  if (!sessionToken && isDashboardRoute) {
    const signInUrl = new URL('/sign-in', request.url);
    signInUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(signInUrl);
  }

  if (sessionToken && isAuthRoute) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/sign-in', '/sign-up'],
};
```

---

## 8. Transactional Email & Resend DNS Specification

### 8.1 Sending Subdomain Policy
- **Recommended Domain:** Dedicated sending subdomain: **`mail.lynvia.in`** (or `notifications.lynvia.in`).
- **Rationale:**
  1. **RFC 7208 SPF Limit:** RFC 7208 §3.2 strictly forbids multiple SPF TXT records on a single domain. If `lynvia.in` uses Google Workspace or Microsoft 365, adding an SPF record for Resend invalidates both.
  2. **10-DNS-Lookup Ceiling:** Combining multiple mail services into a single root SPF record quickly exceeds the hard 10-lookup limit.
  3. **Reputation Blast Radius:** Using `mail.lynvia.in` isolates transactional notification reputation from primary corporate email inboxes.

### 8.2 DNS Record Protocol
- **Do NOT manually construct, guess, or invent DNS values.**
- Add `mail.lynvia.in` in the [Resend Dashboard](https://resend.com/domains).
- Copy the **exact** TXT (SPF), CNAME (DKIM), and MX records generated by Resend into your DNS provider (e.g., Cloudflare).

---

## 9. Test Database Plan: Real PostgreSQL vs. Unit Mocks

### 9.1 Testing Policy
- **Unit Tests (`api/test/prisma-mock.ts`):** Strictly reserved for unit tests of pure logic (DTO validation, string transforms, URL signers). Mocks run in milliseconds.
- **Integration Tests:** **MUST run against a REAL PostgreSQL database.** Mocks cannot test concurrency, transaction rollbacks, row-level locks (`SELECT FOR UPDATE`), or database constraints.

### 9.2 CI Integration Test Database: GitHub Actions Service Container
In CI, integration tests run against a native GitHub Actions PostgreSQL service container (avoiding Neon API rate limits, external network latency, and branch management overhead):

```yaml
# In .github/workflows/ci.yml
services:
  postgres:
    image: postgres:16-alpine
    env:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: lynvia_test
    ports:
      - 5433:5432
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
```

### 9.3 Partial Unique Index & Concurrency Test Target
Phase 2 concurrency tests for `acceptProposal` must execute against this container to verify:
1. `SELECT ... FOR UPDATE` row locks prevent double acceptance under race conditions.
2. The partial unique index **`proposals_one_accepted_per_project`**:
   ```sql
   CREATE UNIQUE INDEX "proposals_one_accepted_per_project" 
   ON "proposals"("project_id") 
   WHERE status = 'ACCEPTED';
   ```
   strictly throws error `P2002` (Unique constraint failed) if two concurrent transactions attempt to accept proposals for the same project.

---

## 10. Citations & References

The architectural decisions in this document were formulated following official documentation:
1. **Node.js & Express Integration (`toNodeHandler`):** [Better Auth Node Guide](https://www.better-auth.com/docs/integrations/node) (v1.7)
2. **Prisma Database Adapter:** [Better Auth Prisma Adapter](https://www.better-auth.com/docs/adapters/prisma) (v1.7)
3. **User Additional Fields & `input: false`:** [Better Auth Extending Users](https://www.better-auth.com/docs/concepts/users) (v1.7)
4. **Session Management & Cookies:** [Better Auth Sessions & Cookies](https://www.better-auth.com/docs/concepts/session-management) and [Better Auth Cookies](https://www.better-auth.com/docs/concepts/cookies) (v1.7)
5. **Rate Limiting & Persistent Storage:** [Better Auth Rate Limit Plugin](https://www.better-auth.com/docs/plugins/rate-limit) (v1.7)
6. **Email Verification:** [Better Auth Email Verification](https://www.better-auth.com/docs/plugins/email-verification) (v1.7)
7. **Node.js 22 `require(esm)` Specification:** [Node.js v22.12.0 Release Notes / PR #51977](https://nodejs.org/en/blog/release/v22.12.0)
