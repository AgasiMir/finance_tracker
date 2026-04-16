from fastapi import APIRouter
from app.api.dependencies import DBDep
from sqlalchemy import text


router = APIRouter(prefix="/handlers", tags=["handlers 🔧🔧🔧"])


@router.get("/check_db")
async def check_db(db: DBDep):
    try:
        version = await db.execute(text("SELECT version()"))
        return {"version": version.scalar()}
    except Exception as e:
        return {"error": str(e)}
