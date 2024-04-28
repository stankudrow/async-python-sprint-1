import pytest

from src.client import YandexWeatherClient, YandexWeatherAPIError
from src.utils import CITIES


def test_get_forecast_for_a_city():
    city_for_test = "moscow"

    res = YandexWeatherClient.get_forecast_by_city_name(city_for_test)

    info = res["info"]

    assert info["geoid"] == 213
    assert info["tzinfo"]["abbr"] == "MSK"


def test_get_unknown_city():
    with pytest.raises(YandexWeatherAPIError):
        YandexWeatherClient.get_forecast_by_city_name("1")
