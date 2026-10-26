-- Rename clerk_id column to firebase_uid on the users table
-- This is a safe rename: drop the old unique index, rename the column, add the new unique index.

ALTER TABLE "users" RENAME COLUMN "clerk_id" TO "firebase_uid";
