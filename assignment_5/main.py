import requests
import json

def json_read(path):
    with open(path, 'r') as f:
        data=json.load(f)
        return data

def get_weather(city, cnt):
    api_key="850a76c5fffd68ec5940b8892d0379a8"
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&cnt={cnt}&appid={api_key}"
    response=requests.get(url)
    info=response.json()

    with open("weather.json", "w") as file:
        json.dump(info, file, indent=4)

    weather_info=json_read("weather.json")
    s=""
    print(f"{city.upper()}: {cnt} days weather info!\n")
    for d, i in enumerate(weather_info['list'], 1):

        time = i['dt_txt']
        temp_c = i['main']['temp'] - 273.15
        feels_like_c = i['main']['feels_like'] - 273.15
        condition = i['weather'][0]['main']
        description = i['weather'][0]['description']
        wind_speed = i['wind']['speed']
        humidity = i['main']['humidity']
        rain = i.get('rain', {}).get('3h', 0)
        icon_code = i['weather'][0]['icon']
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

        s+=f"""DAY {d}:
{time}
Temp: {temp_c:.1f}°C (feels like {feels_like_c:.1f}°C)
Weather: {condition} - {description}
Wind: {wind_speed} m/s | Humidity: {humidity}% | Rain: {rain} mm
{icon_url}\n"""
    return s



print(get_weather('Tashkent', 2))
