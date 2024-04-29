from datetime import date
from typing import Any

from pydantic import BaseModel, field_validator


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
