from typing import Annotated

from fastapi import Depends, HTTPException
from starlette.status import HTTP_403_FORBIDDEN

from app.application.services.permission_service import PermissionService
from app.domain.entities.employee.enum import Permission
from app.infrastructure.database import MentorProfile
from app.presentation.dependencies.employee import get_current_employee


class EndpointPolicy:
    permissions: set[Permission] = set()

    async def require_permission(self, employee: Annotated[MentorProfile, Depends(get_current_employee)]):
        role_perms = set(PermissionService.get_permissions(employee.role))

        if self.permissions and role_perms.isdisjoint(self.permissions):
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Access denied")
