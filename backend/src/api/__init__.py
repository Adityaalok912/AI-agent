## `api/__init__.py`

from fastapi import FastAPI
from api.routes_agents import router as agents_router
from api.routes_results import router as results_router
from api.routes_projects import router as projects_router


app = FastAPI(title="AutoTeamAI API", version="1.0.0")


# Mount routers
app.include_router(projects_router, prefix="/projects", tags=["projects"])
app.include_router(agents_router, prefix="/agents", tags=["agents"])
app.include_router(results_router, prefix="/results", tags=["results"])


# Health check
@app.get("/health")
async def health():
    return {"status": "ok"}