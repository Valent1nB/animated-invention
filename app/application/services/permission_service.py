from app.domain.entities.employee.enum import Permission, UserRole


class PermissionService:
    _role_to_permissions: dict[UserRole, set[Permission]] = {
        UserRole.intern: Permission.basic_intern_permissions(),
        UserRole.superuser: Permission.superuser_permissions(),
        UserRole.mentor: Permission.mentor_permissions(),
        UserRole.head_mentor: Permission.head_mentor_permissions(),
    }

    @classmethod
    def get_permissions(cls, role: UserRole) -> list[Permission]:
        return sorted(cls._role_to_permissions[role])
