# Architecture Decision Record: Auth Migration (Firebase → Better Auth)

- **Status:** Proposed (Awaiting Review & Approval)
- **Phase:** Phase 1 (P1-1)
- **Document Path:** `docs/auth-design.md`
- **Target Framework:** Better Auth v1.1.x
- **Target Runtime:** NestJS 12 (API) + Next.js 16 App Router (Web) + Neon Serverless PostgreSQL

---

## 1. Context & Objectives

Lynvia currently uses Google Firebase Auth (Client SDK + Firebase Admin SDK v14) with a custom `FirebaseAuthGuard` that lazily upserts user records into PostgreSQL. Our Phase 0 audit ([`docs/audit-phase0.md`](./audit-phase0.md)) uncovered severe architectural liabilities:

1. **Account Takeover Vulnerability:** The legacy guard auto-upserted users by email without verifying `decoded.email_verified`. Any unverified identity provider account could hijack existing database users.
2. **Scattered Identity Source of Truth:** Identity data was split between Google's servers and our Postgres database, preventing atomic transactional onboarding, role enforcement, and relational consistency.
3. **Dead Session Proxy:** Next.js middleware checked for a non-existent `__firebase_session` cookie.

### Goals of Better Auth Migration:
- **Self-Hosted Identity:** Users, accounts, sessions, and verification tokens live directly in our Neon PostgreSQL database via Prisma ORM.
- **Strict Email Verification:** Zero app access without a confirmed email verification token.
- **Server-Controlled Roles:** The `role` column (`CLIENT`, `DESIGNER`, `ADMIN`) is strictly immutable from client input.
- **Safe Account Linking:** Zero automatic account linking unless the social identity provider guarantees email verification (e.g., Google OAuth).
- **Session Cookie Architecture:** Shared parent-domain cookies in production (`.lynvia.in`) and standards-compliant localhost credentials in local development.

---

## 2. Integration Architecture: Official Integration vs. Community Adapter

### Options Evaluated:

1. **Community Packages (e.g., `@thallesp/nestjs-better-auth`, `@buiducnhat/nest-better-auth`):**
   - *Pros:* Provides high-level NestJS dynamic modules and wrapper decorators out of the box.
   - *Cons:* Community packages lag weeks or months behind Better Auth core updates and schema generators; they obscure request lifecycle ordering; and they create abstraction leakage around body-parsers and error handlers.
2. **Official Integration (`better-auth/node` + `toNodeHandler`):**
   - *Pros:* Direct maintenance by Better Auth core team; zero version lag; direct control over Express request stream lifecycle; full access to the typed server API (`auth.api.getSession`); native Prisma adapter compatibility.
   - *Cons:* Requires explicit mounting in NestJS bootstrap.

### Decision: Official Integration via `toNodeHandler`
We select the **official Better Auth integration** using `toNodeHandler(auth.handler)` directly on the underlying HTTP platform (Express). It gives us complete control over raw body handling, cookie emission, and guard validation without third-party wrapper lag.

---

## 3. NestJS Mounting & Raw Body Stream Handling

### The Body-Parser Conflict
By default, NestJS initializes with `bodyParser: true` in `NestFactory.create()`. Express's internal `body-parser` middleware reads and consumes the incoming Node.js request stream (`req`), parsing it into `req.body`. When Better Auth's handler receives the request downstream, it attempts to read the raw request stream to process OAuth callbacks, webhooks, and credential payloads. Because the stream was already drained, requests fail with `ERR_STREAM_PREMATURE_CLOSE`, empty bodies, or indefinite hanging.

### Architectural Solution
We disable NestJS's global body parser during bootstrap and mount Better Auth's handler on the underlying Express instance *before* body parsing middleware is registered for other API routes:

```typescript
// api/src/main.ts
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { toNodeHandler } from 'better-auth/node';
import { auth } from './auth/auth';
import express from 'express';

async function bootstrap() {
  // 1. Disable NestJS global body parser to preserve raw stream for Better Auth
  const app = await NestFactory.create(AppModule, { bodyParser: false });

  const expressApp = app.getHttpAdapter().getInstance();

  // 2. Mount Better Auth catch-all route BEFORE body parsers
  // Handles /api/auth/sign-in, /api/auth/sign-up, /api/auth/callback/*, etc.
  expressApp.all('/api/auth/*', toNodeHandler(auth));

  // 3. Re-enable JSON and URL-encoded body parsing for standard NestJS routes
  expressApp.use(express.json());
  expressApp.use(express.urlencoded({ extended: true }));

  // 4. Configure CORS, Helmet, Throttling, and ValidationPipes
  // ...
  await app.listen(process.env.PORT ?? 3001);
}
```

---

## 4. Database Schema: Added Tables & Relations

Better Auth requires four core tables managed via Prisma (`@prisma/client` + `better-auth/adapters/prisma`):

```mermaid
erDiagram
    User ||--o{ Session : "has many"
    User ||--o{ Account : "has many"
    User ||--o| ClientProfile : "has one"
    User ||--o| DesignerProfile : "has one"
    Verification ||--|| Verification : "standalone tokens"

    User {
        string id PK
        string name
        string email UK
        boolean emailVerified
        string image
        Role role "CLIENT | DESIGNER | ADMIN (non-client-settable)"
        boolean onboardingComplete
        datetime createdAt
        datetime updatedAt
    }

    Session {
        string id PK
        string userId FK
        string token UK
        datetime expiresAt
        string ipAddress
        string userAgent
        datetime createdAt
        datetime updatedAt
    }

    Account {
        string id PK
        string userId FK
        string accountId
        string providerId
        string accessToken
        string refreshToken
        string idToken
        datetime accessTokenExpiresAt
        datetime refreshTokenExpiresAt
        string scope
        string password "Hashed securely (scrypt/argon2)"
        datetime createdAt
        datetime updatedAt
    }

    Verification {
        string id PK
        string identifier "Email address or phone"
        string value "Hashed token"
        datetime expiresAt
        datetime createdAt
        datetime updatedAt
    }
```

### Connection Strategy (Neon Serverless PostgreSQL):
- **Runtime API (`DATABASE_URL`):** Connects via Neon Connection Pooler (`*-pooler.*.neon.tech`) using transaction-pooling mode with `sslmode=require`.
- **Prisma Migrations (`DIRECT_URL`):** Connects directly to the compute endpoint (unpooled) because Prisma migrations require direct session-level advisory locking and schema inspection that connection poolers reject.

---

## 5. Non-Client-Settable Role Field Configuration

To eliminate privilege escalation, user roles must never be settable or mutable via client payloads. Better Auth provides the `input: false` option under `user.additionalFields`:

```typescript
// api/src/auth/auth.ts
import { betterAuth } from 'better-auth';
import { prismaAdapter } from 'better-auth/adapters/prisma';
import { PrismaClient, Role } from '@prisma/client';

const prisma = new PrismaClient();

export const auth = betterAuth({
  database: prismaAdapter(prisma, {
    provider: 'postgresql',
  }),
  user: {
    additionalFields: {
      role: {
        type: 'string',
        required: false,
        defaultValue: 'CLIENT',
        input: false, // CRITICAL: Rejects any client-supplied 'role' in sign-up or profile update payloads
        returned: true, // Included in getSession() responses
      },
      onboardingComplete: {
        type: 'boolean',
        required: false,
        defaultValue: false,
        input: false, // Only mutable via server-side /auth/onboard endpoint
        returned: true,
      },
    },
  },
  // ...
});
```

### Role State Lifecycle:
1. **Sign-up:** User created with `role: null` (or default unprivileged `CLIENT`) and `onboardingComplete: false`.
2. **Onboarding:** User calls `POST /api/auth/onboard`. A transactional NestJS service method verifies `onboardingComplete === false`, sets `role` to either `CLIENT` or `DESIGNER` (never `ADMIN`), creates the corresponding `ClientProfile` or `DesignerProfile`, and sets `onboardingComplete: true`.
3. **ADMIN Role:** Only granted via manual database operations or an administrative seed script (`npm run seed:admin`), never through public endpoints.

---

## 6. Email Verification & Account Linking Rules

### Email Verification Enforcement:
- Email/password authentication has `requireEmailVerification: true` enabled.
- On registration, Better Auth creates a hashed token in `verification` and invokes `sendVerificationEmail`.
- A custom `SessionAuthGuard` in NestJS verifies:
  1. Valid session token in cookie/header.
  2. `session.user.emailVerified === true`.
  - If unverified, the guard returns HTTP `403 Forbidden` (`code: 'EMAIL_NOT_VERIFIED'`).

### Account Linking Security Rules:
- **Default Implicit Linking:** By default, Better Auth links accounts with matching emails *only if* the incoming OAuth provider returns `email_verified: true`.
- **Trusted Providers:** We restrict `trustedProviders` strictly to Google OAuth (`['google']`).
- **Unverified Social Providers:** Any provider that does not verify emails is forbidden from auto-linking to prevent account takeover. Users must explicitly link additional accounts from an authenticated settings session.

```typescript
account: {
  accountLinking: {
    enabled: true,
    trustedProviders: ['google'],
  },
},
```

---

## 7. Session Strategy, Cookies, and CORS

| Setting | Local Development (`localhost`) | Production (`lynvia.in`) |
|---|---|---|
| **Frontend Origin** | `http://localhost:3000` | `https://lynvia.in`, `https://www.lynvia.in` |
| **API Origin** | `http://localhost:3001` | `https://api.lynvia.in` |
| **Cookie Domain** | `undefined` *(unset)* | `.lynvia.in` *(shared across subdomains)* |
| **Cookie `SameSite`** | `'lax'` | `'lax'` |
| **Cookie `Secure`** | `false` | `true` |
| **Cookie `HttpOnly`** | `true` | `true` |
| **CORS `credentials`** | `true` | `true` |
| **CORS `allowedHeaders`** | `['Content-Type', 'Authorization', 'Cookie']` | `['Content-Type', 'Authorization', 'Cookie']` |

> [!IMPORTANT]
> **RFC 6265 Browser Cookie Constraint:** Browsers strictly reject cookies set with `Domain=localhost`. In local development, the cookie domain must remain `undefined` so that the browser sets a host-only cookie for `localhost`. In production, setting `domain: '.lynvia.in'` permits `api.lynvia.in` to drop session cookies readable by `lynvia.in`.

---

## 8. Next.js Frontend Client Integration

### Client Setup (`web/src/lib/auth-client.ts`):
```typescript
import { createAuthClient } from 'better-auth/react';

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL + '/auth', // http://localhost:3001/api/auth
  fetchOptions: {
    credentials: 'include', // Required to attach session cookies across origins
  },
});

export const { signIn, signUp, useSession, signOut } = authClient;
```

### Lightweight Edge Proxy (`web/src/proxy.ts`):
Next.js middleware cannot perform heavy database queries. `proxy.ts` performs a fast, zero-query check for the `better-auth.session_token` cookie:
- Unauthenticated users attempting to access `/dashboard/*` are redirected to `/sign-in`.
- Signed-in users attempting to access `/sign-in` or `/sign-up` are redirected to `/dashboard`.
- Full authorization and role checks remain strictly enforced on the NestJS API.

---

## 9. Transactional Email & Resend DNS Specification

### Sending Domain Recommendation:
- **Recommended Domain:** Dedicated sending subdomain: **`mail.lynvia.in`** (or `send.lynvia.in`).
- **Rationale:**
  1. **Reputation Isolation:** Isolates transactional email reputation from root domain and marketing communications.
  2. **RFC 7208 Compliance:** RFC 7208 forbids multiple SPF records on a single host. Using `mail.lynvia.in` prevents conflicting with existing root domain SPF records (e.g. Google Workspace or Microsoft 365).

### DNS Record Protocol:
- **Do NOT manually construct or guess DNS records.**
- Add `mail.lynvia.in` in the [Resend Domains Dashboard](https://resend.com/domains).
- Copy the exact values provided by Resend into your DNS provider (Cloudflare, Namecheap, Route53):

| Record Type | Host / Name | Target / Value | Priority | Purpose |
|---|---|---|---|---|
| **TXT** | `mail.lynvia.in` | *(Exact SPF string from Resend dashboard)* | — | SPF authorization |
| **CNAME** | `resend._domainkey.mail.lynvia.in` | *(Exact DKIM target from Resend dashboard)* | — | DKIM cryptographic signing |
| **MX** | `mail.lynvia.in` | `feedback-smtp.us-east-1.amazonses.com` | 10 | Return-Path / Bounce handling |
| **TXT** | `_dmarc.mail.lynvia.in` | `v=DMARC1; p=none; rua=mailto:dmarc@lynvia.in` | — | DMARC policy |

---

## 10. Test Database Plan: Real PostgreSQL vs. Mock

### Core Policy:
- **Unit Tests (`api/test/prisma-mock.ts`):** Strictly reserved for pure unit tests (DTO transformation, input sanitization, helper functions, namespace prefix validation). Mocks execute in milliseconds.
- **Integration Tests:** **MUST execute against a REAL PostgreSQL database.** Mocks cannot simulate database-level transactions, `SERIALIZABLE` isolation, row-level locks (`SELECT FOR UPDATE`), or database-enforced partial unique indexes (`accepted_proposal_per_project`).

### Two-Tier Real Postgres Test Strategy:

#### 1. Local Developer Environment (Docker / Testcontainers)
- A local PostgreSQL 16 container running on an isolated test port (`5433`):
  ```bash
  docker run -d --name lynvia-test-pg -p 5433:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=lynvia_test postgres:16-alpine
  ```
- Before running integration suites:
  ```bash
  DATABASE_URL="postgresql://postgres:postgres@localhost:5433/lynvia_test" npx prisma migrate deploy
  ```
- Tests run with Vitest integration configuration (`vitest.config.integration.ts`).

#### 2. CI Pipeline (Neon Ephemeral Test Branch)
- In GitHub Actions CI, integration tests leverage Neon's instant copy-on-write branching:
  1. Create ephemeral test branch: `neonctl branches create --name test-$GITHUB_RUN_ID`
  2. Deploy migrations: `DATABASE_URL=$NEON_BRANCH_URL npx prisma migrate deploy`
  3. Execute integration tests: Concurrency tests for `acceptProposal` simulating parallel acceptance requests to verify partial unique index enforcement and transaction locking.
  4. Tear down branch: `neonctl branches delete test-$GITHUB_RUN_ID`

---

## 11. Citations & References

The architectural decisions in this document were formulated following Better Auth v1.1.x official documentation:
1. **Node & Express Integration (`toNodeHandler`):** [Better Auth Node Guide](https://www.better-auth.com/docs/integrations/node)
2. **Prisma Database Adapter:** [Better Auth Prisma Adapter](https://www.better-auth.com/docs/concepts/adapters/prisma)
3. **User Additional Fields & `input: false`:** [Better Auth Extending Users](https://www.better-auth.com/docs/concepts/users)
4. **Email & Password Authentication:** [Better Auth Email/Password](https://www.better-auth.com/docs/authentication/email-password)
5. **Account Linking & Trusted Providers:** [Better Auth Account Linking](https://www.better-auth.com/docs/concepts/account-linking)
6. **Cookie Configuration & Subdomains:** [Better Auth Cookies](https://www.better-auth.com/docs/concepts/cookies)
7. **React Client Integration:** [Better Auth Client SDK](https://www.better-auth.com/docs/integrations/react)
