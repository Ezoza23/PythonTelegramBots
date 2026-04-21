import asyncio
import time
import random
import mysql.connector as mc

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = "8639212152:AAGhwFkaFFg6OAVdyW1hdkQbvAE5R85hJjg"

# ---------------- DATABASE ----------------
db = mc.connect(
    host="localhost",
    user="root",
    password="Yournewpassword123!",
    database="game_bot",
    port=3307
)

# ---------------- GLOBAL ----------------
games = {}
waiting = None
CHOICES = ["Rock", "Paper", "Scissors"]

# ---------------- DB FUNCTIONS ----------------
def get_or_create_player(user_id, name):
    cur = db.cursor()
    cur.execute("SELECT player_id FROM players WHERE player_id=%s", (user_id,))
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO players (player_id, name, score, nog) VALUES (%s, %s, 0, 0)",
            (user_id, name),
        )
        db.commit()
    cur.close()


def update_player(user_id, win):
    cur = db.cursor()
    cur.execute("UPDATE players SET nog = nog + 1 WHERE player_id=%s", (user_id,))
    if win:
        cur.execute("UPDATE players SET score = score + 5 WHERE player_id=%s", (user_id,))
    db.commit()
    cur.close()


def insert_game(player1_id, player2_id, winner, duration):
    cur = db.cursor()
    cur.execute(
        """
        INSERT INTO games (player1_id, player2_id, winner, duration)
        VALUES (%s, %s, %s, %s)
        """,
        (player1_id, player2_id, winner, duration),
    )
    db.commit()
    cur.close()


def get_leaderboard(limit=10):
    cur = db.cursor()
    cur.execute("""
        SELECT name, score, nog
        FROM players
        ORDER BY score DESC
        LIMIT %s
    """, (limit,))
    data = cur.fetchall()
    cur.close()
    return data


# ================= GAME ENGINE =================
class GameSession:
    def __init__(self, p1, p2=None, mode="AI", rounds=3):
        self.p1 = p1
        self.p2 = p2
        self.mode = mode
        self.rounds = rounds

        self.round = 0
        self.start_time = time.time()

        self.scores = {p1.id: 0}
        if p2:
            self.scores[p2.id] = 0

        self.ties = 0
        self.choices = {}

        self.timer_task = None
        self.round_active = False
        self.players_played = set()
        self.round_lock = asyncio.Lock()

    def resolve(self, a, b):
        if a == b:
            return 0
        if (
            (a == "Rock" and b == "Scissors")
            or (a == "Paper" and b == "Rock")
            or (a == "Scissors" and b == "Paper")
        ):
            return 1
        return -1

    async def start_round(self, bot):
        self.choices = {}
        self.players_played = set()
        self.round_active = True

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Rock", callback_data="Rock"),
                InlineKeyboardButton("Paper", callback_data="Paper"),
                InlineKeyboardButton("Scissors", callback_data="Scissors"),
            ]
        ])

        await bot.send_message(self.p1.id, "Choose (5 seconds)...", reply_markup=keyboard)

        if self.p2:
            await bot.send_message(self.p2.id, "Choose (5 seconds)...", reply_markup=keyboard)

        if self.timer_task:
            self.timer_task.cancel()

        self.timer_task = asyncio.create_task(self.timeout(bot))
        self.timer_task.add_done_callback(self.handle_task_error)

    def handle_task_error(self, task):
        try:
            task.result()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print("TASK ERROR:", e)

    async def play(self, player, choice, bot):
        async with self.round_lock:

            if not self.round_active:
                return

            if player.id in self.players_played:
                return

            self.players_played.add(player.id)
            self.choices[player.id] = choice

            # AI MODE
            if self.mode == "AI":
                ai = random.choice(CHOICES)
                result = self.resolve(choice, ai)

                if result == 1:
                    self.scores[player.id] += 1
                elif result == 0:
                    self.ties += 1

                self.round += 1
                self.round_active = False

                if self.timer_task:
                    self.timer_task.cancel()

                await bot.send_message(
                    player.id,
                    f"{player.first_name} chose: {choice}\nAI chose: {ai}"
                )

                await self.next(bot)
                return

            # PVP
            if len(self.players_played) < 2:
                return

            self.round_active = False

            if self.timer_task:
                self.timer_task.cancel()

            c1 = self.choices[self.p1.id]
            c2 = self.choices[self.p2.id]

            await bot.send_message(
                self.p1.id,
                f"{self.p1.first_name}: {c1}\n{self.p2.first_name}: {c2}"
            )
            await bot.send_message(
                self.p2.id,
                f"{self.p1.first_name}: {c1}\n{self.p2.first_name}: {c2}"
            )

            r = self.resolve(c1, c2)

            if r == 1:
                self.scores[self.p1.id] += 1
            elif r == -1:
                self.scores[self.p2.id] += 1
            else:
                self.ties += 1

            self.round += 1

            await self.next(bot)

    async def timeout(self, bot):
        try:
            await asyncio.sleep(5)

            async with self.round_lock:
                if not self.round_active:
                    return

                self.round_active = False

                p1_id = self.p1.id
                p2_id = self.p2.id if self.p2 else None

                c1 = self.choices.get(p1_id)
                c2 = self.choices.get(p2_id) if p2_id else None

                if self.mode == "AI":
                    self.round += 1
                    await bot.send_message(self.p1.id, "⏱ Timeout! You lost this round.")
                    await self.next(bot)
                    return

                if c1 is None and c2 is None:
                    self.ties += 1
                    msg = "⏱ Both players timed out!"
                elif c1 is None:
                    self.scores[p2_id] += 1
                    msg = f"{self.p1.first_name} timed out → {self.p2.first_name} wins"
                elif c2 is None:
                    self.scores[p1_id] += 1
                    msg = f"{self.p2.first_name} timed out → {self.p1.first_name} wins"
                else:
                    return

                self.round += 1

                await bot.send_message(self.p1.id, msg)
                await bot.send_message(self.p2.id, msg)

                await self.next(bot)

        except asyncio.CancelledError:
            return

    async def next(self, bot):
        if self.round < self.rounds:
            await self.start_round(bot)
        else:
            await self.finish(bot)

    async def finish(self, bot):
        duration = int(time.time() - self.start_time)

        p1_score = self.scores[self.p1.id]
        p2_score = self.scores.get(self.p2.id, 0) if self.p2 else 0

        # winner logic (UNCHANGED GAME LOGIC)
        if self.p2:
            if p1_score > p2_score:
                winner_id = self.p1.id
                winner_name = self.p1.first_name
                update_player(self.p1.id, True)
                update_player(self.p2.id, False)

            elif p2_score > p1_score:
                winner_id = self.p2.id
                winner_name = self.p2.first_name
                update_player(self.p2.id, True)
                update_player(self.p1.id, False)

            else:
                winner_id = 0
                winner_name = "Tie"
                update_player(self.p1.id, False)
                update_player(self.p2.id, False)

            insert_game(self.p1.id, self.p2.id, winner_id, duration)

        else:
            if p1_score > 0:
                winner_id = self.p1.id
                winner_name = self.p1.first_name
            else:
                winner_id = 0
                winner_name = "AI"

            update_player(self.p1.id, p1_score > 0)
            insert_game(self.p1.id, None, winner_id, duration)

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")]
        ])

        msg = f"Winner: {winner_name}\nDuration: {duration}s"

        await bot.send_message(self.p1.id, msg, reply_markup=keyboard)
        if self.p2:
            await bot.send_message(self.p2.id, msg, reply_markup=keyboard)


# ================= BOT =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_player(user.id, user.first_name)

    keyboard = [
        [InlineKeyboardButton("AI", callback_data="ai")],
        [InlineKeyboardButton("PvP", callback_data="pvp")]
    ]

    await update.message.reply_text("Choose mode", reply_markup=InlineKeyboardMarkup(keyboard))


async def mode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    context.user_data["mode"] = q.data
    await q.message.reply_text("Enter number of rounds:")


async def rounds_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global waiting

    if not update.message.text.isdigit():
        return

    rounds = int(update.message.text)
    user = update.effective_user
    mode = context.user_data.get("mode")

    if mode == "ai":
        game = GameSession(user, mode="AI", rounds=rounds)
        games[user.id] = game
        await game.start_round(context.bot)

    else:
        if waiting is None:
            waiting = (user, rounds)
            await update.message.reply_text("Waiting for opponent...")
        else:
            opponent, r = waiting
            waiting = None

            game = GameSession(user, opponent, mode="PVP", rounds=r)

            games[user.id] = game
            games[opponent.id] = game

            await game.start_round(context.bot)


async def choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user = q.from_user
    game = games.get(user.id)

    if not game:
        return

    await game.play(user, q.data, context.bot)


async def leaderboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    data = await asyncio.to_thread(get_leaderboard)

    if not data:
        await q.message.reply_text("No players yet.")
        return

    text = "🏆 Leaderboard:\n\n"
    for i, (name, score, nog) in enumerate(data, 1):
        text += f"{i}. {name} — {score} pts ({nog} games)\n"

    await q.message.reply_text(text)


# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(mode_handler, pattern="^(ai|pvp)$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, rounds_handler))
    app.add_handler(CallbackQueryHandler(choice_handler, pattern="^(Rock|Paper|Scissors)$"))
    app.add_handler(CallbackQueryHandler(leaderboard_handler, pattern="^leaderboard$"))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()

