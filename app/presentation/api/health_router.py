from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from app.application.use_cases.health.healch_check_use_case import HealthCheckUseCase
from app.domain.entities.health import HealthCheck
from app.presentation.dependencies.health import get_health_check_use_case

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check(use_case: HealthCheckUseCase = Depends(get_health_check_use_case)) -> JSONResponse:
    hc_data = HealthCheck(
        db=await use_case.db_health(),
    )
    status_code = HTTP_200_OK if hc_data.all_ok else HTTP_500_INTERNAL_SERVER_ERROR

    return JSONResponse(content=hc_data.model_dump(), status_code=status_code)
