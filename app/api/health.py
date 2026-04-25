from fastapi import APIRouter, HTTPException, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import text
from app.api.dependencies import DBDep, UserDep

router = APIRouter(prefix="/health", tags=["monitoring 📊📈"])


@router.get("/check-db")
async def check_db(db: DBDep, current_user: UserDep):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        version = await db.session.execute(text("SELECT version()"))
        return {"version": version.scalar()}
    except Exception:
        raise HTTPException(status_code=503, detail="Database unreachable")


@router.get("/metrics", tags=["monitoring"])
async def get_metrics():
    """
    Эндпоинт для сбора метрик Prometheus.
    Доступ: GET /metrics
    Content-Type: text/plain
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
