import json
import logging
from typing import Any
from http import HTTPStatus
from urllib.request import urlopen

from src.utils import CITIES

logger = logging.getLogger()


class YandexWeatherAPIError(Exception):
    """Yandex Weather HTTP Request Error."""


class YandexWeatherClient:
    """Yandex Weather HTTP Client."""

    def _request(url: str) -> Any:
        """Base request method"""

        with urlopen(url) as response:
            res = response.read().decode("utf-8")
            if (status := response.status) != HTTPStatus.OK:
                msg = (
                    f"The request for {url!r} has failed: " f"status={status} is not OK"
                )
                raise YandexWeatherAPIError(msg)
        return json.loads(res)

    @staticmethod
    def get_forecast_by_city_name(city_name: str):
        """Returns the forecast for a city."""

        try:
            url = CITIES[city_name.upper()]
        except KeyError as ke:
            raise YandexWeatherAPIError from ke
        return YandexWeatherClient._request(url)
