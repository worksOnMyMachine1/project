# Open-Meteo DWD 

A small client that calls the Open-Meteo DWD ICON API using raw `requests`.

## Install

From the repository root:

```bash
pip install -r requirements.txt
```

## Run the example

From the repository root:

```bash
python -m weather_client.example
```

The example requests a two-day hourly forecast for the sample Berlin coordinates. The client returns Open-Meteo's JSON response as a Python dictionary.


## API details

Documentation: <https://open-meteo.com/en/docs/dwd-api>
