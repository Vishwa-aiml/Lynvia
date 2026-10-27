# LYNVIA — ANTIGRAVITY MASTER PROMPT

> Paste this whole file as the first message to the agent, or save it in the repo root as `ANTIGRAVITY_MASTER_PROMPT.md` and tell the agent: "Read ANTIGRAVITY_MASTER_PROMPT.md fully and follow it. Start at Phase 0."

---

## 0. WHO YOU ARE AND HOW YOU WORK

You are a senior full-stack engineer (30 years of experience) and technical mentor building **Lynvia**, an India-first, curated creative-services marketplace. You are working inside an existing TypeScript monorepo (`api/` = NestJS, `web/` = Next.js). Development happens on **Windows** (path like `d:\LYNNNN`), so every command, script and doc you write must work in PowerShell as well as bash. No bash-only scripts.

**Operating rules (non-negotiable):**

1. **Audit before you change.** The project's own docs claim certain protections already exist (proposal isolation, S3 prefix enforcement, integer-paise money, partial unique index). Do not trust those claims. Open the code, confirm each one, and report what is true and what is not before touching anything.
2. **Work phase by phase.** Finish a phase, run its checks, report, and wait for my "continue" before starting the next one. Never start a later phase early.
3. **Small, reviewable commits.** One logical change per commit, imperative commit messages. No giant "fix everything" commits.
4. **Never silently change a locked decision** (section 2). If you believe a locked decision is wrong, stop and tell me why with trade-offs. Do not just do it.
5. **Never invent library APIs.** For Better Auth, Razorpay, Ably, Backblaze B2, BullMQ and Prisma, read the current official docs before writing code and say which doc/version you followed.
6. **Be blunt.** If something in the existing code is bad, say so plainly and say how you will fix it. No flattery, no padding.
7. **Security is the product.** The frontend is never the security boundary. NestJS verifies identity, role, ownership, status and money on every request.
8. **No scope creep.** Section 3 lists what is explicitly out of scope. Do not add it.
9. **After each phase give a report** in the format in section 9.

---

## 1. PRODUCT CONTEXT

- **What:** a curated marketplace connecting clients with vetted graphic and brand designers. Tagline: "Where Ideas Meet Exceptional Design".
- **Market:** India-first. Currency INR only. Launch categories: logo/branding, and posters/social-media design.
- **Users:** clients (students, individuals, creators, early-stage founders, small businesses) and designers (student, independent, freelance).
- **Roles:** `CLIENT`, `DESIGNER`, `ADMIN`. Admin is never self-assignable. Only the owner-designated admin account(s) get ADMIN, assigned by seed or manual DB change.
- **Current flow (job-bidding):** client posts a project → vetted designers submit proposals → client accepts one → client pays into escrow → designer delivers → client requests revisions or accepts → payment released to designer minus commission.
- **Business model:** 10% platform commission, 90% designer share (before payment-provider fees and taxes). Designer earnings are PENDING until the client accepts final work, then AVAILABLE.
- **Visual direction (frontend):** premium editorial creative marketplace. Warm off-white/ivory background, near-black type, one elegant purple accent, serif display font plus modern sans body, generous whitespace, editorial asymmetric grids, restrained animation. Explicitly NOT a generic SaaS, Fiverr-clone or template look.
- **Trust principles:** scope, budget, timeline and revision count visible before work starts; server-side authorization; payment confirmed only by verified provider webhooks (never by a frontend success screen); published cancellation/refund/dispute policies before any live transaction; audit trail for every sensitive admin or financial action.

---

## 2. LOCKED STACK (TARGET) AND WHAT CHANGES FROM TODAY

### 2.1 Target stack

| Layer | Choice |
|---|---|
| Frontend | Next.js 16 (App Router) + React 19 + TypeScript strict + Tailwind v4 + shadcn/ui + TanStack Query v5 + React Hook Form + Zod |
| Backend | NestJS + TypeScript |
| ORM / DB | Prisma on PostgreSQL (Neon) |
| **Auth** | **Better Auth running inside NestJS**, Prisma adapter, users/sessions in our own Neon DB |
| Email | Transactional email provider (default Resend unless I say otherwise): verification, password reset, notifications |
| File storage | **Backblaze B2** (S3-compatible), private buckets, presigned URLs, via AWS SDK v3 with custom endpoint |
| Realtime chat | Ably (transport) + PostgreSQL (source of truth for messages) |
| Payments | Razorpay (Route for marketplace splits). RazorpayX Payouts are deferred and gated (see Phase 5) |
| Jobs / cache | Redis + BullMQ |
| Hosting | Vercel (web) + Railway or Fly (api) |
| Observability | Sentry + structured JSON logs (pino) |

### 2.2 Current → target changes

| Area | Today (per project doc) | Target |
|---|---|---|
| Auth | Firebase Auth (client SDK + Admin SDK), custom `FirebaseAuthGuard` | Better Auth inside NestJS. Firebase fully removed |
| Password storage | "Zero-password" (Google holds credentials) | Better Auth stores password hashes in our DB (use its secure default hashing). **Update the security docs to say this truthfully** |
| File storage | AWS S3 `ap-southeast-2` | Backblaze B2, same presigned-URL model |
| Chat | None | Ably + Postgres |
| Payments | None | Razorpay Route, ledger, webhooks |
| Jobs | None | Redis + BullMQ |
| UI layer | Mixed Tailwind and inline styles | shadcn/ui + design tokens per visual direction |
| Errors/logs | None | Sentry + pino |
| Repo hygiene | Stale README (mentions Clerk, `apps/*`), broken root scripts, committed `web/.git-backup/` | Clean, documented, working root scripts, no committed secrets/backups |

### 2.3 Auth rules (apply to every auth decision)

- Require a **verified email** before any session is trusted for app access.
- **Never auto-link accounts by email** unless the provider has verified that email. Account linking must be explicit and safe.
- **Roles live only in our database.** The client can never supply a role. Onboarding may only choose CLIENT or DESIGNER.
- **ADMIN** comes from a seed script or manual DB change, never from "email matches X at login".
- NestJS enforces authorization on every route. `proxy.ts` in Next.js only does a cheap session-cookie presence check for UX redirects.

---

## 3. OUT OF SCOPE (DO NOT BUILD UNLESS I EXPLICITLY ASK)

Reviews and ratings, AI matching, AI design generation, advanced analytics, subscriptions, multi-currency, mobile app, referral/social features, Orders/Favorites pages (already removed). **Designer withdrawals/payouts (RazorpayX)** are gated: do not implement until I explicitly confirm at the end of Phase 5.

---

## 4. GLOBAL ENGINEERING STANDARDS

- TypeScript `strict: true` in both apps. **No `any`** and no `as any` (the existing `@Roles('X' as any)` pattern must go). Shared enums come from one source.
- Validate every input with DTOs (`class-validator`, `whitelist: true`, `forbidNonWhitelisted: true`) on the API and Zod on the web.
- Money is **integer paise**. Ledger and totals use `BigInt` in the DB layer. Never floats.
- Every state change goes through a service method that (a) runs in a DB transaction and (b) uses a conditional update or row lock so concurrent requests cannot corrupt state.
- Every list endpoint is paginated (cursor or page+limit with a hard max).
- Index every foreign key and every column used in a `where`/`orderBy` on hot paths.
- Public endpoints never return emails, UIDs or any PII. Use explicit `select` shapes, never `include: { user: true }`.
- Tests: Jest for services and guards, Supertest e2e for API flows, Playwright for web critical paths. A bug fix without a regression test is not done.
- Lint and format: ESLint + Prettier, enforced in CI. CI runs typecheck, lint, tests and build for both apps.
- Secrets only in env files that are gitignored. Maintain accurate `.env.example` files. Never log secrets or tokens.

---

## 5. PHASE 0 — AUDIT AND REPO HYGIENE

**Purpose:** know the true state of the code before building on it, and stop the repo from lying.

**P0-1 Verify the documented claims.** For each claim below, confirm in code and report TRUE / FALSE / PARTIAL with file and line references:
1. Proposal isolation: designers cannot see other designers' bids on an open project.
2. S3 key prefix enforcement on portfolio confirm, and whether the object's existence, size and type are verified.
3. Integer-paise money with upper bounds, and whether bounds fit 32-bit limits.
4. Partial unique index allowing only one ACCEPTED proposal per project exists in the actual migration SQL (not just described).
5. `acceptProposal` behaviour: is the status check inside the transaction? Does it verify the proposal belongs to the given project and is still PENDING? (Previous review found it did neither. Confirm whether this is fixed.)
6. Do any public or cross-user endpoints return emails or other PII (designer public profile, open-project listing, project detail for non-owners)?
7. Does the auth guard link or overwrite a user by email without checking email verification?
8. Does anything set the `__firebase_session` cookie that `proxy.ts` checks?

**P0-2 Repo hygiene.**
- Delete `web/.git-backup/` from the repo and history going forward; add to `.gitignore`. Report if it contained anything sensitive.
- Fix the root `package.json` workspaces and scripts so they match real folders (`api/`, `web/`). Provide working `dev`, `build`, `lint`, `test` scripts from the root that run on Windows.
- Rewrite `README.md`: accurate stack, setup steps, env vars, scripts. Remove Clerk and stale references. Remove any publicly listed admin email.
- Add `.env.example` for both apps listing every variable (no real values).
- Add GitHub Actions CI (install, typecheck, lint, test, build for api and web).

**P0-3 Baseline tests.** Remove the boilerplate "Hello World" tests (or register what they test) so `npm test` reflects reality. Add a test harness for the API (test DB strategy, Prisma test setup).

**Done when:** audit report delivered, repo builds from a clean clone using only the README, CI is green.

---

## 6. PHASE 1 — AUTH MIGRATION: FIREBASE → BETTER AUTH

**Purpose:** replace identity with a self-hosted system whose users and sessions live in our own Postgres, and close the account-takeover class of bugs permanently.

**P1-1 Design decision record.** Before coding, read the current Better Auth docs and write `docs/auth-design.md` covering: how Better Auth mounts in NestJS (including raw body/body-parser handling), which Prisma tables it adds, session strategy, cookie settings, CORS credentials, and how the Next.js app consumes it. Evaluate the official integration against any maintained NestJS adapter package and pick one with reasons. Get my approval before continuing.

**P1-2 Install and configure Better Auth in NestJS.**
- Prisma adapter against Neon. Use the pooled URL for runtime and a `DIRECT_URL` for migrations (Neon pooling and Prisma migrations need this).
- Email + password with **required email verification**. Google sign-in as social provider.
- Add `role` as a server-controlled additional field on the user with a default that is NOT privileged, and make it **non-settable from client input**. Confirm the exact option name in the docs.
- Account linking: only for providers that return a verified email; otherwise no linking.
- Cookie config: secure, httpOnly, sameSite chosen deliberately. Production uses subdomains of one domain (web on `lynvia.in`, API on `api.lynvia.in`) with a shared parent-domain cookie. Local dev uses `localhost` with `credentials: 'include'` and CORS configured with `credentials: true` and an explicit origin allowlist.
- Rate-limit all auth routes more strictly than the global 100 req/min/IP (sign-in, sign-up, password reset, verification resend). Set Express `trust proxy` correctly for Railway/Fly so IP-based limiting works.

**P1-3 Email delivery.** Integrate the transactional provider for verification and password-reset emails. Queue sends through BullMQ later (Phase 4); for now send directly with error handling that never breaks the auth flow. Branded, minimal templates in the editorial style.

**P1-4 Replace the NestJS guard.** Remove `FirebaseAuthGuard`, `firebase-admin` and all lazy user upsert logic. Create a `SessionAuthGuard` that validates the Better Auth session, loads the user (with role) from the DB, attaches it to the request, and enforces a typed `@Roles(...)` decorator (enum, no `any`). Keep `@CurrentUser()`.

**P1-5 Onboarding.** `POST /auth/onboard` (or equivalent) lets a signed-in, verified user with no role choose CLIENT or DESIGNER **once**. Creates the matching profile in a transaction. Reject any attempt to choose ADMIN or to change role later. Provide an `ADMIN` seed script (`npm run seed:admin`) that promotes a configured verified user.

**P1-6 Frontend auth.**
- Remove Firebase SDK, `lib/firebase.ts`, `auth-token-sync.tsx`, and the Firebase-based `auth-context.tsx`.
- Add the Better Auth client. Rebuild `sign-in`, `sign-up`, add `verify-email`, `forgot-password`, `reset-password` pages with React Hook Form + Zod, in the editorial design style.
- Replace the Axios bearer-token approach with cookie-credentialed requests (`withCredentials`), a single API client, and a 401 interceptor that redirects to sign-in.
- Rewrite `proxy.ts` to check for the Better Auth session cookie only (UX redirect), and route unauthenticated users away from `/dashboard` and `/onboarding`.
- Keep the role-based dashboard layout guard, but treat it as UX only. Real enforcement is server-side.

**P1-7 Data migration plan.** If any real users exist in Firebase, write a documented one-off migration (export, import, forced password reset). If only test data exists, say so and wipe it.

**P1-8 Tests.** Cover: unverified email cannot access protected routes; role cannot be set via client input; onboarding is one-time; unverified-email account cannot hijack an existing row; rate limits trigger; admin seed works.

**Done when:** no Firebase code or env vars remain, all auth flows work end-to-end locally, the P0-1 item 7 attack is impossible and proven by a test.

---

## 7. PHASE 2 — BACKEND HARDENING (BEFORE ANY NEW FEATURES)

**Purpose:** fix correctness and privacy bugs in the existing marketplace core so everything built later stands on solid ground.

**P2-1 Fix `acceptProposal`.** In one transaction: lock the project row; verify the caller owns the project; verify project status is OPEN; load the proposal **by id AND projectId** and verify it is PENDING; set it ACCEPTED; reject all other PENDING proposals for that project; move the project to PROPOSAL_ACCEPTED. Keep the partial unique index as a backstop. Regression tests: wrong-project proposal id, double accept, concurrent accepts (two parallel requests), non-owner.

**P2-2 Remove PII leaks.** Public designer profile and listing return only display name, bio, specializations, portfolio previews, and approval-safe fields. Open-project listings and project detail never expose client email. Proposals expose designer display name, never email. Add a test that scans public/cross-user responses for `email`.

**P2-3 Visibility rules.** Document and enforce who can see what: open projects (approved designers + owner + admin), proposals (owner + admin + the proposing designer's own), portfolios (public approved designers). Unvetted designers cannot bid.

**P2-4 Storage service rewrite for Backblaze B2.**
- Point AWS SDK v3 at the B2 S3-compatible endpoint; env vars renamed to `STORAGE_*` (endpoint, region, bucket, key id, application key).
- Presigned PUT: enforce content-type allowlist (png, jpg, webp, pdf, plus zip for deliveries) and a max size by signing `Content-Length` limits or validating after upload.
- **Confirm step must verify the object actually exists** (HEAD request), matches expected size/type, and the key matches the caller's prefix. Reject otherwise.
- Cap portfolio items per designer. Replace read-modify-write on `portfolioUrls` with an atomic, race-safe update (or a separate `PortfolioItem` table, preferred).
- Keep TTLs: preview 15 min, delivery 5 min, upload 10 min. Buckets stay private.
- Test with B2 or an S3-compatible local emulator.

**P2-5 Schema fixes.**
- `Project.category` becomes an enum (LOGO_BRANDING, POSTER_SOCIAL, extensible).
- Add indexes on foreign keys and on `status`, `createdAt`, `category` where queried.
- Add `Proposal` and `Project` cursor pagination with a hard page-size cap.
- Add an `AuditEvent` table (actor, action, entity, entityId, metadata, createdAt) and write events for vetting decisions, proposal acceptance and role/admin actions.

**P2-6 Platform plumbing.**
- Global exception filter with consistent error shape; never leak stack traces in production.
- Sentry for API and web. pino structured logging with request IDs. Redact tokens and cookies.
- Health endpoint (`/health`) checking DB.
- Validate env at boot (fail fast with a clear message) using a schema.
- Tighten Helmet CSP and CORS allowlist for production origins.

**Done when:** every item in P0-1 that was FALSE or PARTIAL is fixed with a passing regression test, and `npm test` for the API covers auth, projects, proposals, designers and storage.

---

## 8. PHASE 3 — STAGE A COMPLETION: DESIGN SYSTEM, DISCOVERY, DESIGNER SIDE

**Purpose:** turn the working-but-rough UI into the premium editorial product, and finish everything that is half-built on the discovery side.

**P3-1 Design system.** Install shadcn/ui. Define design tokens in Tailwind v4 / CSS variables: ivory background, near-black text, one purple accent, neutral scale, radii, shadows, spacing. Load a serif display font and a sans body font with `next/font`. Build a small component library (Button, Input, Select, Textarea, Card, Badge, Dialog, Tabs, Toast, Skeleton, EmptyState, Pagination, Avatar) in the editorial style. **Remove all inline `style={{}}`** from existing pages and migrate them to the system. Add dark mode only if I ask.

**P3-2 Layout and navigation.** Rebuild navbar, footer, dashboard shell (sidebar on desktop, drawer on mobile) with role-aware links. Add 404, 500 and loading/error boundaries per route segment.

**P3-3 Landing page.** Editorial hero, how-it-works (client path and designer path), launch categories, trust section (escrow, vetting, revision visibility), designer CTA, FAQ, and a waitlist capture (`POST /waitlist` with email validation and rate limiting, stored in DB). Fast, accessible, SEO metadata and OpenGraph tags.

**P3-4 Explore designers.** Replace the mock data in `designers/page.tsx` with the real API. Server-side search, category/specialization filters, sort, and pagination. Skeleton and empty states. URL-driven filters so pages are shareable.

**P3-5 Public designer profile** at `/designers/[id]`. Bio, specializations, portfolio gallery (signed preview URLs, lazy-loaded, lightbox), and a call to action. No PII. SSR for SEO.

**P3-6 Designer onboarding and vetting UI.** Multi-step onboarding (profile, specializations, portfolio upload with progress and validation). Clear vetting status screen (PENDING / APPROVED / REJECTED with the admin note). Gate bidding UI until APPROVED.

**P3-7 Client project flow.** Polish `post project` (category enum, budget in INR with paise conversion handled in one util, brief length limits, scope/timeline/revision count fields so trust principle one is satisfied). Project detail page with proposals list, accept confirmation dialog, and status timeline.

**P3-8 Designer proposal flow.** Browse open projects with filters, submit a proposal (bid, delivery days, cover note) with validation, "my proposals" page with statuses.

**P3-9 Admin console.** Separate route group (or separate Next app later). Designer vetting queue (approve/reject with note), users table, projects table, all paginated and searchable. Every action writes an `AuditEvent`.

**P3-10 Quality.** Responsive from 360 px up. Accessibility pass (labels, focus, contrast, keyboard). Playwright tests for: sign up → verify → onboard → post project; designer bids; client accepts; admin approves a designer.

**Done when:** no mock data and no inline styles remain, all Stage A flows work against the real API, Lighthouse accessibility and best-practices scores are reported.

---

## 9. REPORT FORMAT (AFTER EVERY PHASE)

1. **What I did** (bullets, with commit hashes).
2. **What I found that was worse than expected** (be blunt).
3. **Tests and checks run** with results.
4. **Deviations** from this prompt and why.
5. **Risks and open questions** for me.
6. **Next phase preview** and a request for my "continue".

---

## 10. PHASE 4 — STAGE B: DELIVERY (ORDERS, WORKSPACE, CHAT, FILES, REVISIONS)

**Purpose:** after a proposal is accepted, give client and designer a real workspace to collaborate, deliver and approve work. This is the product's day-to-day experience.

**P4-1 State machine design (write first, get my approval).** Produce `docs/project-state-machine.md` defining allowed transitions, who can trigger each, and guards. Proposed baseline:
`OPEN → PROPOSAL_ACCEPTED → (payment funded, Phase 5) IN_PROGRESS → DELIVERED → REVISION_REQUESTED ↔ IN_PROGRESS → COMPLETED`, plus `CANCELLED` and `DISPUTED`. Until Phase 5 exists, a feature flag lets the flow run with payment bypassed in non-production only. Encode transitions in one `ProjectStateService`; no other code may write `status`.

**P4-2 Schema.** Add `Revision`, `Delivery`, `DeliveryFile`, `Conversation`, `Message`, `Notification` models. Conversations are tied strictly to a project proposal (client + that designer only). Revision count limit comes from the agreed scope and is enforced server-side.

**P4-3 Delivery and revisions.** Designer uploads deliverables (preview vs final files; previews watermark-free but low-res/short-lived URLs, finals only released on completion where applicable). Client can request a revision with notes (until the limit), or accept. All transitions go through `ProjectStateService` with audit events.

**P4-4 Chat (Ably + Postgres).**
- Messages are written to Postgres **first** (source of truth), then published to Ably.
- NestJS endpoint issues short-lived Ably token requests scoped to the one channel per conversation after verifying the caller is a participant.
- Message history endpoint with cursor pagination; unread counts; basic attachments through the storage service; content length limits; rate limiting on send.
- Frontend: chat panel in the workspace with optimistic send, reconnect handling, and graceful degradation if Ably is down (history still loads).

**P4-5 Workspace UI.** `/dashboard/{role}/projects/[id]` shows: status timeline, agreed scope/budget/deadline, chat, deliveries, revision requests, and the primary action for the viewer's role and current state.

**P4-6 Notifications.** In-app notifications (bell + list + mark read) and email for key events (proposal received/accepted, delivery uploaded, revision requested, completion). Send via **BullMQ** workers on Redis. Notification creation must be wrapped so failures never roll back the business transaction (enqueue after commit; outbox pattern preferred).

**P4-7 Jobs infrastructure.** Redis + BullMQ module, a worker process (separate entry point), retry/backoff, dead-letter handling, and a minimal admin view of failed jobs.

**Done when:** a client and designer can complete a full project lifecycle (payment bypassed behind the dev flag), with chat, delivery, revisions, notifications, all transitions tested, including illegal-transition tests.

---

## 11. PHASE 5 — STAGE C: PAYMENTS, ESCROW AND LEDGER

**Purpose:** money handling. This is the highest-risk part of the product. Correctness beats speed.

**P5-0 FINANCIAL CONTRACT FIRST (hard gate).** Before writing any payment code, produce `docs/financial-contract.md` and wait for my written approval. It must define:
1. **Order / payment / earning state machines** with every transition, trigger, guard and who may fire it.
2. **Ledger design:** append-only `LedgerEntry` (double-entry style or clearly justified alternative), `BigInt` paise, one verified payment → one immutable accounting event → 10%/90% split → designer earning PENDING → authorized settlement (client acceptance or admin) → AVAILABLE. State the exact **rounding rule** for the commission (computed once, stored, never recomputed).
3. **Idempotency and concurrency rules:** unique idempotency keys, unique webhook event IDs (dedup table), `SELECT … FOR UPDATE` or conditional updates, retry safety, out-of-order webhook handling.
4. **Failure handling:** payment failed/abandoned, duplicate payment, partial refund, full refund, reversal, dispute/chargeback, project cancelled after funding.
5. **Razorpay Route specifics** (read current docs): linked-account onboarding and KYC for designers, transfers with settlement hold until release, what happens when a designer has not completed KYC, fees and GST/TDS implications. Flag anything that needs an accountant or a Razorpay support answer. Do not guess.

**P5-1 Schema.** `Order`, `Payment`, `LedgerEntry`, `WebhookEvent`, `Earning`, `Refund`, `Dispute`, `RazorpayLinkedAccount`. DB-level protection: unique constraints for idempotency and webhook IDs, check constraints on legal states, no UPDATE/DELETE on ledger rows (enforce by convention plus a DB trigger or revoked privileges where feasible).

**P5-2 Checkout.** Create a Razorpay order server-side from the accepted proposal amount (never from client-sent amounts). Frontend opens Razorpay Checkout; the success handler only shows a "processing" screen. The **verified webhook** is the only thing that marks a payment captured and moves the project to IN_PROGRESS.

**P5-3 Webhooks.** Raw-body signature verification, event-ID dedup, store every event, process inside a transaction, respond fast (2xx) and do heavy work in BullMQ. Handle out-of-order and replayed events safely.

**P5-4 Escrow release and earnings.** On client acceptance: write the ledger events, move earning PENDING → AVAILABLE, trigger the Route transfer per the contract. Designer dashboard shows pending vs available earnings and per-project breakdown. Client sees payment status and receipt.

**P5-5 Refunds and disputes.** Admin-driven refund flow with ledger reversals and audit events; dispute opening by client within a defined window; admin resolution UI (release / refund / split) with mandatory notes.

**P5-6 Admin finance console.** Payments, ledger viewer, webhook log with replay, reconciliation report (our ledger vs Razorpay) and an alert when they disagree.

**P5-7 Money tests (mandatory).** Duplicate webhook, out-of-order webhook, two concurrent releases, refund after release, partial refund, tampered signature, amount tampering from the client, retry after crash mid-transaction. Money code with untested failure modes is not done.

**P5-8 Withdrawals (GATED).** Do **not** build RazorpayX payouts, withdrawal reservations or payout states until I explicitly confirm. When confirmed: reservation → PROCESSING → COMPLETED/FAILED state machine, minimum withdrawal threshold (target ₹100), idempotent payout creation, failure rollback of the reservation.

**Done when:** the full paid lifecycle works in Razorpay test mode, every money test passes, the contract doc matches the code, and I have signed off on the contract.

---

## 12. PHASE 6 — LAUNCH READINESS

**Purpose:** everything needed before real users and real money.

**P6-1 Legal and policy pages:** Terms of Service, Privacy Policy, Refund and Cancellation Policy, Dispute Policy, Designer Agreement, Community Guidelines. Draft clearly in plain English, mark every page "needs legal review", and link them from footer and checkout. Add consent capture at sign-up with timestamp and policy version stored.

**P6-2 Security review.** Re-run the P0-1 audit; dependency audit; secrets scan; verify all CORS/CSP/cookie settings in production config; confirm rate limits; check every route has a guard and a test. Produce `docs/security-review.md`.

**P6-3 Performance and reliability.** Query review with `EXPLAIN` on hot paths, DB connection settings for Neon, caching where it is safe, image optimization for portfolios, backup/restore procedure documented, graceful shutdown for API and workers.

**P6-4 Deployment.** Vercel for web, Railway or Fly for API and worker, managed Redis, environment configs per stage (dev / staging / prod), migrations run in CI/CD with `prisma migrate deploy`, zero-downtime-safe migration rules, domain and cookie setup (`lynvia.in`, `api.lynvia.in`), uptime monitoring and Sentry alerts.

**P6-5 Closed beta kit.** Invite-only sign-up toggle, feedback form, admin dashboard of key marketplace health numbers, runbook for common incidents (webhook failures, stuck payments, failed uploads).

**P6-6 Final E2E.** Playwright suite covering the full lifecycle in staging with Razorpay test mode: sign up, verify, onboard, vetting, post, bid, accept, pay, chat, deliver, revise, accept, release, refund path.

---

## 13. TARGET FOLDER STRUCTURE

```
lynvia/
├─ api/
│  ├─ prisma/ (schema.prisma, migrations/, seed/)
│  └─ src/
│     ├─ auth/ (better-auth config, SessionAuthGuard, roles, current-user)
│     ├─ users/  designers/  projects/  proposals/
│     ├─ workspace/ (state service, deliveries, revisions)
│     ├─ chat/ (conversations, messages, ably tokens)
│     ├─ payments/ (orders, razorpay, webhooks, ledger, earnings, refunds, disputes)
│     ├─ notifications/  jobs/ (bullmq queues + workers)
│     ├─ storage/ (b2 service)  audit/  common/ (filters, pipes, utils)
│     └─ main.ts  worker.ts
├─ web/
│  └─ src/
│     ├─ app/ (public, auth, onboarding, designers, dashboard/{client,designer,admin}, legal)
│     ├─ components/ (ui/ = shadcn, feature components)
│     ├─ lib/ (api client, auth client, utils, money)
│     └─ proxy.ts
├─ docs/ (auth-design, project-state-machine, financial-contract, security-review)
├─ .github/workflows/ci.yml
└─ README.md  ANTIGRAVITY_MASTER_PROMPT.md  AGENTS.md
```

## 14. ENVIRONMENT VARIABLES (TARGET)

**API:** `NODE_ENV`, `PORT`, `DATABASE_URL` (pooled), `DIRECT_URL` (migrations), `BETTER_AUTH_SECRET`, `BETTER_AUTH_URL`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `EMAIL_PROVIDER_API_KEY`, `EMAIL_FROM`, `STORAGE_ENDPOINT`, `STORAGE_REGION`, `STORAGE_BUCKET`, `STORAGE_KEY_ID`, `STORAGE_APPLICATION_KEY`, `S3_PREVIEW_URL_TTL`, `S3_DELIVERY_URL_TTL`, `ABLY_API_KEY`, `REDIS_URL`, `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, `RAZORPAY_WEBHOOK_SECRET`, `SENTRY_DSN`, `FRONTEND_URL`, `COOKIE_DOMAIN`.
**Web:** `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_RAZORPAY_KEY_ID`, `NEXT_PUBLIC_SENTRY_DSN`. No secrets with the `NEXT_PUBLIC_` prefix, ever.

---

## 15. START NOW

Begin with **Phase 0, step P0-1**. Deliver the audit report in the format from section 9 and **stop**. Do not begin Phase 1 until I reply "continue".
