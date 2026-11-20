from .client import OpenMeteoClient


def main() -> None:
    client = OpenMeteoClient(timeout=10)

    # Example coordinates from the Open-Meteo documentation (Berlin).
    forecast = client.get_hourly_forecast(
        latitude=52.52,
        longitude=13.41,
        forecast_days=2,
    )

    print("Coordinates:", forecast.get("latitude"), forecast.get("longitude"))
    print("Hourly forecast:", forecast.get("hourly", {}))


if __name__ == "__main__":
    main()