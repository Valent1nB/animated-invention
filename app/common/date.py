from datetime import date

from pydantic import BaseModel, ConfigDict, model_validator


class DateRange(BaseModel):
    start_date: date
    end_date: date

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def check_dates(self) -> "DateRange":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be after or equal to start_date")
        return self
