import pytest

from src.core import fetch_forecasts 
from src.exceptions import YandexWeatherAPIError


def test_get_forecast_for_a_city():
    city_for_test = "moscow"

    res = fetch_forecasts(city_for_test)

    assert isinstance(res, list)


def test_get_unknown_city():
    with pytest.raises(YandexWeatherAPIError):
        fetch_forecasts("1")
