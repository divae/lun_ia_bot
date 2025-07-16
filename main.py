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
    ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, ContextTypes, filters
)
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
        moon_phase_value = phase(datetime.now())
        if moon_phase_value < 0.0625:
            return 0
        elif moon_phase_value < 0.1875:
            return 1
        elif moon_phase_value < 0.3125:
            return 1
        elif moon_phase_value < 0.4375:
            return 2
        elif moon_phase_value < 0.5625:
            return 2
        elif moon_phase_value < 0.6875:
            return 2
        elif moon_phase_value < 0.8125:
            return 3
        elif moon_phase_value < 0.9375:
            return 3
        else:
            return 0
    except Exception as e:
        logger.error(f"Error calculando fase lunar: {e}")
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

# Handlers asíncronos
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Bienvenid@! Usa /luna para ver el mensaje lunar de hoy, /intro para más info, o únete al canal: @lun_ia_oficial")

async def intro(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    await update.message.reply_text(msg)

async def moon(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Error en función moon: {e}")
        try:
            await update.message.reply_text("❌ Error al obtener información lunar. Intenta de nuevo.")
        except:
            logger.error("No se pudo enviar mensaje de error al usuario")

async def ask_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¿Qué quieres anotar hoy? Escribe tu avance. Usa /cancelar para cancelar.")
    return NOTE

async def save_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    note_text = update.message.text
    phase_idx = get_moon_phase()
    phase_name = MOON_PHASE_NAMES[phase_idx]
    now = datetime.now().strftime('%Y-%m-%d')
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
    await update.message.reply_text(f"✅ Nota guardada en {phase_name}. Usa /logros para ver tu historial.")
    return ConversationHandler.END

async def cancel_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Anotación cancelada.")
    return ConversationHandler.END

async def show_logros(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    try:
        with open("user_notes.json", "r", encoding="utf-8") as f:
            notes = json.load(f)
    except:
        notes = {}
    user_notes = notes.get(user_id, [])
    if not user_notes:
        await update.message.reply_text("Aún no tienes logros. Usa /anotar para registrar tu avance.")
        return
    msg = "📒 *Tus notas recientes:*\n\n"
    for n in user_notes[-10:][::-1]:
        msg += f"{n['date']} ({n['phase']}): {n['note']}\n\n"
    await update.message.reply_text(msg, parse_mode='Markdown')

async def get_mantra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /mantra [tema]\nTemas disponibles: proyectos, amor, creatividad, abundancia, proteccion, limpieza")
        return
    theme = context.args[0].lower()
    phase_idx = get_moon_phase()
    phase_name = MOON_PHASE_NAMES[phase_idx]
    try:
        mantras = RITUALS_DATA[phase_name]["mantras"]
        if theme in mantras:
            mantra = random.choice(mantras[theme])
            message = f"🧘‍♀️ *Mantra para {theme} en {phase_name}:*\n\n{mantra}\n\n💫 Repítelo 3 veces al día para potenciar su efecto."
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            available_themes = ", ".join(mantras.keys())
            await update.message.reply_text(f"Tema '{theme}' no disponible para {phase_name}.\nTemas disponibles: {available_themes}")
    except KeyError:
        await update.message.reply_text(f"No hay mantras disponibles para {phase_name}.")

async def get_meditacion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /meditacion [tema]\nTemas disponibles: proyectos, amor, creatividad, abundancia, proteccion, limpieza")
        return
    theme = context.args[0].lower()
    phase_idx = get_moon_phase()
    phase_name = MOON_PHASE_NAMES[phase_idx]
    try:
        meditaciones = RITUALS_DATA[phase_name]["meditaciones"]
        if theme in meditaciones:
            meditacion = random.choice(meditaciones[theme])
            message = f"🧘‍♀️ *Meditación para {theme} en {phase_name}:*\n\n{meditacion}\n\n✨ Dedica 5-10 minutos a esta práctica."
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            available_themes = ", ".join(meditaciones.keys())
            await update.message.reply_text(f"Tema '{theme}' no disponible para {phase_name}.\nTemas disponibles: {available_themes}")
    except KeyError:
        await update.message.reply_text(f"No hay meditaciones disponibles para {phase_name}.")

async def get_conjuro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /conjuro [tema]\nTemas disponibles: proteccion, abundancia, amor, creatividad, limpieza")
        return
    theme = context.args[0].lower()
    phase_idx = get_moon_phase()
    phase_name = MOON_PHASE_NAMES[phase_idx]
    try:
        conjuros = RITUALS_DATA[phase_name]["conjuros"]
        if theme in conjuros:
            conjuro = random.choice(conjuros[theme])
            message = f"🔮 *Conjuro para {theme} en {phase_name}:*\n\n{conjuro}\n\n🌟 Realiza este ritual con intención y fe."
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            available_themes = ", ".join(conjuros.keys())
            await update.message.reply_text(f"Tema '{theme}' no disponible para {phase_name}.\nTemas disponibles: {available_themes}")
    except KeyError:
        await update.message.reply_text(f"No hay conjuros disponibles para {phase_name}.")

async def contacto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Puedes contactarme en Telegram: @divae\nGracias por usar LUN.IA 🌙")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error en el bot: {context.error}")
    if update and hasattr(update, 'effective_message') and update.effective_message:
        await update.effective_message.reply_text("❌ Ocurrió un error. Por favor, intenta de nuevo más tarde.")

async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_error_handler(error_handler)
    note_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('anotar', ask_note)],
        states={NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_note)]},
        fallbacks=[CommandHandler('cancelar', cancel_note)]
    )
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('intro', intro))
    application.add_handler(CommandHandler('luna', moon))
    application.add_handler(CommandHandler('mantra', get_mantra))
    application.add_handler(CommandHandler('meditacion', get_meditacion))
    application.add_handler(CommandHandler('conjuro', get_conjuro))
    application.add_handler(note_conv_handler)
    application.add_handler(CommandHandler('logros', show_logros))
    application.add_handler(CommandHandler('contacto', contacto))
    logger.info("Bot iniciado correctamente. Presiona Ctrl+C para detener.")
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
