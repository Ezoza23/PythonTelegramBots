import requests
import tempfile
import shutil
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

# ---------- WEATHER FUNCTIONS ----------

API_KEY = "850a76c5fffd68ec5940b8892d0379a8"  # replace with your valid key

def kelvin_to_celsius(k):
    return k - 273.15

def get_weather(city, days):
    """
    Returns a tuple: (message string, list of (icon_url for each day))
    Aggregates 3-hour intervals into daily summaries.
    """
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}"
    response = requests.get(url)
    info = response.json()

    if info.get("cod") != "200":
        return f"Error: {info.get('message', 'Unable to fetch weather')}", []

    # Collect daily data
    daily_data = {}
    for item in info['list']:
        dt_txt = item['dt_txt']  # e.g., '2026-03-05 12:00:00'
        date_str = dt_txt.split()[0]  # '2026-03-05'
        temp = kelvin_to_celsius(item['main']['temp'])
        condition = item['weather'][0]['main']
        description = item['weather'][0]['description']
        icon = item['weather'][0]['icon']
        daily_data.setdefault(date_str, []).append({
            "temp": temp,
            "condition": condition,
            "description": description,
            "icon": icon
        })

    # Prepare message and icon URLs
    message = f"Weather forecast for {city.upper()}:\n\n"
    icon_urls = []
    for i, (date, forecasts) in enumerate(daily_data.items()):
        if i >= days:
            break
        temps = [f['temp'] for f in forecasts]
        conditions = [f['condition'] for f in forecasts]
        descriptions = [f['description'] for f in forecasts]

        avg_temp = sum(temps)/len(temps)
        main_condition = conditions[0]  # take the first interval's main condition
        main_description = descriptions[0]
        icon_code = forecasts[0]['icon']
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        icon_urls.append(icon_url)

        message += f"📅 {date}\n"
        message += f"Temp: {avg_temp:.1f}°C\n"
        message += f"Weather: {main_condition} - {main_description}\n\n"

    return message, icon_urls

# ---------- TELEGRAM HANDLERS ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! Send me a city name and number of days.\nExample: Tashkent 3"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.split()
    if len(text) < 2:
        await update.message.reply_text("Please send city name and number of days.")
        return

    city = text[0]
    try:
        days = int(text[1])
        if days < 1 or days > 5:
            await update.message.reply_text("Number of days must be between 1 and 5.")
            return
    except ValueError:
        await update.message.reply_text("Number of days must be an integer.")
        return

    result_text, icon_urls = get_weather(city, days)
    if not icon_urls:
        await update.message.reply_text(result_text)
        return

    # Send forecast day by day with temporary icon
    for icon_url in icon_urls:
        response = requests.get(icon_url, stream=True)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            shutil.copyfileobj(response.raw, tmp_file)
            icon_path = tmp_file.name

        await update.message.reply_photo(photo=open(icon_path, "rb"), caption=result_text)

        os.remove(icon_path)

# ---------- MAIN ----------

TOKEN = "8639212152:AAGhwFkaFFg6OAVdyW1hdkQbvAE5R85hJjg"

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot is running...")
app.run_polling()