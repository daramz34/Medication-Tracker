from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from api.v1.router import api_router
from database import Base, engine
from service.scheduler import start_scheduler
from core.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Track your medications, streaks, and get email reminders"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000",  "https://medication-tracker-production-19b8.up.railway.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

app.add_middleware(BaseHTTPMiddleware, dispatch=security_headers_middleware)

app.include_router(api_router, prefix="/api/v1")
FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"
TEMPLATES_DIR = FRONTEND_DIR / "templates"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR / "static"), name="static")


def frontend_page(name: str) -> FileResponse:
    return FileResponse(TEMPLATES_DIR / name)


@app.get("/", include_in_schema=False)
def landing_page():
    return frontend_page("index.html")


@app.get("/login", include_in_schema=False)
def login_page():
    return frontend_page("auth.html")


@app.get("/app", include_in_schema=False)
def dashboard_page():
    return frontend_page("dashboard.html")


@app.get("/medications", include_in_schema=False)
def medications_page():
    return frontend_page("medications.html")
# ✅ use /med/ instead of /medications/
@app.get("/med/{med_id}", include_in_schema=False)
def medication_detail_page(med_id: int):
    return frontend_page("medication-detail.html")



@app.get("/settings", include_in_schema=False)
def settings_page():
    return frontend_page("settings.html")

@app.on_event("startup")
def startup():
    start_scheduler()

@app.on_event("shutdown")
def shutdown():
    from service.scheduler import scheduler
    scheduler.shutdown()