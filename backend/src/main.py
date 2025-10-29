import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes_agents import router as agents_router
from api.routes_results import router as results_router
from api.routes_projects import router as projects_router
from api.db.database import engine, Base


# --- Initialize Database ---
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# --- Lifespan Context ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting AutoTeamAI Backend...")
    await init_db()
    yield
    print("🧹 Cleaning up database connections...")
    await engine.dispose()


# --- Create FastAPI App ---
app = FastAPI(
    title="AutoTeamAI Backend",
    version="1.0.0",
    description="Multi-agent orchestration backend for AI workflow automation.",
    lifespan=lifespan,
)


# --- ✅ CORS Middleware ---
# This is CRUCIAL to fix your 405 'Method Not Allowed' preflight issue
origins = [
    "http://localhost:5173",  # React dev server
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # Which frontends can access
    allow_credentials=True,
    allow_methods=["*"],            # Allow all methods (POST, GET, OPTIONS, etc.)
    allow_headers=["*"],            # Allow all headers
)


# --- Include Routers ---
app.include_router(projects_router, prefix="/api/projects", tags=["Projects"])
app.include_router(agents_router, prefix="/api/agents", tags=["Agents"])
app.include_router(results_router, prefix="/api/results", tags=["Results"])


# --- Environment Variables ---
API_KEY = os.getenv("API_KEY")


# --- Root Endpoint ---
@app.get("/")
async def root():
    return {"message": "Welcome to AutoTeamAI Backend!"}


# --- Health Check ---
@app.get("/health")
async def health():
    return {"status": "ok"}


# --- Lifecycle Events (optional logging) ---
@app.on_event("startup")
async def startup_event():
    print("✅ AutoTeamAI backend started successfully.")


@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 AutoTeamAI backend shutting down.")


# --- Entry Point for Local Run ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
