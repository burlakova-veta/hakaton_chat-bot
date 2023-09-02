from telebot import types,TeleBot
import requests
import speech_recognition as sr
import soundfile as sf 
import sqlite3

api_token="5730882401:AAGFyiOZUyl-DeqzFUOduChk9LAvE2yPPFA"
bot =TeleBot(api_token)

vopros=["Записаться на приём","Записаться на диспансеризацию","Результаты теста на COVID","Оставить жалобу"]
med_ucherejdenie=["Городская клиническая больница №1","Городская клиническая больница №2","Городская клиническая больница №3",
                    "Городская поликлиника больница №4","Городской родильный дом",
                    "Детский клинический медицинский центр г. Читы",
                    "Клинический медицинский центр г.Читы",
                    "Станция скорой медицинской помощи",
                    "Лаборатория «Гемотест»",
                    "Клиника «Академия Здоровья»",
                    "Стоматологическая клиника «Дента Люкс»",
                    "Клиника Медикс",
                    "Клиника «Новомед»",
                    "Медицинский центр «Медлюкс»"]
top_med_ucherejdenie=["Клиника «Академия Здоровья»","Клинический медицинский центр г.Читы","Краевой онкологический диспансер"]
simv=["(",")","'","",","]
flag=''
@bot.message_handler(commands=["help", "start"])
def send_welcome(message):
    markup=types.InlineKeyboardMarkup()
    for i in vopros:
        TN = types.InlineKeyboardButton(text=i,callback_data=i)
        markup.add(TN)
    bot.send_message(message.chat.id, """
    Здраствуйте!\nВас приветсвует ЗдравБот. Вы можете выбрать подходящий вам запрос из предложенных или задать свой вопрос
    """,reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in["Оставить жалобу"])
def jaloba_start(call):
    jaloba=""
    bot.send_message(call.message.chat.id, """Введите ФИО""")
    bot.register_next_step_handler(call.message, FIO,jaloba)
def FIO(message,jaloba):
    jaloba+=message.text+"\n"
    bot.send_message(message.chat.id,"Укажите контактный телефон и e-mail через пробел")
    bot.register_next_step_handler(message,personal,jaloba)
def personal(message,jaloba):
    jaloba+=message.text+"\n"
    bot.send_message(message.chat.id,"Введите тему")
    bot.register_next_step_handler(message,tema,jaloba)
def tema(message,jaloba):
    jaloba+=message.text+"\n"
    bot.send_message(message.chat.id,"Введите название медицинского учреждения")
    bot.register_next_step_handler(message,ucherejdenia,jaloba)
def ucherejdenia(message,jaloba):
    jaloba+=message.text+"\n"
    bot.send_message(message.chat.id,"Опишите свою проблему")
    bot.register_next_step_handler(message,jalobi,jaloba)
def jalobi(message,jaloba):
    jaloba+=message.text
    bot.send_message(message.chat.id,text=f"Ваша жалоба: \n{jaloba}\n")
    markup=types.InlineKeyboardMarkup()
    TN = types.InlineKeyboardButton(text="да",callback_data="jyes")
    MN = types.InlineKeyboardButton(text="нет",callback_data="jno")
    markup.add(TN,MN)
    bot.send_message(message.chat.id, """Всё верно?""",reply_markup=markup)



@bot.callback_query_handler(func=lambda call: call.data in ["jyes","jno"])
def jaloba_otvet(call):
    if call.data=="jyes":
        bot.send_message(call.message.chat.id,"Ваша жалоба принята.")
        
    else:
        bot.send_message(call.message.chat.id,"Начнём сначала")
        jaloba=""
        bot.send_message(call.message.chat.id, """Введите ФИО""")
        bot.register_next_step_handler(call.message, FIO,jaloba)
        

@bot.callback_query_handler(func=lambda call: call.data in ["Другие"])
def drugie(call):
    k=0
    markup=types.InlineKeyboardMarkup()
    for i in med_ucherejdenie:
        k+=1
        MN = types.InlineKeyboardButton(text=i,callback_data=k)
        markup.add(MN)
    k+=1
    bot.send_message(call.message.chat.id, """Другие мед учреждения""",reply_markup=markup)



@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
        k=0
        try:
            if call.message:
                if call.data=="Записаться на приём":
                    markup=types.InlineKeyboardMarkup()
                    for i in top_med_ucherejdenie:
                        k+=1
                        MN = types.InlineKeyboardButton(text=i,callback_data=k)
                        markup.add(MN)
                    k+=1
                    MN = types.InlineKeyboardButton(text="Другие",callback_data="Другие")
                    markup.add(MN)
                    bot.send_message(call.message.chat.id, """Выберите медицинское учреждение из списка или введите самостоятельно""",reply_markup=markup)


                elif call.data=="Результаты теста на COVID":
                    markup=types.InlineKeyboardMarkup()
                    TN = types.InlineKeyboardButton(text="Госуслуги",url="https://www.gosuslugi.ru/")
                    markup.add(TN)
                    bot.send_message(call.message.chat.id, """Вы можете узнать результат теста на COVID на сайте госуслуг.\n\nДля этого в личном кабинете перейдите в раздел "Сведения об иммунизации" """,reply_markup=markup)
        except Exception as e:
            print(repr(e))



@bot.message_handler(content_types=["text"])
def echo_message(message):
    connect=sqlite3.connect("вопрос_ответ.db")
    curs=connect.cursor()
    text=message.text
    otvet=curs.execute(f"SELECT Аналог FROM Вопрос WHERE Аналог='{text.lower()}'").fetchall()
    if len(otvet)==1:
        otvet=str(*otvet)
        for i in simv:
            otvet=otvet.replace(i,"")
        otvet=curs.execute(f"SELECT Ответ FROM Вопрос INNER JOIN Ответ ON Вопрос.[Id вопроса]=Ответ.[Id вопроса] WHERE Аналог='{text.lower()}'").fetchall()
        
        bot.send_message(message.chat.id, otvet)
    if len(otvet)==0:
        bot.send_message(message.chat.id,text="Я не могу ответить на ваш вопроc. Идет переключение на оператора. Подождите")
        # send_welcome(message)  

@bot.message_handler(content_types=['voice'])
def repeat_all_message(message):
    file_info = bot.get_file(message.voice.file_id)
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(api_token, file_info.file_path))
    audio=f'./voice/voice.ogg'
    with open(audio,'wb') as f:
        f.write(file.content)

    data, samplerate = sf.read(audio)
    audio2=f'./voice/voice.wav'
    sf.write(audio2, data, samplerate)

    recognizer = sr.Recognizer()
    with sr.AudioFile(audio2) as source:
        recorded_audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(
                recorded_audio, 
                language="ru-RU"
            )
        print(text) # забираем голосовое сообщение !!!!!!!!
        bot.send_message(message.chat.id,text)
        
    except Exception as ex:
        print(ex)
        

bot.polling(none_stop=True)