import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# La clave API de AccuWeather
API_KEY = 'vPG6pI46wYqObrHyATsVIyJbyPNqUoWZ'
BASE_URL = "http://dataservice.accuweather.com"
CITY_SEARCH_URL = f"{BASE_URL}/locations/v1/cities/search"
FORECAST_URL = f"{BASE_URL}/forecasts/v1/daily/5day/"


# Función para obtener el ID de la ciudad
def get_city_id(city_name):
    params = {
        'q': city_name,
        'apikey': API_KEY
    }

    response = requests.get(CITY_SEARCH_URL, params=params)

    if response.status_code != 200:
        return None

    data = response.json()

    if not data:
        return None

    # Retorna el ID de la primera ciudad que encuentre
    city_id = data[0]['Key']
    return city_id


# Función para obtener el pronóstico del tiempo
def get_weather_forecast(city_id):
    params = {
        'apikey': API_KEY,
        'metric': 'true'
    }

    response = requests.get(f"{FORECAST_URL}{city_id}", params=params)

    if response.status_code != 200:
        return None

    return response.json()


# Función para calcular las temperaturas
def calculate_temperatures(weather_data):
    if not weather_data:
        return None

    temperatures = {
        "min": float('inf'),
        "max": float('-inf'),
        "sum": 0,
        "count": 0
    }

    for day in weather_data['DailyForecasts']:
        temperatures["min"] = min(temperatures["min"], day['Temperature']['Minimum']['Value'])
        temperatures["max"] = max(temperatures["max"], day['Temperature']['Maximum']['Value'])
        temperatures["sum"] += (day['Temperature']['Minimum']['Value'] + day['Temperature']['Maximum']['Value']) / 2
        temperatures["count"] += 1

    temperatures["avg"] = temperatures["sum"] / temperatures["count"]

    return temperatures


# Endpoint para obtener el pronóstico del clima de una ciudad
@app.route('/weather', methods=['GET'])
def weather():
    city_name = request.args.get('city')

    if not city_name:
        return jsonify({'error': 'City name is required'}), 400

    # Obtener el ID de la ciudad
    city_id = get_city_id(city_name)

    if not city_id:
        return jsonify({'error': 'City not found'}), 404

    # Obtener el pronóstico del clima para los próximos 5 días
    weather_data = get_weather_forecast(city_id)

    if not weather_data:
        return jsonify({'error': 'Weather data not found'}), 500

    # Calcular las temperaturas
    temperatures = calculate_temperatures(weather_data)

    if not temperatures:
        return jsonify({'error': 'Could not calculate temperatures'}), 500

    # Devolver los resultados
    result = {
        'city': city_name,
        'temperatures': {
            'min': temperatures["min"],
            'max': temperatures["max"],
            'avg': temperatures["avg"]
        }
    }
    return jsonify(result)


# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)