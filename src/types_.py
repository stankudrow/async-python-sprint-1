from datetime import date
from typing import Any

from pydantic import BaseModel, field_validator, NonNegativeInt


FORECAST = dict[str, Any]


class HourInfo(BaseModel):
    hour: None | int = None
    temperature: None | int | float = None
    condition: None | str = None

    def to_json(self) -> FORECAST:
        return {
            "hour": self.hour,
            "temp": self.temperature,
            "cond": self.condition,
        }


class DayInfo(BaseModel):
    date_: None | date = None
    hours: None | list[HourInfo] = None

    @field_validator("date_", mode="before")
    @classmethod
    def validate_date(cls, date_):
        if isinstance(date_, str):
            return date.fromisoformat(date_)
        return date_

    def to_json(self) -> FORECAST:
        hours = [hour.to_json() for hour in self.hours] if self.hours else self.hours
        return {
            "date": self.date_,
            "hours": hours,
        }


class StatsInfo(BaseModel):
    date_: None | date = None
    hours_start: None | NonNegativeInt = None
    hours_end: None | NonNegativeInt = None
    hours_count: None | NonNegativeInt = None
    temp_avg: None | float = None
    relevant_cond_hours: NonNegativeInt = 0

    @field_validator("date_", mode="before")
    @classmethod
    def validate_date(cls, date_):
        if isinstance(date_, str):
            return date.fromisoformat(date_)
        return date_

    def model_post_init(self, _ctx):
        hs, he = self.hours_start, self.hours_end
        hc = self.hours_count
        if (hs is None) and (he is None) and (hc is None):
            return
        if hs > he:
            msg = f"hours_end={he} < hours_start={hs}"
            raise ValueError(msg)
        if he and not hc:
            msg = f"hours_count={hc} is zero with non-zero hours"
            raise ValueError(msg)

    def to_json(self) -> FORECAST:
        return {
            "date": self.date_.isoformat() if self.date_ else None,
            "hours_start": self.hours_start,
            "hours_end": self.hours_end,
            "hours_count": self.hours_count,
            "temp_avg": self.temp_avg,
            "relevant_cond_hours": self.relevant_cond_hours,
        }
