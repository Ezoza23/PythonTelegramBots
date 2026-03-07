import gspread
from google.oauth2.service_account import Credentials
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import matplotlib.pyplot as plt
# ---------- GOOGLE SHEETS SETUP ----------
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)

sheet_id = "1a6BpkwVXmRdGytGDG1q4SbAjiqSLDlPsuc9A7TLvfdE"
spreadsheet = client.open_by_key(sheet_id)
worksheet = spreadsheet.worksheet("Sheet1")


def attendance(name, surname):
    data = worksheet.get_all_values()
    column = data[0][2:]
    info = []

    for i in range(1, len(data)):
        if data[i][0] == name and data[i][1] == surname:
            info = data[i][2:]

            break
    else:
        return "Student not found."

    result = f"{name} {surname}\n\n"
    yes=0
    no=0
    for i in range(len(column) - 2):
        if info[i] == '1':
            result += column[i] + " ✅\n"
            yes+=1
        else:
            result += column[i] + " ❌\n"
            no+=1
    plt.figure()
    plt.pie([yes, no], labels=["Present", "Absent"], colors=["White", "Black"], autopct='%1.1f%%')
    plt.title(f"Attendance ({name}, {surname})")

    plt.savefig(f'attendance.png')
    plt.close()
    return result


# ---------- TELEGRAM BOT HANDLERS ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send student's name and surname like this:\n\nJohn Doe"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.split()

    if len(text) < 2:
        await update.message.reply_text("Please send Name and Surname.")
        return

    name = text[0].title()
    surname = text[1].title()

    result = attendance(name, surname)
    await update.message.reply_text(result)
    if result!="Student not found.":
        with open(f'attendance.png', 'rb') as chart_file:
            await update.message.reply_photo(chart_file)

# ---------- MAIN ----------

TOKEN = "8639212152:AAGhwFkaFFg6OAVdyW1hdkQbvAE5R85hJjg"

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot is running...")
app.run_polling()