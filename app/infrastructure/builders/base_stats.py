from __future__ import annotations

from datetime import date, datetime, time, timedelta


class BaseStatsQueryBuilder:
    """
    Common helpers for stats builders.
    """

    @staticmethod
    def _date_bounds(start: date, end: date) -> tuple[datetime, datetime]:
        start_dt = datetime.combine(start, time.min)
        # exclusive upper bound is the start of the day after `end`
        end_dt = datetime.combine(end + timedelta(days=1), time.min)
        return start_dt, end_dt
