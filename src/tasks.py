import logging
from collections import defaultdict
from concurrent.futures import (
    ProcessPoolExecutor,
    ThreadPoolExecutor,
    as_completed,
    Future,
)
from json import dump
from typing import Any

from src.core import fetch_forecasts, aggregate_forecast_stats
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


def aggregate_forecasts_task(city_name: str, forecasts: list[FORECAST]):
    """Returns the analysed forecasts for the city."""

    stats = None
    try:
        stats = aggregate_forecast_stats(forecasts=forecasts)
    except Exception as e:
        msg = f"DataAggregationError: {e}"
        logging.error(msg)
    result = {"days": stats}
    return (city_name, result)


def analyse_forecasts_task(cities_days: dict[str, dict[str, Any]]) -> list[str]:
    """Returns the list of favourable cities."""

    results: dict[tuple[float, int], list[str]] = defaultdict(list)
    for city, analytics in cities_days.items():
        days: list[dict[str, Any]] = analytics["days"]
        total_temp: float = 0.0
        total_conds: int = 0
        for day in days:
            atemp = day["temp_avg"]
            conds = day["relevant_cond_hours"]
            if atemp and conds:
                total_temp += atemp
                total_conds += conds
        results[(total_temp, total_conds)].append(city)
    return results[max(results)]


def main_task(city_names: tuple[str], file_object):
    check_python_version()

    if not city_names:
        print("No cities were given. Exit.")
        return

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
                proc_pool.submit(aggregate_forecasts_task, city, forecasts)
            )

        # aggregating the successfully analysed results
        for future in as_completed(analysed_futures):
            city, analysed_result = future.result()
            if not analysed_result:
                logging.warning(f"no analysed data for the city {city!r}")
                continue
            final_results[city] = analysed_result

    # the results are already aggregated
    # so we can write them in the main thread...
    with file_object as fout:
        dump(obj=final_results, fp=fout, indent=2)
        # ...and choose the best cities in the same main thread
        msg = "No cities to analyse. Exit"
        if final_results:
            favourable_cities = analyse_forecasts_task(final_results)
            msg = f"The best city/cities is/are: {favourable_cities}"
        # this code is within the context manager of a file which can be stdout.
        # Otherwise, `ValueError: I/O operation on closed file.`
        print(msg)
