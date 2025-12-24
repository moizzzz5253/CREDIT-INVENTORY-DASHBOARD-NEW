from fastapi import APIRouter
from .constants import CATEGORIES

router = APIRouter(prefix="/constants", tags=["constants"])


@router.get("/categories")
def get_categories():
    return {"categories": CATEGORIES}
