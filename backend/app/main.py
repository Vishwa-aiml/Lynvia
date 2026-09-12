from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
import logging
from app.core.config import settings


def create_app() -> FastAPI:
    """Application factory to allow tests to configure DB engine/session before routers import."""
    app = FastAPI(title="Lynvia API")

    # CORS configuration
    origins = []
    raw = getattr(settings, "BACKEND_CORS_ORIGINS", None)
    if raw is None or raw == "*":
        origins = ["*"]
    elif isinstance(raw, str) and "," in raw:
        origins = [o.strip() for o in raw.split(",") if o.strip()]
    elif isinstance(raw, str):
        origins = [raw]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register a simple exception handler for uncaught exceptions
    logger = logging.getLogger("app")

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error: %s", exc)
        return JSONResponse({"detail": "Internal server error"}, status_code=500)

    # Import routers lazily so DB/session can be overridden in tests before router modules import
    from app.api.routes.health import router as health_router
    from app.api.routes import auth as auth_router
    # from app.api.routes import users as users_router
    # from app.api.routes import client_profile as client_profile_router
    # from app.api.routes import designer_profile as designer_profile_router
    # from app.api.routes import service as services_router
    # from app.api.routes import projects as projects_router
    # from app.api.routes import portfolio as portfolio_router
    # from app.api.routes import discovery as discovery_router
    # from app.api.routes import workspace as workspace_router
    # from app.api.routes import payments as payments_router
    # from app.api.routes import earnings as earnings_router

    app.include_router(health_router, prefix="/health", tags=["health"])
    app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
    # app.include_router(users_router.router, prefix="/users", tags=["users"])
    # app.include_router(client_profile_router.router, prefix="/profiles", tags=["profiles"])
    # app.include_router(designer_profile_router.router, prefix="/profiles", tags=["profiles"])
    # app.include_router(services_router.router, prefix="/services", tags=["services"])
    # app.include_router(portfolio_router.router, prefix="/portfolio", tags=["portfolio"])
    # app.include_router(discovery_router.router, prefix="/discovery", tags=["discovery"])
    # app.include_router(projects_router.router, prefix="/projects", tags=["projects"])
    # app.include_router(workspace_router.router, prefix="/projects/{project_id}/workspace", tags=["workspace"])
    # from app.api.routes import invitations as invitations_router
    # app.include_router(invitations_router.router, prefix="", tags=["invitations"])
    # app.include_router(payments_router.router, prefix="", tags=["payments"])
    
    # from app.api.routes import notifications as notifications_router
    # app.include_router(notifications_router.router, prefix="", tags=["notifications"])
    # app.include_router(earnings_router.router, prefix="", tags=["earnings"])

    # from app.api.routes import chat as chat_router
    # app.include_router(chat_router.router, prefix="", tags=["chat"])

    # from app.api.routes import disputes as disputes_router
    # app.include_router(disputes_router.router, prefix="", tags=["disputes"])

    # from app.api.routes import withdrawals as withdrawals_router
    # app.include_router(withdrawals_router.router, prefix="", tags=["withdrawals"])

    @app.get("/")
    def root():
        return {"message": "Lynvia API - Foundation ready"}

    return app


# Default app for running directly
app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
