Development README — Lynvia (Foundation setup)

Create a virtualenv and install dependencies:

   python -m venv .venv
   ..venv\Scripts\activate
   pip install -r backend\requirements.txt

Copy .env.example -> .env and update DATABASE_URL

Run the app locally:

   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

Database & Migrations (Alembic):

   cd backend
   alembic init alembic  # only once; see alembic/README.md for guidance

Project structure:
   backend/app/       FastAPI application
   backend/alembic/   DB migration scripts

Next suggested steps:
Add SQLAlchemy models in backend/app/models
Add Alembic env + migration scripts
Implement authentication
