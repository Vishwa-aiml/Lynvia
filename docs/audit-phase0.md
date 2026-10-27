# Lynvia — Phase 0 Audit Report (P0-1)

**Date:** October 27, 2026  
**Auditor:** Senior Full-Stack Engineer / Technical Mentor  
**Scope:** Verification of documented security and architecture claims across `api/` (NestJS) and `web/` (Next.js).

---

## 1. Executive Summary

A line-by-line verification was conducted across all codebase components, Prisma schemas, and migrations to validate the eight baseline claims defined in `ANTIGRAVITY_MASTER_PROMPT.md` (P0-1). 

While certain defensive controls (proposal isolation, 32-bit integer paise bounds, and the database-level partial unique index) are confirmed active, **critical vulnerabilities were discovered** in authentication account linking (account takeover), proposal state transition race conditions, and extensive public/cross-user PII leakage (user emails). Additionally, repository hygiene issues (committed `.git-backup` directory and broken workspace scripts) require immediate remediation.

---

## 2. Item-by-Item Verification Findings

### 2.1 Proposal Isolation
* **Claim:** Designers cannot see competing designers' bids, delivery times, or cover notes on an open project.
* **Verdict:** **TRUE**
* **Code Reference:** [`api/src/projects/projects.service.ts:87-92`](file:///d:/LYNNNN/api/src/projects/projects.service.ts#L87-L92) and [`api/src/proposals/proposals.service.ts:98`](file:///d:/LYNNNN/api/src/proposals/proposals.service.ts#L98)
* **Details:**
  * In `ProjectsService.findOne(id, requesterId, requesterRole)`:
    ```typescript
    if (!isOwner && !isAdmin) {
      return {
        ...project,
        proposals: project.proposals.filter((p) => p.designerId === requesterId),
      };
    }
    ```
  * In `ProposalsService.findForProject(projectId, clientId)`:
    ```typescript
    if (project.clientId !== clientId) throw new ForbiddenException('Not your project');
    ```
  * Designers only receive their own submitted proposal when viewing an open project. Non-owners never receive competing bids.

---

### 2.2 S3 Key Prefix Enforcement & Portfolio Asset Verification
* **Claim:** S3 key prefix is enforced on portfolio confirmation, and the object's existence, size, and type are verified.
* **Verdict:** **PARTIAL**
* **Code Reference:** [`api/src/designers/designers.service.ts:50-67`](file:///d:/LYNNNN/api/src/designers/designers.service.ts#L50-L67)
* **Details:**
  * **Prefix Enforcement (Active):**
    ```typescript
    if (!s3Key.startsWith(`portfolios/${designer.id}/`)) {
      throw new ForbiddenException('Invalid S3 key: key must belong to your portfolio namespace');
    }
    ```
  * **Missing Verifications (Vulnerable):**
    * The server **does not perform a `HeadObjectCommand`** against S3.
    * Object existence, true byte size, and actual MIME type are **unverified**. A designer can confirm a non-existent key or a file uploaded with altered headers.
    * Portfolio update uses an unprotected array spread (`[...profile.portfolioUrls, s3Key]`), susceptible to lost updates under concurrent confirmations.
    * No maximum item cap is enforced.

---

### 2.3 Integer-Paise Money & 32-Bit Limit Bounds
* **Claim:** Money is stored as integer paise with upper bounds fitting PostgreSQL 32-bit limits.
* **Verdict:** **TRUE**
* **Code Reference:**
  * [`api/src/projects/dto/create-project.dto.ts:31-34`](file:///d:/LYNNNN/api/src/projects/dto/create-project.dto.ts#L31-L34)
  * [`api/src/proposals/dto/create-proposal.dto.ts:11-14`](file:///d:/LYNNNN/api/src/proposals/dto/create-proposal.dto.ts#L11-L14)
  * [`api/prisma/schema.prisma:104,119`](file:///d:/LYNNNN/api/prisma/schema.prisma#L104)
* **Details:**
  * DTOs enforce `@IsInt()`, `@Min(50000)` (₹500), and `@Max(200000000)` (₹20,00,000 / 200M paise).
  * PostgreSQL signed `INTEGER` max is `2,147,483,647` (2.14B paise).
  * `200,000,000 < 2,147,483,647`, fitting safely within 32-bit database bounds.
  * *Note for Phase 5:* Accounting ledger and cumulative totals must transition to `BigInt`.

---

### 2.4 Partial Unique Index for Accepted Proposals
* **Claim:** Partial unique index enforcing only one `ACCEPTED` proposal per project exists in actual migration SQL.
* **Verdict:** **TRUE**
* **Code Reference:** [`api/prisma/migrations/20261025061228_add_partial_unique_accepted_proposal/migration.sql:10-12`](file:///d:/LYNNNN/api/prisma/migrations/20261025061228_add_partial_unique_accepted_proposal/migration.sql#L10-L12)
* **Details:**
  * Active deployed migration SQL:
    ```sql
    CREATE UNIQUE INDEX "proposals_one_accepted_per_project"
      ON "proposals" ("project_id")
      WHERE (status = 'ACCEPTED');
    ```
  * Enforces at the database engine level that two concurrent acceptances cannot succeed.

---

### 2.5 `acceptProposal` Transaction & Validation Integrity
* **Claim:** Project status check is inside the transaction, and verifies the proposal belongs to the given project and is currently `PENDING`.
* **Verdict:** **FALSE**
* **Code Reference:** [`api/src/projects/projects.service.ts:98-126`](file:///d:/LYNNNN/api/src/projects/projects.service.ts#L98-L126)
* **Details:**
  * **Status check is outside the transaction:** Lines 105–107 check `if (project.status !== ProjectStatus.OPEN)` before `prisma.$transaction`. Without `SELECT ... FOR UPDATE`, concurrent requests can race past the check.
  * **Missing proposal project-binding:** Line 116 executes:
    ```typescript
    await tx.proposal.update({
      where: { id: proposalId },
      data: { status: 'ACCEPTED' },
    });
    ```
    The query filters only on `id: proposalId`. It **does not verify** that `proposal.projectId === projectId`. A client could pass a proposal ID from an unrelated project.
  * **Missing PENDING check:** Does not assert that `proposal.status === 'PENDING'` prior to acceptance.

---

### 2.6 Personally Identifiable Information (PII) Leaks
* **Claim:** No public or cross-user endpoints return user emails or sensitive PII.
* **Verdict:** **FALSE (Active PII Leaks Present)**
* **Code References:**
  1. [`api/src/designers/designers.service.ts:28`](file:///d:/LYNNNN/api/src/designers/designers.service.ts#L28):
     `GET /api/designers/:userId` (public, unauthenticated) includes:
     ```typescript
     include: { user: { select: { id: true, email: true } } }
     ```
     Exposes verified designer email addresses to anonymous web scrapers.
  2. [`api/src/projects/projects.service.ts:34`](file:///d:/LYNNNN/api/src/projects/projects.service.ts#L34):
     `GET /api/projects` (open projects) includes:
     ```typescript
     client: { select: { id: true, email: true } }
     ```
     Leaks the email of every client who posted an open project to any authenticated user.
  3. [`api/src/projects/projects.service.ts:56`](file:///d:/LYNNNN/api/src/projects/projects.service.ts#L56):
     `GET /api/projects/:id` includes client email, accessible by any designer viewing project details.

---

### 2.7 Insecure Account Linking (Account Takeover)
* **Claim:** Auth guard does not link or overwrite users by email without verifying email ownership.
* **Verdict:** **FALSE (Critical Account Takeover Vulnerability)**
* **Code Reference:** [`api/src/auth/firebase-auth.guard.ts:85-95`](file:///d:/LYNNNN/api/src/auth/firebase-auth.guard.ts#L85-L95)
* **Details:**
  ```typescript
  if (!user) {
    const existingByEmail = email
      ? await this.prisma.user.findUnique({ where: { email } })
      : null;

    if (existingByEmail) {
      user = await this.prisma.user.update({
        where: { id: existingByEmail.id },
        data: { firebaseUid },
      });
    } ...
  }
  ```
  * The guard **never inspects `decoded.email_verified`**.
  * An attacker can create an unverified Firebase account using a target user's email (e.g. `admin@lynvia.in` or a client's email), present their valid Firebase token, and the guard overwrites `firebaseUid` on the victim's database record.

---

### 2.8 Edge Session Cookie Check (`__firebase_session`)
* **Claim:** Session indicator checked by edge proxy middleware is actively set by the application.
* **Verdict:** **FALSE (Dead Code)**
* **Code Reference:** [`web/src/proxy.ts:34`](file:///d:/LYNNNN/web/src/proxy.ts#L34)
* **Details:**
  * `proxy.ts` checks `request.cookies.has('__firebase_session')`.
  * A full codebase scan confirms `__firebase_session` is never set anywhere in `web/` or `api/`.
  * The middleware check fails closed or relies entirely on client-side routing.

---

## 3. Hygiene & Infrastructure Findings

1. **Tracked `.git-backup`:**
   `web/.git-backup/` was checked into Git tracking (over 80 loose Git object files, refs, and commit logs in the Git index).
2. **Broken Root Workspaces:**
   `package.json` specifies `"workspaces": ["apps/*", "packages/*"]` and scripts pointing to `apps/api` and `apps/web`. The actual folders are `api/` and `web/`. Root execution (`npm run dev:api`) fails immediately.
3. **Empty Test Suite:**
   API test harness contains only a single boilerplate unit test (`AppController -> Hello World!`). No integration or domain tests exist.

---

## 4. Remediation Checklist for Phase 0 & Phase 1

- [x] Document audit findings in `docs/audit-phase0.md`.
- [ ] Scan full Git history for committed credentials and keys.
- [ ] Untrack and purge `web/.git-backup/` from Git and filesystem.
- [ ] Align root `package.json` workspaces to `api` and `web` with cross-platform PowerShell/bash scripts.
- [ ] Rewrite `README.md` and sanitize `.env.example`.
- [ ] Establish GitHub Actions CI with automated secret scanning (`gitleaks`).
- [ ] Replace `Hello World` test with baseline test harness in Vitest.
- [ ] Phase 1: Migrate completely from Firebase to Better Auth (closing the unverified email account linking bug permanently).
