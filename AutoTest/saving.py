import mysql.connector as mc
mydb = mc.connect(
    host="localhost",
    user="root",
    password="Yournewpassword123!",
    port=3307,
    database="users"
)
mycursor=mydb.cursor()

def add_user(user_id, language, surname, name, username, number_of_questions, points, right_answers, history, status, percent):
    mycursor.execute(f'insert into users values ("{user_id}", "{language}", "{surname}", "{name}", "{username}", "{number_of_questions}", "{points}", "{right_answers}", "{status}", "{percent}");')
    for i in history:
        mycursor.execute(f'insert into questions_history values ("{user_id}", "{i}")')
    mydb.commit()

def modify_user(user_id, language, surname, name, username, number_of_questions, points, right_answers, history, status, percent):
    mycursor.execute(f"DELETE FROM questions_history WHERE user_id = {user_id};")
    mycursor.execute(f"DELETE FROM users WHERE user_id = {user_id};")
    mycursor.execute(f'insert into users values ("{user_id}", "{language}", "{surname}", "{name}", "{username}", "{number_of_questions}", "{points}", "{right_answers}", "{status}", "{percent}");')
    for i in history:
        mycursor.execute(f'insert into questions_history values ("{user_id}", "{i}")')
    mydb.commit()
def show_all():
    mycursor.execute(f"SELECT * FROM users ORDER BY points DESC;")
    myresult = mycursor.fetchall()
    column_names = mycursor.column_names
    print(column_names)
    for i in myresult:
        print(i)
show_all()
