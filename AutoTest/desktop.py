import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import json
import mysql.connector as mc

# -------- DB --------
mydb = mc.connect(
    host="localhost",
    user="root",
    password="Yournewpassword123!",
    port=3307,
    database="users"
)
mycursor = mydb.cursor()

# -------- JSON --------
def json_read(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

# -------- DB FUNCTIONS --------
def get_user_by_name_surname(name, surname):
    mycursor.execute(
        "SELECT * FROM users WHERE name=%s AND surname=%s",
        (name.lower(), surname.lower())
    )
    row = mycursor.fetchone()
    if row:
        # Fetch question history
        mycursor.execute("SELECT question_id FROM questions_history WHERE user_id=%s", (row[0],))
        q_history = [r[0] for r in mycursor.fetchall()]
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
            "questions_history": q_history
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
        "surname": {"рус": "Пожалуйста, введите вашу фамилию:",
                    "кирилл": "Илтимос, фамилиянгизни киритинг:",
                    "lotin": "Iltimos, familyangizni kiriting:"},
        "name": {"рус": "Пожалуйста, введите ваше имя:",
                 "кирилл": "Илтимос, исмингизни киритинг:",
                 "lotin": "Iltimos, ismingizni kiriting:"},
        "username": {"рус": "Пожалуйста, введите ваш никнейм:",
                     "кирилл": "Илтимос, никнеймингизни киритинг:",
                     "lotin": "Iltimos, nikneymingizni kiriting:"},
        "questions": {"рус": "Сколько вопросов вы хотите решить? (введите число):",
                      "кирилл": "Нечта саволга жавоб беришни хохлайсиз? (ракам киритинг):",
                      "lotin": "Nechta savolga javob berishni xohlaysiz? (raqam kiriting):"},
        "invalid": {"рус": "Введите число", "кирилл": "Ракам киритинг", "lotin": "Raqam kiriting"},
        "finish": {"рус": "Результат", "кирилл": "Натижа", "lotin": "Natija"},
        "status": {"рус": "Зачёт" if s=="Pass" else "Незачёт",
                   "кирилл": "Ўтди" if s=="Pass" else "Ўтмади",
                   "lotin": "O'tdi" if s=="Pass" else "O'tmadi"},
        "skip": {"рус": "Пропустить", "кирилл": "Утказиш", "lotin": "O'tkazish"},
        "incorrect_intro": {"рус": "Неправильно отвеченные вопросы:",
                            "кирилл": "Нотўғри жавоб берилган саволлар:",
                            "lotin": "Noto'g'ri javoblar:"}
    }
    return texts[key][lang]

# -------- APP --------
class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # hide main window
        self.load_user()
        self.load_questions()
        self.current_index = 0
        self.right = 0
        self.wrong = 0
        self.skip = 0
        self.incorrect = []
        self.ask_number_of_questions()

    def load_user(self):
        # ask language first
        self.lang = simpledialog.askstring("Language", "Choose language (рус, кирилл, lotin)")
        self.surname = simpledialog.askstring("Surname", get_text(self.lang, "surname"))
        self.name = simpledialog.askstring("Name", get_text(self.lang, "name"))
        db_user = get_user_by_name_surname(self.name, self.surname)
        if db_user:
            # existing user
            self.user_id = db_user["user_id"]
            self.number_of_questions = db_user["number_of_questions"]
            self.right_answers = db_user["right_answers"]
            self.points = db_user["points"]
            self.questions_history = db_user["questions_history"]
            self.username = simpledialog.askstring("Username", get_text(self.lang, "username"))
        else:
            self.user_id = random.randint(10**9, 10**10-1)
            self.number_of_questions = 0
            self.right_answers = 0
            self.points = 0
            self.questions_history = []
            self.username = simpledialog.askstring("Username", get_text(self.lang, "username"))

    def load_questions(self):
        if self.lang == 'кирилл':
            self.all_questions = json_read("Autotest/uzkiril.json")
        elif self.lang == 'рус':
            self.all_questions = json_read("Autotest/rus.json")
        else:
            self.all_questions = json_read("Autotest/uzlotin.json")

    def ask_number_of_questions(self):
        while True:
            try:
                no_q = simpledialog.askinteger("Questions", get_text(self.lang, "questions"))
                if not no_q or no_q <= 0:
                    continue
                break
            except:
                messagebox.showerror("Error", get_text(self.lang, "invalid"))
        # filter out already answered
        available_questions = [q for q in self.all_questions if q['id'] not in self.questions_history]
        random.shuffle(available_questions)
        self.questions_to_ask = available_questions[:no_q]
        self.total_in_quiz = len(self.questions_to_ask)
        self.show_question()

    def show_question(self):
        if self.current_index >= len(self.questions_to_ask):
            self.finish_quiz()
            return

        q = self.questions_to_ask[self.current_index]
        # handle 'choises' vs 'choices'
        opts = q["choises"] if self.lang in ["рус", "кирилл"] else q["choices"]
        text = f"Q {q['id']}: {q['question']}\n"
        for idx, opt in enumerate(opts, 1):
            text += f"{idx}. {opt['text']}\n"
        text += f"0. {get_text(self.lang, 'skip')}"
        ans = simpledialog.askinteger("Answer", text)

        if ans == 0:
            self.skip += 1  # skip: points unchanged
        else:
            if opts[ans - 1]["answer"]:
                self.right += 1
                self.right_answers += 1
                self.points += 1  # correct: +1
            else:
                self.wrong += 1
                self.points -= 0.25  # incorrect: -0.25
                self.incorrect.append(q["question"])

        self.questions_history.append(q["id"])
        self.current_index += 1
        self.show_question()

    def finish_quiz(self):
        total_questions = self.number_of_questions + self.total_in_quiz
        total_right = self.right_answers
        percent = round((100 * total_right) / total_questions, 2)
        status = "Pass" if percent >= 60 else "Fail"
        add_user(
            self.user_id, self.lang, self.surname, self.name, self.username,
            total_questions, self.points, total_right,
            self.questions_history, status, percent
        )
        result_text = (
            f"{get_text(self.lang,'finish',status)}\n"
            f"✔ {self.right} (correct in this quiz)\n"
            f"✖ {self.wrong} (incorrect in this quiz)\n"
            f"➜ {self.skip} (skipped)\n"
            f"📊 {round((100*self.right/self.total_in_quiz),2)}% (this quiz)\n"
            f"📌 {status} (overall)"
        )
        messagebox.showinfo("Result", result_text)
        if self.incorrect:
            messagebox.showinfo(get_text(self.lang,"incorrect_intro"), "\n".join(self.incorrect))
        self.root.destroy()

# -------- RUN --------
if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)