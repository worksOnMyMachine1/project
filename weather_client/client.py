from typing import Any

import requests

from .decorator import retry, timing
from .exceptions import WeatherAPIError


class OpenMeteoClient:

    BASE_URL = "https://api.open-meteo.com/v1/dwd-icon"
    RETRY_ATTEMPTS = 3

    def __init__(self, timeout: float = 10.0) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be greater than 0")
        self.timeout = timeout

    def get_current_weather(
        self,
        latitude: float,
        longitude: float,
    ) -> dict[str, Any]:
        params = self._location_params(latitude, longitude)
        params.update(
            {
                "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
                "timezone": "auto",
            }
        )
        return self._get_weather(params)

    def get_hourly_forecast(
        self,
        latitude: float,
        longitude: float,
        forecast_days: int = 7,
    ) -> dict[str, Any]:
        self._validate_forecast_days(forecast_days)
        params = self._location_params(latitude, longitude)
        params.update(
            {
                "hourly": "temperature_2m,precipitation,wind_speed_10m",
                "forecast_days": forecast_days,
                "timezone": "auto",
            }
        )
        return self._get_weather(params)


    @staticmethod
    def _location_params(
        latitude: float,
        longitude: float,
    ) -> dict[str, float | str | int]:
        if not -90 <= latitude <= 90:
            raise ValueError("latitude must be between -90 and 90")
        if not -180 <= longitude <= 180:
            raise ValueError("longitude must be between -180 and 180")
        return {"latitude": latitude, "longitude": longitude}

    @staticmethod
    def _validate_forecast_days(forecast_days: int) -> None:
        if not 1 <= forecast_days <= 10:
            raise ValueError("forecast_days must be between 1 and 10")

    @timing
    def _get_weather(self, params: dict[str, float | str | int]) -> dict[str, Any]:
        try:
            return self._send_request(params)
        except (requests.Timeout, requests.ConnectionError) as error:
            raise WeatherAPIError(
                f"Open-Meteo could not be reached after {self.RETRY_ATTEMPTS} attempts"
            ) from error
        except requests.RequestException as error:
            raise WeatherAPIError("The Open-Meteo request failed") from error

    @retry(
        times=3,
        delay=1.0,
        exceptions=(requests.Timeout, requests.ConnectionError),
    )
    def _send_request(self, params: dict[str, float | str | int]) -> dict[str, Any]:
        response = requests.get(self.BASE_URL, params=params, timeout=self.timeout)

        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            raise WeatherAPIError(
                f"Open-Meteo returned HTTP {response.status_code}"
            ) from error

        try:
            data: Any = response.json()
        except ValueError as error:
            raise WeatherAPIError("Open-Meteo returned invalid JSON") from error

        if not isinstance(data, dict):
            raise WeatherAPIError("Open-Meteo returned an unexpected response")

        return data
