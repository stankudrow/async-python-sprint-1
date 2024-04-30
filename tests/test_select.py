import pytest

from src.core import select_forecast_days
from src.types_ import FORECAST, DayInfo, HourInfo
from src.utils import SUITABLE_CONDITIONS


@pytest.mark.parametrize(
    ("forecasts", "days"),
    [
        ([{}], []),
        (
            [
                {
                    "date": None,
                    "hours": None,
                }
            ],
            [],
        ),
        (
            [
                {
                    "date": None,
                    "hours": [{"hour": "10", "temp": 6.3, "condition": "lolo"}],
                }
            ],
            [],
        ),
        (
            [
                {
                    "date": "2022-05-13",
                    "hours": [
                        {"hour": "20", "temp": "4.1", "condition": "nonono"},
                        {
                            "hour": "12",
                            "temp": 9.2,
                            "condition": SUITABLE_CONDITIONS[0],
                        },
                        {
                            "hour": "9",
                            "temp": "12.6",
                            "condition": SUITABLE_CONDITIONS[1],
                        },
                        {"hour": "7", "temp": "4.1", "condition": "nonono"},
                    ],
                }
            ],
            [
                DayInfo(
                    date_="2022-05-13",
                    hours=[
                        HourInfo(
                            hour=12, temperature=9.2, condition=SUITABLE_CONDITIONS[0]
                        ),
                        HourInfo(
                            hour=9, temperature=12.6, condition=SUITABLE_CONDITIONS[1]
                        ),
                    ],
                )
            ],
        ),
    ],
)
def test_select_forecast_days(forecasts: list[FORECAST], days: list[DayInfo]):
    assert select_forecast_days(forecasts) == days
