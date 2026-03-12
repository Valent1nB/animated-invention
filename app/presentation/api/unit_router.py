from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.use_cases.units.get_units_use_case import GetUnitsUseCase
from app.domain.entities.employee.employee import UnitOut
from app.domain.unit_of_work import IUnitOfWork
from app.infrastructure.database import MentorProfile
from app.presentation.dependencies.unit_of_work import get_unit_of_work
from app.presentation.policies.units.can_get_units import CanGetUnits

router = APIRouter(prefix="/unit", tags=["unit"])


def get_units_use_case(uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)]) -> GetUnitsUseCase:
    return GetUnitsUseCase(uow)


@router.get("", response_model=list[UnitOut])
async def get_units(
    _: Annotated[MentorProfile, Depends(CanGetUnits())],
    use_case: GetUnitsUseCase = Depends(get_units_use_case),
) -> list[UnitOut]:
    return await use_case()
