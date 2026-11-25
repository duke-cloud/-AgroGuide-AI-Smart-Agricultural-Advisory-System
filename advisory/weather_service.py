"""
Weather service — fetches current conditions and 7-day forecast.
Falls back to simulated data if API key is not set.
"""
import requests
from django.conf import settings

OWM_BASE = "https://api.openweathermap.org/data/2.5"

def get_weather(lat, lon):
    """Current weather from OpenWeatherMap (or simulated fallback)."""
    key = getattr(settings, 'OPENWEATHER_API_KEY', '')
    if not key or key == 'YOUR_OPENWEATHER_API_KEY':
        return _simulated_weather(lat, lon)
    try:
        url = f"{OWM_BASE}/weather?lat={lat}&lon={lon}&appid={key}&units=metric"
        r   = requests.get(url, timeout=5)
        if r.status_code == 200:
            return _parse_current(r.json())
    except Exception:
        pass
    return _simulated_weather(lat, lon)

def get_forecast(lat, lon):
    """7-day forecast (or simulated fallback)."""
    key = getattr(settings, 'OPENWEATHER_API_KEY', '')
    if not key or key == 'YOUR_OPENWEATHER_API_KEY':
        return _simulated_forecast()
    try:
        url = f"{OWM_BASE}/forecast?lat={lat}&lon={lon}&appid={key}&units=metric&cnt=40"
        r   = requests.get(url, timeout=5)
        if r.status_code == 200:
            return _parse_forecast(r.json())
    except Exception:
        pass
    return _simulated_forecast()

def _parse_current(data):
    return {
        'temp':        round(data['main']['temp'], 1),
        'feels_like':  round(data['main']['feels_like'], 1),
        'humidity':    data['main']['humidity'],
        'pressure':    data['main']['pressure'],
        'description': data['weather'][0]['description'].title(),
        'icon':        data['weather'][0]['icon'],
        'wind_speed':  round(data['wind']['speed'] * 3.6, 1),  # m/s → km/h
        'rainfall_1h': data.get('rain', {}).get('1h', 0),
        'city':        data.get('name', ''),
        'simulated':   False,
    }

def _parse_forecast(data):
    days = {}
    for item in data['list']:
        date = item['dt_txt'][:10]
        if date not in days:
            days[date] = {'temps':[], 'rain':0, 'description': item['weather'][0]['description'].title()}
        days[date]['temps'].append(item['main']['temp'])
        days[date]['rain'] += item.get('rain', {}).get('3h', 0)
    result = []
    for date, d in list(days.items())[:7]:
        result.append({
            'date': date,
            'high': round(max(d['temps']), 1),
            'low':  round(min(d['temps']), 1),
            'rain': round(d['rain'], 1),
            'description': d['description'],
        })
    return result

def _simulated_weather(lat, lon):
    import random, math
    base_temp = 28 + 5 * math.sin(lat * 0.1)
    return {
        'temp':        round(base_temp + random.uniform(-3, 5), 1),
        'feels_like':  round(base_temp + random.uniform(-1, 4), 1),
        'humidity':    random.randint(55, 80),
        'pressure':    random.randint(1008, 1018),
        'description': random.choice(['Partly Cloudy','Mostly Sunny','Light Rain Showers','Overcast']),
        'icon':        '02d',
        'wind_speed':  round(random.uniform(8, 22), 1),
        'rainfall_1h': round(random.uniform(0, 15), 1),
        'city':        'Abuja',
        'simulated':   True,
    }

def _simulated_forecast():
    import random
    days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    icons = ['☀️','⛅','🌦️','🌧️','🌤️']
    return [
        {
            'date': f'Day {i+1}',
            'high': random.randint(28, 36),
            'low':  random.randint(20, 24),
            'rain': round(random.uniform(0, 70), 1),
            'description': random.choice(['Sunny','Partly Cloudy','Light Rain','Heavy Rain','Clear']),
            'icon': random.choice(icons),
        }
        for i in range(7)
    ]
