Quick API guide (JWT auth)

Auth
POST /auth/register -> { email, password, full_name, role }
POST /auth/login -> { email, password } -> returns { access_token }
GET /auth/me -> Bearer token -> returns current user

Profiles
POST /profiles/client (CLIENT only) -> create client profile
PUT /profiles/client/{user_id} (owner only) -> update client profile
POST /profiles/designer (DESIGNER only) -> create designer profile
PUT /profiles/designer/{user_id} (owner or ADMIN) -> update designer profile

Services
POST /services (DESIGNER only) -> create service
GET /services/designers/{designer_id}/services -> list active services

Projects
POST /projects (CLIENT only) -> create project
GET /projects/{id} -> get project
PUT /projects/{id} (owner only) -> update project

Notes
Money fields are stored as integer minor-units (e.g., paise/cents). Use integers in requests.
Project deadlines must be in the future (ISO 8601). Naive datetimes are treated as UTC.
Set DATABASE_URL and SECRET_KEY via environment (.env supported).
