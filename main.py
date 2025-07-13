import os
import json
import math
import random
import locale
import logging
import sys
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, BotCommand
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, ConversationHandler
)
from telegram.ext import Filters
from astral import LocationInfo
from astral.moon import moonrise, phase

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Cargar token
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

if not TOKEN:
    logger.error("No se encontró el token de Telegram. Asegúrate de tener config.env con TELEGRAM_TOKEN")
    sys.exit(1)

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

try:
    with open("moon_data.json", encoding="utf-8") as f:
        MOON_DATA = json.load(f)
    with open("moon_science_data.json", encoding="utf-8") as f:
        MOON_SCIENCE_DATA = json.load(f)
    with open("rituals_db.json", encoding="utf-8") as f:
        RITUALS_DATA = json.load(f)
except FileNotFoundError as e:
    logger.error(f"Archivo JSON no encontrado: {e}")
    sys.exit(1)
except json.JSONDecodeError as e:
    logger.error(f"Error al decodificar JSON: {e}")
    sys.exit(1)

NOTE = 1
ADMIN_USERNAMES = ["divae", "EstelaYoMisma"]
CHANNEL_CHAT_ID = '@lun_ia_oficial'

def get_moon_phase():
    try:
        # Usar la librería astral para un cálculo más preciso
        moon_phase_value = phase(datetime.now())
        
        # Convertir el valor de fase (0-1) a índice de fase lunar
        # 0 = Luna Nueva, 0.25 = Cuarto Creciente, 0.5 = Luna Llena, 0.75 = Cuarto Menguante
        if moon_phase_value < 0.0625:  # 0-6.25%
            return 0  # Luna Nueva
        elif moon_phase_value < 0.1875:  # 6.25-18.75%
            return 1  # Cuarto Creciente
        elif moon_phase_value < 0.3125:  # 18.75-31.25%
            return 1  # Cuarto Creciente
        elif moon_phase_value < 0.4375:  # 31.25-43.75%
            return 2  # Luna Llena
        elif moon_phase_value < 0.5625:  # 43.75-56.25%
            return 2  # Luna Llena
        elif moon_phase_value < 0.6875:  # 56.25-68.75%
            return 2  # Luna Llena
        elif moon_phase_value < 0.8125:  # 68.75-81.25%
            return 3  # Cuarto Menguante
        elif moon_phase_value < 0.9375:  # 81.25-93.75%
            return 3  # Cuarto Menguante
        else:  # 93.75-100%
            return 0  # Luna Nueva
    except Exception as e:
        logger.error(f"Error calculando fase lunar: {e}")
        # Fallback al algoritmo anterior en caso de error
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
    try:
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
    except Exception as e:
        logger.error(f"Error en función moon: {e}")
        update.message.reply_text("❌ Error al obtener información lunar. Intenta de nuevo.")

def ask_note(update, context):
    update.message.reply_text("¿Qué quieres anotar hoy? Escribe tu avance. Usa /cancelar para cancelar.")
    return NOTE

def save_note(update, context):
    user_id = str(update.effective_user.id)
    note_text = update.message.text
    phase_idx = get_moon_phase()
    phase_name = MOON_PHASE_NAMES[phase_idx]
    now = datetime.now().strftime('%Y-%m-%d')
    
    # Debug: mostrar la fase calculada
    moon_phase_value = phase(datetime.now())
    logger.info(f"Fase lunar calculada: {moon_phase_value:.3f} -> {phase_name} (índice: {phase_idx})")
    
    note_entry = {"date": now, "phase": phase_name, "note": note_text}

    try:
        with open("user_notes.json", "r", encoding="utf-8") as f:
            notes = json.load(f)
    except:
        notes = {}
    notes.setdefault(user_id, []).append(note_entry)
    with open("user_notes.json", "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)
    update.message.reply_text(f"✅ Nota guardada en {phase_name}. Usa /logros para ver tu historial.")
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

def get_mantra(update, context):
    if not context.args:
        update.message.reply_text("Uso: /mantra [tema]\nTemas disponibles: proyectos, amor, creatividad, abundancia, proteccion, limpieza")
        return
    
    theme = context.args[0].lower()
    phase_idx = get_moon_phase()
    phase_name = MOON_PHASE_NAMES[phase_idx]
    
    try:
        mantras = RITUALS_DATA[phase_name]["mantras"]
        if theme in mantras:
            mantra = random.choice(mantras[theme])
            message = f"🧘‍♀️ *Mantra para {theme} en {phase_name}:*\n\n{mantra}\n\n💫 Repítelo 3 veces al día para potenciar su efecto."
            update.message.reply_text(message, parse_mode='Markdown')
        else:
            available_themes = ", ".join(mantras.keys())
            update.message.reply_text(f"Tema '{theme}' no disponible para {phase_name}.\nTemas disponibles: {available_themes}")
    except KeyError:
        update.message.reply_text(f"No hay mantras disponibles para {phase_name}.")

def get_meditacion(update, context):
    if not context.args:
        update.message.reply_text("Uso: /meditacion [tema]\nTemas disponibles: proyectos, amor, creatividad, abundancia, proteccion, limpieza")
        return
    
    theme = context.args[0].lower()
    phase_idx = get_moon_phase()
    phase_name = MOON_PHASE_NAMES[phase_idx]
    
    try:
        meditaciones = RITUALS_DATA[phase_name]["meditaciones"]
        if theme in meditaciones:
            meditacion = random.choice(meditaciones[theme])
            message = f"🧘‍♀️ *Meditación para {theme} en {phase_name}:*\n\n{meditacion}\n\n✨ Dedica 5-10 minutos a esta práctica."
            update.message.reply_text(message, parse_mode='Markdown')
        else:
            available_themes = ", ".join(meditaciones.keys())
            update.message.reply_text(f"Tema '{theme}' no disponible para {phase_name}.\nTemas disponibles: {available_themes}")
    except KeyError:
        update.message.reply_text(f"No hay meditaciones disponibles para {phase_name}.")

def get_conjuro(update, context):
    if not context.args:
        update.message.reply_text("Uso: /conjuro [tema]\nTemas disponibles: proteccion, abundancia, amor, creatividad, limpieza")
        return
    
    theme = context.args[0].lower()
    phase_idx = get_moon_phase()
    phase_name = MOON_PHASE_NAMES[phase_idx]
    
    try:
        conjuros = RITUALS_DATA[phase_name]["conjuros"]
        if theme in conjuros:
            conjuro = random.choice(conjuros[theme])
            message = f"🔮 *Conjuro para {theme} en {phase_name}:*\n\n{conjuro}\n\n🌟 Realiza este ritual con intención y fe."
            update.message.reply_text(message, parse_mode='Markdown')
        else:
            available_themes = ", ".join(conjuros.keys())
            update.message.reply_text(f"Tema '{theme}' no disponible para {phase_name}.\nTemas disponibles: {available_themes}")
    except KeyError:
        update.message.reply_text(f"No hay conjuros disponibles para {phase_name}.")

def contacto(update, context):
    update.message.reply_text("Puedes contactarme en Telegram: @divae\nGracias por usar LUN.IA 🌙")

def error_handler(update, context):
    logger.error(f"Error en el bot: {context.error}")
    if update and update.effective_message:
        update.effective_message.reply_text("❌ Ocurrió un error. Por favor, intenta de nuevo más tarde.")

def main():
    try:
        logger.info("Iniciando bot LUN.IA...")
        updater = Updater(TOKEN, use_context=True)
        dp = updater.dispatcher

        # Agregar manejador de errores
        dp.add_error_handler(error_handler)

        note_conv_handler = ConversationHandler(
            entry_points=[CommandHandler('anotar', ask_note)],
            states={NOTE: [MessageHandler(Filters.text & ~Filters.command, save_note)]},
            fallbacks=[CommandHandler('cancelar', cancel_note)]
        )

        dp.add_handler(CommandHandler('start', start))
        dp.add_handler(CommandHandler('intro', intro))
        dp.add_handler(CommandHandler('luna', moon))
        dp.add_handler(CommandHandler('mantra', get_mantra))
        dp.add_handler(CommandHandler('meditacion', get_meditacion))
        dp.add_handler(CommandHandler('conjuro', get_conjuro))
        dp.add_handler(note_conv_handler)
        dp.add_handler(CommandHandler('logros', show_logros))
        dp.add_handler(CommandHandler('contacto', contacto))

        logger.info("Bot iniciado correctamente. Presiona Ctrl+C para detener.")
        updater.start_polling()
        updater.idle()
        
    except Exception as e:
        logger.error(f"Error al iniciar el bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
