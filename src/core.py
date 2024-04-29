from typing import Any

import httpx

from src.exceptions import YandexWeatherAPIError
from src.types_ import FORECAST, HourInfo, DayInfo
from src.utils import get_url_by_city_name, FETCH_TIMEOUT, SUITABLE_CONDITIONS


httpx_client = httpx.Client()


def fetch_forecasts(
    city: str, timeout: None | float = FETCH_TIMEOUT
) -> None | list[FORECAST]:
    """Returns the forecasts for the city.

    Args:
        city: str - the name of the city
        timeout: None | float - the timeout for the request

    Returns:
        the forecasts for URL mapped to the city name
    """

    try:
        url = get_url_by_city_name(city)
    except KeyError as e:
        raise YandexWeatherAPIError from e

    response = httpx_client.get(url=url, timeout=timeout)
    if (status := response.status_code) != httpx.codes.OK:
        msg = f"The request for {url!r} has failed: " f"status={status} is not OK"
        raise YandexWeatherAPIError(msg)

    result = response.json()
    return result["forecasts"] if result else None


def select_forecast_days(forecasts: list[FORECAST]) -> list[DayInfo]:
    """Extracts the data for the further analysis.

    This routine defines selection conditions
    """

    days_info: list[DayInfo] = []
    for forecast in forecasts:
        date = forecast["date"]
        hours = forecast["hours"]
        hours_info: list[HourInfo] = []
        for hour_forecast in hours:
            hour = int(hour_forecast["hour"])
            if 9 <= hour <= 19:
                cond = hour_forecast["condition"]
                if cond in SUITABLE_CONDITIONS:
                    temp = hour_forecast["temp"]
                    hours_info.append(
                        HourInfo(hour=hour, temperature=temp, condition=cond)
                    )
        days_info.append(DayInfo(date_=date, hours=hours_info))
    return days_info


def analyse_forecast_days(days: list[DayInfo]) -> list[dict[str, Any]]:
    """Results in analysed forecast data."""

    results: list[dict[str, Any]] = []
    for day in days:
        date_ = day.date_
        hours, start_hour, end_hour = None, None, None
        avg_temp = None
        hours_count, rel_cond_hours = 0, 0
        if hours := day.hours:
            hours = sorted(hours, key=lambda hi: hi.hour)  # type: ignore
            start_hour = hours[0].hour
            end_hour = hours[-1].hour
            hours_count = rel_cond_hours = len(hours)
            temp = sum(h.temperature for h in hours)  # type: ignore
            avg_temp = temp / rel_cond_hours if rel_cond_hours else None
            if avg_temp:
                avg_temp = round(avg_temp, 3)
        date_ = date_.isoformat() if date_ else date_  # type: ignore
        results.append(
            {
                "date": date_,
                "hours_start": start_hour,
                "hours_end": end_hour,
                "hours_count": hours_count,
                "temp_avg": avg_temp,
                "relevant_cond_hours": rel_cond_hours,
            }
        )
    return results
