import requests
import tempfile
import os
from collections import Counter
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import pycountry
import json

# -------- CONFIG --------
API_KEY = "850a76c5fffd68ec5940b8892d0379a8"
TOKEN = "8639212152:AAGhwFkaFFg6OAVdyW1hdkQbvAE5R85hJjg"

# -------- WEATHER LOGIC --------
def json_read(path):
    with open(path, 'r') as f:
        data=json.load(f)
        return data

def kelvin_to_celsius(k):
    return k - 273.15


def get_weather(city, days=1):

    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}"
    response = requests.get(url)
    data = response.json()
    with open("weather.json", "w") as file:
        json.dump(data, file, indent=4)

    weather_info=json_read("weather.json")
    print(weather_info[''])

    if data.get("cod") != "200":
        return {"error": data.get("message", "City not found")}

    # country info
    country_code = data["city"]["country"]
    country = pycountry.countries.get(alpha_2=country_code)
    country_name = country.name if country else country_code
    population=data["city"]["population"]
    wiki_link = f"https://en.wikipedia.org/wiki/{country_name.replace(' ', '_')}"
    flag_url = f"https://flagcdn.com/w320/{country_code.lower()}.png"

    daily = {}

    for item in data["list"]:
        date = item["dt_txt"].split()[0]

        temp = kelvin_to_celsius(item["main"]["temp"])
        condition = item["weather"][0]["main"]
        description = item["weather"][0]["description"]
        icon = item["weather"][0]["icon"]

        if date not in daily:
            daily[date] = []

        daily[date].append({
            "temp": temp,
            "condition": condition,
            "description": description,
            "icon": icon
        })

    results = []

    for i, (date, values) in enumerate(daily.items()):

        if i >= days:
            break

        temps = [v["temp"] for v in values]
        conditions = [v["condition"] for v in values]
        descriptions = [v["description"] for v in values]

        avg_temp = sum(temps) / len(temps)

        main_condition = Counter(conditions).most_common(1)[0][0]
        main_description = Counter(descriptions).most_common(1)[0][0]

        icon_code = values[0]["icon"]
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

        caption = (
            f"📅 {date}\n"
            f"Temperature: {avg_temp:.1f}°C\n"
            f"Weather: {main_condition} - {main_description}"
        )

        results.append((caption, icon_url))

    return {
        "country": country_name,
        "wiki": wiki_link,
        "flag": flag_url,
        "days": results
    }


# -------- TELEGRAM HANDLERS --------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.split()

    if len(text) == 0:
        await update.message.reply_text("Example: London or London 3")
        return

    # Check if the last part is a number
    if text[-1].isdigit():

        days = int(text[-1])
        city = " ".join(text[:-1])

        if days < 1 or days > 5:
            await update.message.reply_text("Days must be between 1 and 5.")
            return

    else:
        # user sent only city
        city = " ".join(text)
        days = 1

    weather = get_weather(city, days)

    if "error" in weather:
        await update.message.reply_text(weather["error"])
        return

    # send country flag
    await update.message.reply_photo(
        photo=weather["flag"],
        caption=f"Country: {weather['country']}\n{weather['wiki']}"
    )

    # send forecasts
    for caption, icon_url in weather["days"]:

        response = requests.get(icon_url)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
            f.write(response.content)
            temp_path = f.name

        with open(temp_path, "rb") as img:
            await update.message.reply_photo(photo=img, caption=caption)

        os.remove(temp_path)
# -------- START COMMAND --------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send a city name or city with number of days.\nExample:\nLondon\nLondon 3"
    )

# -------- MAIN --------

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot running...")
app.run_polling()