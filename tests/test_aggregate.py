import pytest

from src.core import aggregate_forecast_stats
from src.types_ import FORECAST, StatsInfo
from src.utils import SUITABLE_CONDITIONS


@pytest.mark.parametrize(
    ("forecasts", "stats"),
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
                    "date": "2024-08-09",
                    "hours": [
                        {
                            "hour": "10",
                            "temp": None,
                            "condition": SUITABLE_CONDITIONS[2],
                        }
                    ],
                }
            ],
            [
                StatsInfo(
                    date_="2024-08-09",
                    hours_start=10,
                    hours_end=10,
                    hours_count=1,
                    temp_avg=None,
                    relevant_cond_hours=1,
                ).to_json()
            ],
        ),
        (
            [
                {
                    "date": "2022-05-13",
                    "hours": [
                        {"hour": "20", "temp": "4.1", "condition": "nonono"},
                        {"hour": "14", "temp": 1, "condition": "nonono"},
                        {"hour": "12", "temp": 2, "condition": SUITABLE_CONDITIONS[0]},
                        {"hour": "9", "temp": "4", "condition": SUITABLE_CONDITIONS[1]},
                        {"hour": "7", "temp": "4.1", "condition": "nonono"},
                    ],
                }
            ],
            [
                StatsInfo(
                    date_="2022-05-13",
                    hours_start=9,
                    hours_end=12,
                    hours_count=2,
                    temp_avg=3.0,
                    relevant_cond_hours=2,
                ).to_json()
            ],
        ),
    ],
)
def test_aggregate_forecast_stats(forecasts: list[FORECAST], stats: list[StatsInfo]):
    assert aggregate_forecast_stats(forecasts=forecasts) == stats
