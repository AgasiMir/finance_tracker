from fastapi import APIRouter
from sqlalchemy import text
from app.api.dependencies import DBDep


router = APIRouter(prefix="/handlers", tags=["handlers 🔧🔧🔧"])


@router.get("/check-db")
async def check_db(db: DBDep):
    try:
        version = await db.session.execute(text("SELECT version()"))
        return {"version": version.scalar()}
    except Exception as err:
        return {"error": str(err)}
