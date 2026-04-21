from fastapi import APIRouter, HTTPException
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
