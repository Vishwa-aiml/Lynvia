-- Partial unique index enforcing at DB level that only ONE proposal
-- per project can ever have status = 'ACCEPTED'.
-- This is a safety net on top of the application-level check in
-- ProposalsService. Even if two concurrent transactions race to
-- accept different proposals, the DB will reject one.
--
-- Prisma doesn't generate partial indexes natively, so this migration
-- is hand-crafted (the only acceptable exception to the "no hand-edit" rule).

CREATE UNIQUE INDEX "proposals_one_accepted_per_project"
  ON "proposals" ("project_id")
  WHERE (status = 'ACCEPTED');