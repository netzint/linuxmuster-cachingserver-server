from fastapi import APIRouter

router = APIRouter(
    prefix="/v2",
    tags=["v2"],
    responses={404: {"description": "Not found"}}
)