# Import libraries
import time
import telebot
from telebot import types
import mysql.connector

# The variable for the token to connect to the bot
TOKEN = "TOKEN"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# A function that allows you to access the database
def open_db():
    global db
    global cursor
    db = mysql.connector.connect(
        host="HOST",
        user="USER",
        password="PASSWORD",
        database="DATABASE"
    )
    cursor = db.cursor()

# A function that closes access to the database
def close_db():
    cursor.close()
    db.close()

# A function to receive data from the user, make a record in the database
# and show the main menu
@bot.message_handler(commands=["start"])
def start(message):
    user_data = (message.from_user.id, message.from_user.username)
    open_db()
    try:
        cursor.execute("""INSERT INTO user (id, username) VALUES (%s, %s);""",
                       user_data)
        db.commit()
    except:
        db.rollback()
    db.close()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("🧩 Вибрати гру")
    button2 = types.KeyboardButton("💵 Підтримати")
    markup.add(button1, button2)
    bot.send_message(message.chat.id, f"<b>Вітаю @{message.from_user.username}!</b>\n", reply_markup=markup)


# The main function that allows you to receive messages sent by the user
@bot.message_handler(content_types=["text"])
def bot_message(message):

	# A function that receives the value of a specific user
    def get_value(i):
        open_db()
        cursor.execute(f"""SELECT {i} FROM user WHERE id = %s""",
                       [message.from_user.id])
        value = cursor.fetchone()[0]
        close_db()
        return value

	# A function that updates the value of a specific user
    def update_value(i, value):
        open_db()
        cursor.execute(f"""UPDATE user SET {i} = %s WHERE id = %s""",
                       [value, message.from_user.id])
        db.commit()
        close_db()

	# Game_Казино: A function that allows you to choose a bet
    def rate_menu(money):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        button1 = types.KeyboardButton(f"🟢 Крутити (Ставка: {money} fr)")
        button2 = types.KeyboardButton("🧿 Поставити іншу ставку")
        button_back = types.KeyboardButton("🐸 Повернутися до меню")
        markup.add(button1, button2, button_back)
        bot.send_message(message.chat.id, f"<i>Ставка: {money} fr 💵</i>", reply_markup=markup)
        return message.text

	# Game_Казино: The function that calculates the winnings
    def rate_calc(money, win1, win2, win3, win4):
        if get_value('balance') < money:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            button1 = types.KeyboardButton("🎰 Казино")
            button2 = types.KeyboardButton("🎯 Дартс")
            button3 = types.KeyboardButton("🎳 Боулінг")
            button4 = types.KeyboardButton("💰 Баланс")
            button_back = types.KeyboardButton("🛏️ На головну")
            markup.add(button1, button2, button3, button4, button_back)
            bot.send_message(message.chat.id, money_false_message, reply_markup=markup)
        else:
            sent = bot.send_dice(message.chat.id, "🎰")
            value = sent.dice.value

            if value == 1:
                new_balance = get_value('balance') + win1
                update_value('balance', new_balance)
                time.sleep(2.1)
                bot.send_message(message.chat.id, f"<i>+{win1} fr 🍾 <b>Твій баланс: {get_value('balance')} fr</b></i>")
            elif value == 22:
                new_balance = get_value('balance') + win2
                update_value('balance', new_balance)
                time.sleep(2.1)
                bot.send_message(message.chat.id, f"<i>+{win2} fr 🍾 <b>Твій баланс: {get_value('balance')} fr</b></i>")
            elif value == 43:
                new_balance = get_value('balance') + win3
                update_value('balance', new_balance)
                time.sleep(2.1)
                bot.send_message(message.chat.id, f"<i>+{win3} fr 🍾 <b>Твій баланс: {get_value('balance')} fr</b></i>")
            elif value == 64:
                new_balance = get_value('balance') + win4
                update_value('balance', new_balance)
                time.sleep(2.1)
                bot.send_message(message.chat.id, f"<i>+{win4} fr 🍾 <b>Твій баланс: {get_value('balance')} fr</b></i>")
            else:
                new_balance = get_value('balance') - money
                update_value('balance', new_balance)
                time.sleep(2.1)
                bot.send_message(message.chat.id, f"<i>-{money} fr! <b>Твій баланс: {get_value('balance')} fr</b></i>")

	# Game_Дартс: The function checks (not perfectly) whether the user is playing fair
	# and allows darts to be thrown
    def throw_dart(t, m):
        if get_value('points') > 15:
            games_menu("<b>Жабеня не задоволене, що ти граєш нечесно :(</b>")
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            button1 = types.KeyboardButton(t)
            button_back = types.KeyboardButton("🐸 Повернутися до меню")
            markup.add(button1, button_back)
            bot.send_message(message.chat.id, m, reply_markup=markup)
            sent = bot.send_dice(message.chat.id, "🎯")
            value = sent.dice.value

            if value == 1:
                point = get_value('points') + 0
            elif value == 2:
                point = get_value('points') + 1
            elif value == 3:
                point = get_value('points') + 2
            elif value == 4:
                point = get_value('points') + 3
            elif value == 5:
                point = get_value('points') + 4
            elif value == 6:
                point = get_value('points') + 5

            update_value('points', point)

	# The function that shows games menu
    def games_menu(m):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        button1 = types.KeyboardButton("🎰 Казино")
        button2 = types.KeyboardButton("🎯 Дартс")
        button3 = types.KeyboardButton("🎳 Боулінг")
        button4 = types.KeyboardButton("💰 Баланс")
        button_back = types.KeyboardButton("🛏️ На головну")
        markup.add(button1, button2, button3, button4, button_back)
        bot.send_message(message.chat.id, m, reply_markup=markup)

	# Game_Боулінг: The function allows you to throw the ball
    def throw_ball(t, m):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        button1 = types.KeyboardButton(t)
        button_back = types.KeyboardButton("🐸 Повернутися до меню")
        markup.add(button1, button_back)
        bot.send_message(message.chat.id, m, reply_markup=markup)
        sent = bot.send_dice(message.chat.id, "🎳")
        value = sent.dice.value
        if value == 6:
            update_value('points', value)

	# A variable with a message in case the user does not have enough funds to play the game
    money_false_message = "<b><i>Не достатньо коштів на балансі (</i>\n" \
                          "Зароби грошенят граючи у 🎯 Дартс або 🎳 Боулінг!</b>"

    # Buttons that help the user navigate the bot
    if message.text == "🛏️ На головну":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("🧩 Вибрати гру")
        button2 = types.KeyboardButton("💵 Підтримати")
        markup.add(button1, button2)
        bot.send_message(message.chat.id, "<b>Ти на головній сторінці!</b>", reply_markup=markup)

    elif message.text == "🧩 Вибрати гру" or message.text == "🐸 Повернутися до меню":
        games_menu("<b>Жабеня пропонує тобі вибрати гру! 🐸</b>")

    elif message.text == "💵 Підтримати":
        SUPPORT_LINK = "https://send.monobank.ua/jar/3AxAFP26Gh"
        SUPPORT_PHOTO = open("support_photo.jpg", "rb")
        bot.send_photo(message.chat.id, SUPPORT_PHOTO, caption="<b>Підтримай FROGY!</b>\n"
                                                               "<b>Посилання на банку: </b>"
                                                               f"{SUPPORT_LINK} \n"
                                                               "<b>Дякую тобі ❤</b>")

    elif message.text == "💰 Баланс":
        bot.send_message(message.chat.id, f"<b><i>Твій поточний баланс: {get_value('balance')} fr 💸</i></b>")

    # GAME_Казино
    elif message.text == "🎰 Казино":
        if get_value('balance') < 5:
            bot.send_message(message.chat.id, money_false_message)
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            button1 = types.KeyboardButton("💵 Вибрати ставку")
            button_back = types.KeyboardButton("🐸 Повернутися до меню")
            markup.add(button1, button_back)
            bot.send_message(message.chat.id,
                             "<b><i>Правила гри 🎰 Казино:</i></b>\n\n"
                             "▫ ставка 5 fr:\n"
                             "       <b>BAR</b> - 50 fr\n"
                             "       🫐 - 100 fr\n"
                             "       🍋 - 200 fr\n"
                             "       7️⃣7️⃣7️⃣ - 300 fr\n\n"
                             "▫ ставка 10 fr:\n"
                             "       <b>BAR</b> - 100 fr\n"
                             "       🫐 - 200 fr\n"
                             "       🍋 - 400 fr\n"
                             "       7️⃣7️⃣7️⃣ - 600 fr\n\n"
                             "▫ ставка 50 fr:\n"
                             "       <b>BAR</b> - 150 fr\n"
                             "       🫐 - 300 fr\n"
                             "       🍋 - 600 fr\n"
                             "       7️⃣7️⃣7️⃣ - 900 fr\n\n"
                             "▫ ставка 100 fr:\n"
                             "       <b>BAR</b> - 200 fr\n"
                             "       🫐 - 400 fr\n"
                             "       🍋 - 800 fr\n"
                             "       7️⃣7️⃣7️⃣ - 1200 fr\n\n"
                             f"<b><i>Твій поточний баланс: {get_value('balance')} fr 💸</i></b>", reply_markup=markup)

    elif message.text == "💵 Вибрати ставку" or message.text == "🧿 Поставити іншу ставку":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
        button1 = types.KeyboardButton("5 fr 💵")
        button2 = types.KeyboardButton("10 fr 💵")
        button3 = types.KeyboardButton("50 fr 💵")
        button4 = types.KeyboardButton("100 fr 💵")
        button_back = types.KeyboardButton("🐸 Повернутися до меню")
        markup.add(button1, button2, button3, button4, button_back)
        bot.send_message(message.chat.id, "<b>Скільки поставиш? 😏</b>", reply_markup=markup)

    elif message.text == "5 fr 💵":
        rate_menu(5)
    elif message.text == "🟢 Крутити (Ставка: 5 fr)":
        rate_calc(5, 50, 100, 200, 300)
    elif message.text == "10 fr 💵":
        rate_menu(10)
    elif message.text == "🟢 Крутити (Ставка: 10 fr)":
        rate_calc(10, 100, 200, 400, 600)
    elif message.text == "50 fr 💵":
        rate_menu(50)
    elif message.text == "🟢 Крутити (Ставка: 50 fr)":
        rate_calc(50, 150, 300, 600, 900)
    elif message.text == "100 fr 💵":
        rate_menu(100)
    elif message.text == "🟢 Крутити (Ставка: 100 fr)":
        rate_calc(100, 200, 400, 800, 1200)

    # Game_Дартс
    elif message.text == "🎯 Дартс":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        button1 = types.KeyboardButton("▶ Почати гру")
        button_back = types.KeyboardButton("🐸 Повернутися до меню")
        markup.add(button1, button_back)
        bot.send_message(message.chat.id,
                         "<b><i>Правила гри 🎯 Дартс:</i></b>\n\n"
                         "▫ 3 спроби\n"
                         "▫ влучення в яблучко - 5 балів\n"
                         "       друге коло - 4 бали\n"
                         "       третє коло - 3 бали\n"
                         "       четверте коло - 2 бали\n"
                         "       п\'яте коло - 1 бал\n"
                         "       повз мішень - 0 балів\n"
                         "▫ якщо кількість балів дорівнює або\n"
                         "       перебільшує 8 - ти виграв\n"
                         "       якщо ні - ти програв\n"
                         "▫ кожен виграш + 10 fr на баланс\n\n"
                         "<b><i>Щасти тобі! 😄</i></b>", reply_markup=markup)

    elif message.text == "▶ Почати гру" or message.text == "↩ Спробувати ще раз":
        update_value('points', 0)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        button1 = types.KeyboardButton("🟢 Кинути")
        button_back = types.KeyboardButton("🐸 Повернутися до меню")
        markup.add(button1, button_back)
        bot.send_message(message.chat.id, "<b>Кидай!</b>", reply_markup=markup)

    elif message.text == "🟢 Кинути":
        throw_dart("🟡 Кинути", "<i>Перша спроба</i>")
    elif message.text == "🟡 Кинути":
        throw_dart("🔴 Кинути", "<i>Друга спроба\nБудь обережним! У тебе залишилася остання спроба</i>")
    elif message.text == "🔴 Кинути":
        throw_dart("↩ Спробувати ще раз", "<i>Третя спроба</i>")
        time.sleep(3)
        if get_value('points') >= 8:
            update_value('balance', get_value('balance') + 10)
            result_message = "<b>Вітаю! Ти виграв 🎉</b>\n" \
                             "<i>Ваш баланс поповнено на 10 fr</i>"
        else:
            result_message = "<b>На жаль, ти програв 😕</b>"
        bot.send_message(message.chat.id, f"{result_message}\n<i>Твій результат: {get_value('points')}</i>")

    # Game_Боулінг
    elif message.text == "🎳 Боулінг":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        button1 = types.KeyboardButton("▶ Я готовий")
        button_back = types.KeyboardButton("🐸 Повернутися до меню")
        markup.add(button1, button_back)
        bot.send_message(message.chat.id, "<b><i>Правила гри 🎳 Боулінг:</i></b>\n"
                                          "\n"
                                          "▫ 5 спроб\n"
                                          "▫ хоч один страйк - твоя перемога\n"
                                          "       ні разу не збив всі кеглі - ти програв\n"
                                          "▫ кожен виграш + 20 fr на баланс\n"
                                          "     \n"
                                          "<b><i>Покажи як потрібно! 💪🏻</i></b>", reply_markup=markup)

    elif message.text == "▶ Я готовий" or message.text == "↪ Спробувати ще раз":
        update_value('points', 0)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        button1 = types.KeyboardButton("🟢 Кинути кулю")
        button_back = types.KeyboardButton("🐸 Повернутися до меню")
        markup.add(button1, button_back)
        bot.send_message(message.chat.id, "<b>Кидай!</b>", reply_markup=markup)

    elif message.text == "🟢 Кинути кулю":
        throw_ball("🟠 Кинути кулю", "<i>Перша спроба</i>")
    elif message.text == "🟠 Кинути кулю":
        throw_ball("🟡 Кинути кулю", "<i>Друга спроба</i>")
    elif message.text == "🟡 Кинути кулю":
        throw_ball("⚪️Кинути кулю", "<i>Третя спроба</i>")
    elif message.text == "⚪️Кинути кулю":
        throw_ball("🔴 Кинути кулю", "<i>Четверта спроба</i>")
    elif message.text == "🔴 Кинути кулю":
        throw_ball("↪ Спробувати ще раз", "<i>П'ята спроба</i>")
        time.sleep(4)
        if get_value('points') >= 6:
            update_value('balance', get_value('balance') + 20)
            results_message = "<b>Юхуу твоя пермога 🤩</b>\n" \
                              "<i>Баланс поповнено на 20 fr</i>\n" \
                              "<i>Влучно поцілив!</i>"

        else:
            results_message = "<b>Ти програв 🫤</b>\n" \
                              "<i>Спробуй ще раз!</i>"

        bot.send_message(message.chat.id, results_message)

    else:
        # In case the buttons don't exist
        bot.send_message(message.chat.id, "<i>Упсс, такої команди не інсує (</i>")

bot.polling(none_stop=False, interval=0) # A line of code to keep the bot running all the time
