import logging
from concurrent.futures import (
    ProcessPoolExecutor,
    ThreadPoolExecutor,
    as_completed,
    Future,
)
from json import dump
from typing import Any

from src.core import fetch_forecasts, select_forecast_days, analyse_forecast_days
from src.exceptions import YandexWeatherAPIError
from src.types_ import FORECAST
from src.utils import check_python_version, FETCH_TIMEOUT


def fetch_forecasts_task(
    city_name: str, timeout: None | float
) -> tuple[str, None | list[FORECAST]]:
    """Fetches the forecasts for the city."""

    forecasts = None
    try:
        forecasts = fetch_forecasts(city=city_name, timeout=timeout)
    except YandexWeatherAPIError as e:
        msg = f"Cannot request data for the city {city_name!r}: {e}"
        logging.error(msg)
    except KeyError as e:
        msg = f'The key "forecasts" does not exist for the city {city_name!r}: {e}'
        logging.error(msg)
    return (city_name, forecasts)


def analyse_forecasts_task(city_name: str, forecasts: list[FORECAST]):
    """Returns the analysed forecasts for the city."""

    info = None
    try:
        days = select_forecast_days(forecasts=forecasts)
        info = analyse_forecast_days(days=days)
    except Exception as e:
        print(f"EXC = {e}")
    return (city_name, info)


def main_task(city_names: list[str], file_object):
    check_python_version()

    cities = set(cname.lower() for cname in city_names)
    final_results: dict[str, dict[str, Any]] = {}
    with ProcessPoolExecutor() as proc_pool, ThreadPoolExecutor() as thread_pool:
        # fetching data from the YandexWeatherAPI
        fetched_futures: list[Future] = [
            thread_pool.submit(fetch_forecasts_task, city_name, FETCH_TIMEOUT)
            for city_name in cities
        ]

        # analysing non-None fetched data for a city
        analysed_futures = []
        for future in as_completed(
            fetched_futures
        ):  # timeout=FETCH_TIMEOUT * len(cities)
            city, forecasts = future.result()
            if not forecasts:
                logging.warning(f"no forecasts for the city {city!r}")
                continue
            analysed_futures.append(
                proc_pool.submit(analyse_forecasts_task, city, forecasts)
            )

        # aggregating the successfully analysed results
        for future in as_completed(analysed_futures):
            city, analysed_result = future.result()
            if not analysed_result:
                logging.warning(f"no analysed data for the city {city!r}")
                continue
            final_results[city] = analysed_result

    # the results are already aggregated
    with file_object as fout:
        dump(obj=final_results, fp=fout, indent=2)
