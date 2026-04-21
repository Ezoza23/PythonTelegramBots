import random
import json
import mysql.connector as mc
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8639212152:AAGhwFkaFFg6OAVdyW1hdkQbvAE5R85hJjg"

# -------- DB --------
mydb = mc.connect(
    host="localhost",
    user="root",
    password="Yournewpassword123!",
    port=3307,
    database="users"
)
mycursor = mydb.cursor()

# -------- SESSION --------
user_sessions = {}

# -------- JSON --------
def json_read(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

# -------- DB FUNCTIONS --------
def get_user_history(user_id):
    mycursor.execute("SELECT question_id FROM questions_history WHERE user_id=%s", (user_id,))
    return [row[0] for row in mycursor.fetchall()]

def get_user_from_db(user_id):
    mycursor.execute(
        "SELECT user_id, language, surname, name, username, number_of_questions, points, right_answers, status, percent FROM users WHERE user_id=%s",
        (user_id,))
    row = mycursor.fetchone()
    if row:
        return {
            "user_id": row[0],
            "language": row[1],
            "surname": row[2],
            "name": row[3],
            "username": row[4],
            "number_of_questions": row[5],
            "points": row[6],
            "right_answers": row[7],
            "status": row[8],
            "percent": row[9],
            "questions_history": get_user_history(user_id)
        }
    return None

def add_user(user_id, language, surname, name, username,
             number_of_questions, points, right_answers,
             history, status, percent):
    # INSERT OR UPDATE
    mycursor.execute("""
        INSERT INTO users (user_id, language, surname, name, username,
                           number_of_questions, points, right_answers,
                           status, percent)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
            language=%s,
            surname=%s,
            name=%s,
            username=%s,
            number_of_questions=%s,
            points=%s,
            right_answers=%s,
            status=%s,
            percent=%s
    """, (
        user_id, language, surname, name, username,
        number_of_questions, points, right_answers,
        status, percent,
        # update values
        language, surname, name, username,
        number_of_questions, points, right_answers,
        status, percent
    ))

    # insert new history (without deleting old history)
    for q_id in history:
        mycursor.execute(
            "INSERT IGNORE INTO questions_history (user_id, question_id) VALUES (%s,%s)",
            (user_id, q_id)
        )

    mydb.commit()

# -------- TEXTS --------
def get_text(lang, key, s="Fail"):
    texts = {
        "start": {"рус": "Выберите язык:", "кирилл": "Тилни танланг:", "lotin": "Tilni tanlang:"},
        "surname": {"рус": "Пожалуйста, введите вашу фамилию:", "кирилл": "Илтимос, фамилиянгизни киритинг:", "lotin": "Iltimos, familyangizni kiriting:"},
        "name": {"рус": "Пожалуйста, введите вашу имю:", "кирилл": "Илтимос, исмингизни киритинг:", "lotin": "Iltimos, ismingizni kiriting:"},
        "username": {"рус": "Пожалуйста, введите вашу никнейм:", "кирилл": "Илтимос, никнеймингизни киритинг:",
                 "lotin": "Iltimos, nikneymingizni kiriting:"},
        "questions": {"рус": "Сколько вопросов вы хотите решить? (введите число):", "кирилл": "Нечта саволга жавоб беришни хохлайсиз? (ракам киритинг):", "lotin": "Nechta savolga javob berishni xohlaysiz? (raqam kiriting):"},
        "invalid": {"рус": "Введите число", "кирилл": "Ракам киритинг", "lotin": "Raqam kiriting"},
        "finish": {"рус": "Результат", "кирилл": "Натижа", "lotin": "Natija"},
        "status": {"рус": "Зачёт" if s=="Pass" else "Незачёт", "кирилл": "Ўтди" if s=="Pass" else "Ўтмади", "lotin": "O'tdi" if s=="Pass" else "O'tmadi"},
        "skip": {"рус": "Пропустить", "кирилл": "Утказиш", "lotin": "O'tkazish"},
        "incorrect_intro": {"рус": "Неправильно отвеченные вопросы:", "кирилл": "Нотўғри жавоб берилган саволлар:", "lotin": "Noto'g'ri javoblar:"}
    }
    return texts[key][lang]

# -------- QUESTION --------
async def question(update, data, l):
    if data['media']['exist']:
        with open(f"Autotest/{data['media']['name']}.png", "rb") as img:
            await update.message.reply_photo(photo=img)

    text = f"Q {data['id']}: {data['question']}\n"

    options = data["choises"] if l in ["рус", "кирилл"] else data["choices"]

    keyboard = [[str(i+1)] for i in range(len(options))]
    keyboard.append([get_text(l, "skip")])

    for i, opt in enumerate(options, 1):
        text += f"\n{i}. {opt['text']}"

    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# -------- ANSWER --------
def answer(user_answer, data, l):
    try:
        answer = int(user_answer)
        if l == 'рус':
            return 'Правильно' if data["choises"][answer-1]["answer"] else 'Неправильно'
        elif l == 'кирилл':
            return 'Тугри' if data["choises"][answer-1]["answer"] else 'Нотугри'
        else:
            return "To'g'ri" if data["choices"][answer-1]["answer"] else "Noto'g'ri"
    except:
        return None

# -------- START --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    db_user = get_user_from_db(user_id)
    if db_user:
        user_sessions[user_id] = {"new_user": db_user, "step": "questions"}
        await update.message.reply_text(get_text(db_user["language"], "questions"))
        return

    keyboard = [["рус", "кирилл", "lotin"]]
    await update.message.reply_text(
        """Привет! Добро пожаловать в Авто тест бот 
Salom! Auto test botiga xush kelibsiz
Салом! Авто тест ботига хуш келибсиз

Какой язык вы предпочитаете?
Qaysi til sizga ma'qul?
Кайси тил сизга ма'кул?: """,
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
def get_leaderboard_text(current_user_id):
    mycursor.execute("SELECT user_id, username, points FROM users ORDER BY points DESC;")
    rows = mycursor.fetchall()

    if not rows:
        return "No data yet."

    text = "🏆 Leaderboard:\n\n"
    medals = ["🥇", "🥈", "🥉"]

    for i, row in enumerate(rows, start=1):
        user_id, username, points = row
        username = username if username else "NoName"

        prefix = medals[i-1] if i <= 3 else f"{i}."

        if user_id == current_user_id:
            text += f"{prefix} 👉 {username} — {points} pts\n"
        else:
            text += f"{prefix} {username} — {points} pts\n"

    return text

# -------- MAIN HANDLER --------
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    # -------- LEADERBOARD BUTTON --------
    if text == "🏆 Leaderboard":
        leaderboard = get_leaderboard_text(user_id)
        await update.message.reply_text(leaderboard)
        return
    session = user_sessions.get(user_id)

    # -------- LANGUAGE SELECTION OR NEW USER --------
    if not session:
        if text in ["рус", "кирилл", "lotin"]:
            new_user = {
                "user_id": user_id,
                "language": text,
                "surname": '',
                "name": '',
                "username": update.message.from_user.username,
                "number_of_questions": 0,
                "questions_history": [],
                "points": 0,
                "right_answers": 0,
                "status": "Failed",
                "percent": 0
            }
            user_sessions[user_id] = {"new_user": new_user, "step": "surname"}
            await update.message.reply_text(get_text(text, "surname"))
        return

    new_user = session["new_user"]
    lang = new_user["language"]

    # -------- SURNAME --------
    if session["step"] == "surname":
        new_user["surname"] = text.lower()
        session["step"] = "name"
        await update.message.reply_text(get_text(lang, "name"))
        return

    # -------- NAME --------
    if session["step"] == "name":
        new_user["name"] = text.lower()
        session["step"] = "questions"
        await update.message.reply_text(get_text(lang, "questions"))
        return

    # -------- QUESTIONS --------
    if session["step"] == "questions":
        try:
            questions_no = int(text)
        except:
            await update.message.reply_text(get_text(lang, "invalid"))
            return

        # load content
        if lang == 'кирилл':
            content = json_read("Autotest/uzkiril.json")
        elif lang == 'рус':
            content = json_read("Autotest/rus.json")
        else:
            content = json_read("Autotest/uzlotin.json")

        # exclude already answered
        used_questions = new_user["questions_history"]
        available_questions = [q for q in content if q['id'] not in used_questions]

        random.shuffle(available_questions)
        session["content"] = available_questions[:questions_no]

        session["current"] = 0
        session["right"] = 0
        session["wrong"] = 0
        session["skip"] = 0
        session['points']=0
        session["incorrect"] = []
        session["step"] = "quiz"

        await question(update, session["content"][0], lang)
        return

    # -------- QUIZ --------
    if session["step"] == "quiz":
        current = session["current"]
        content = session["content"]

        # ---- SKIP ----
        if text == get_text(lang, "skip"):
            session["skip"] += 1
            session["current"] += 1
        else:
            res = answer(text, content[current], lang)
            if res is None:
                await update.message.reply_text(get_text(lang, "invalid"))
                return

            if res in ['Правильно', 'Тугри', "To'g'ri"]:
                session["right"] += 1
                session['points']+=1
            else:
                session["wrong"] += 1
                session['points']-=0.25
                session["incorrect"].append(content[current]["question"])

            await update.message.reply_text(res)
            new_user["questions_history"].append(content[current]["id"])
            session["current"] += 1

        # ---- END ----
        if session["current"] >= len(session["content"]):
            # update cumulative totals in DB
            total_questions = new_user["number_of_questions"] + len(session["content"])
            total_right = new_user["right_answers"] + session["right"]
            total_point=new_user["points"]+session['points']
            percent = round((100 * total_right) / total_questions, 2)
            status = "Pass" if percent >= 60 else "Fail"


            add_user(
                new_user["user_id"],
                new_user["language"],
                new_user["surname"],
                new_user["name"],
                new_user["username"],
                total_questions,
                total_point,
                total_right,
                new_user["questions_history"],
                status,
                percent
            )

            # show session-specific results
            result_text = (
                f"{get_text(lang,'finish', status)}\n\n"
                f"✔ {session['right']} (correct in this quiz)\n"
                f"✖ {session['wrong']} (incorrect in this quiz)\n"
                f"➜ {session['skip']} (skipped)\n"
                f"📊 {round((100*session['right']/len(session['content'])),2)}% (this quiz)\n"
                f"📌 {status} (overall status)"
            )
            keyboard = [["🏆 Leaderboard"]]

            await update.message.reply_text(
                result_text,
                reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            )

            if session["incorrect"]:
                await update.message.reply_text(get_text(lang,"incorrect_intro"))
                for q in session["incorrect"]:
                    await update.message.reply_text(q)

            del user_sessions[user_id]

        else:
            await question(update, content[session["current"]], lang)

# -------- MAIN --------
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle))
    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()