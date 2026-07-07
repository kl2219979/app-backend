from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    """Verify that the API is running."""
    return {"status": "ok"}
