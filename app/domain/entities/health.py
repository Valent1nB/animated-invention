from enum import StrEnum

from pydantic import BaseModel


class Status(StrEnum):
    OK = "ok"
    FAILED = "failed"


class CheckResult(BaseModel):
    status: Status
    time: float
    info: str | None = None


class HealthCheck(BaseModel):
    db: CheckResult

    @property
    def all_ok(self) -> bool:
        return all(getattr(self, name).status == Status.OK for name in self.__class__.model_fields.keys())
