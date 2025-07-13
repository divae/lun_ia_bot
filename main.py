import os
import json
import math
import random
import locale
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, BotCommand
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, ConversationHandler
)
from telegram.ext import Filters
from astral import LocationInfo
from astral.moon import moonrise, phase

# Cargar token
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

# Constantes y datos
MOON_CYCLE_DAYS = 30
NEW_MOON_THRESHOLD = 7
FIRST_QUARTER_THRESHOLD = 15
FULL_MOON_THRESHOLD = 22
MOON_PHASE_NAMES = ["Luna Nueva", "Cuarto Creciente", "Luna Llena", "Cuarto Menguante"]

try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    pass

with open("moon_data.json", encoding="utf-8") as f:
    MOON_DATA = json.load(f)
with open("moon_science_data.json", encoding="utf-8") as f:
    MOON_SCIENCE_DATA = json.load(f)

NOTE = 1
ADMIN_USERNAMES = ["divae", "EstelaYoMisma"]
CHANNEL_CHAT_ID = '@lun_ia_oficial'

def get_moon_phase():
    now = datetime.now()
    r = (now.year % 100) % 19
    if r > 9:
        r -= 19
    phase_calc = ((r * 11) % MOON_CYCLE_DAYS) + now.month + now.day
    if now.month < 3:
        phase_calc += 2
    phase_calc -= 8.3
    phase_calc = int(phase_calc + 0.5) % MOON_CYCLE_DAYS
    if phase_calc < NEW_MOON_THRESHOLD:
        return 0
    if phase_calc < FIRST_QUARTER_THRESHOLD:
        return 1
    if phase_calc < FULL_MOON_THRESHOLD:
        return 2
    return 3

def get_moon_illumination():
    moon_phase_value = phase(datetime.now())
    return round(abs(math.sin(moon_phase_value * math.pi)) * 100, 1)

def get_moon_distance():
    day_of_year = datetime.now().timetuple().tm_yday
    variation = 25000 * math.sin(2 * math.pi * day_of_year / 365.25)
    return round(384400 + variation, -3)

def get_zodiac_sign():
    now = datetime.now()
    month, day = now.month, now.day
    zodiac_signs = [
        ("Capricornio", 1, 19), ("Acuario", 1, 20), ("Piscis", 2, 19),
        ("Aries", 3, 20), ("Tauro", 4, 20), ("Géminis", 5, 21),
        ("Cáncer", 6, 21), ("Leo", 7, 22), ("Virgo", 8, 22),
        ("Libra", 9, 22), ("Escorpio", 10, 22), ("Sagitario", 11, 21),
        ("Capricornio", 12, 22)
    ]
    for i, (sign, m, d) in enumerate(zodiac_signs):
        next_d = zodiac_signs[(i + 1) % len(zodiac_signs)][2]
        if (month == m and day >= d) or (month == (m % 12) + 1 and day < next_d):
            return sign
    return "Capricornio"

def start(update, context):
    update.message.reply_text("¡Bienvenid@! Usa /luna para ver el mensaje lunar de hoy, /intro para más info, o únete al canal: @lun_ia_oficial")

def intro(update, context):
    msg = (
        "🌙 ¡Bienvenid@ a LUN.IA!\n\n"
        "Aquí puedes recibir inspiración lunar diaria, rituales, mantras, meditaciones y tips.\n"
        "Comandos:\n"
        "/luna – Mensaje lunar\n"
        "/anotar – Registrar avance\n"
        "/logros – Ver notas\n"
        "/meditacion [tema]\n"
        "/mantra [tema]\n"
        "/conjuro [tema]\n"
        "/contacto – Info y contacto"
    )
    update.message.reply_text(msg)

def moon(update, context):
    idx = get_moon_phase()
    phase_name = MOON_PHASE_NAMES[idx]
    science_data = MOON_SCIENCE_DATA[phase_name]
    illumination = get_moon_illumination()
    distance = get_moon_distance()
    zodiac = get_zodiac_sign()
    date_str = datetime.now().strftime('%-d %B %Y')

    phase_emoji = {"Luna Nueva": "🌑", "Cuarto Creciente": "🌔", "Luna Llena": "🌕", "Cuarto Menguante": "🌗"}

    message = (
        f"{phase_emoji[phase_name]} {phase_name} en {zodiac} – {date_str} {phase_emoji[phase_name]}\n\n"
        f"✨ Iluminación: {illumination}%\n"
        f"🌍 Distancia Tierra-Luna: ~{distance:,} km\n\n"
        f"👉 Dato curioso:\n"
        f"{science_data['curiosidad']}\n\n"
        f"✨ Ritual breve para hoy:\n"
        f"{science_data['ritual_breve']}\n\n"
        f"Es momento de:\n"
        f"{science_data['momentos_propicios']}\n\n"
        f"¿Quieres inspiración personalizada, mantras, meditaciones o anotar tus logros?\n"
        f"Habla conmigo en privado: @lun_ia_my_bot"
    )
    update.message.reply_text(message)

def ask_note(update, context):
    update.message.reply_text("¿Qué quieres anotar hoy? Escribe tu avance. Usa /cancelar para cancelar.")
    return NOTE

def save_note(update, context):
    user_id = str(update.effective_user.id)
    note_text = update.message.text
    phase_idx = get_moon_phase()
    phase_name = MOON_PHASE_NAMES[phase_idx]
    now = datetime.now().strftime('%Y-%m-%d')
    note_entry = {"date": now, "phase": phase_name, "note": note_text}

    try:
        with open("user_notes.json", "r", encoding="utf-8") as f:
            notes = json.load(f)
    except:
        notes = {}
    notes.setdefault(user_id, []).append(note_entry)
    with open("user_notes.json", "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)
    update.message.reply_text("✅ Nota guardada. Usa /logros para ver tu historial.")
    return ConversationHandler.END

def cancel_note(update, context):
    update.message.reply_text("❌ Anotación cancelada.")
    return ConversationHandler.END

def show_logros(update, context):
    user_id = str(update.effective_user.id)
    try:
        with open("user_notes.json", "r", encoding="utf-8") as f:
            notes = json.load(f)
    except:
        notes = {}
    user_notes = notes.get(user_id, [])
    if not user_notes:
        update.message.reply_text("Aún no tienes logros. Usa /anotar para registrar tu avance.")
        return
    msg = "📒 *Tus notas recientes:*\n\n"
    for n in user_notes[-10:][::-1]:
        msg += f"{n['date']} ({n['phase']}): {n['note']}\n\n"
    update.message.reply_text(msg, parse_mode='Markdown')

def contacto(update, context):
    update.message.reply_text("Puedes contactarme en Telegram: @divae\nGracias por usar LUN.IA 🌙")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    note_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('anotar', ask_note)],
        states={NOTE: [MessageHandler(Filters.text & ~Filters.command, save_note)]},
        fallbacks=[CommandHandler('cancelar', cancel_note)]
    )

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('intro', intro))
    dp.add_handler(CommandHandler('luna', moon))
    dp.add_handler(note_conv_handler)
    dp.add_handler(CommandHandler('logros', show_logros))
    dp.add_handler(CommandHandler('contacto', contacto))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
