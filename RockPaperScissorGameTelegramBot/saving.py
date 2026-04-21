import mysql.connector as mc
mydb = mc.connect(
    host="localhost",
    user="root",
    password="Yournewpassword123!",
    port=3307,
    database="game_bot"
)
mycursor=mydb.cursor()
# 8639212152:AAGhwFkaFFg6OAVdyW1hdkQbvAE5R85hJjg
def add_user(telegram_id, name):
    query = """
    INSERT INTO players (telegram_id, name)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE name=%s
    """
    mycursor.execute(query, (telegram_id, name, name))
    mydb.commit()
def save_game(player1, player2, winner, score, duration, ties):
    query = """
    INSERT INTO games (player1, player2, winner, score, duration, ties)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    mycursor.execute(query, (player1, player2, winner, score, duration, ties))
    mydb.commit()
t='8639212152:AAGhwFkaFFg6OAVdyW1hdkQbvAE5R85hJjg'