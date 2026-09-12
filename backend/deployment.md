Deployment notes for Lynvia backend

Environment
Copy backend/.env.example -> backend/.env and set DATABASE_URL and SECRET_KEY.
SECRET_KEY: use a secure random 32+ character value (e.g., use os.urandom(48).hex()).

Database & Migrations
Alembic is preconfigured under backend/alembic. Apply migrations with:
  alembic -c backend/alembic.ini upgrade head
The code normalizes emails on write and a Postgres unique index on lower(email) is included in migrations.

Passwords & Hashing
Current hashing: pbkdf2_sha256 (passlib) — chosen for portability. If you have existing bcrypt hashes, plan a migration:
Keep bcrypt support in verification by detecting hash scheme and re-hashing to pbkdf2 on next login, or
Use passlib's CryptContext with multiple schemes and preferred scheme set to pbkdf2_sha256.

Security
Run behind TLS. Set BACKEND_CORS_ORIGINS to your frontend origins.
Rotate SECRET_KEY if compromised; invalidate existing tokens by changing the key.

Notes
Money fields stored as integer minor-units (e.g., cents). Ensure frontend sends integers.
Deadlines are validated to be future datetimes; naive datetimes treated as UTC.
