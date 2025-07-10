import os
from dotenv import load_dotenv
from telegram.ext import CommandHandler
from datetime import datetime
import random
import json
from telegram.ext import ApplicationBuilder
import locale
from astral import LocationInfo
from astral.moon import moonrise, phase
from astral.sun import sun
from telegram.ext import ConversationHandler, MessageHandler, filters
from telegram import BotCommand, ReplyKeyboardMarkup
import math

load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
# Constants for moon phase calculation
MOON_CYCLE_DAYS = 30
NEW_MOON_THRESHOLD = 7
FIRST_QUARTER_THRESHOLD = 15
FULL_MOON_THRESHOLD = 22

# Fases lunares en el mismo orden que en moon_data.json
MOON_PHASE_NAMES = ["Luna Nueva", "Cuarto Creciente", "Luna Llena", "Cuarto Menguante"]

# Cargar datos desde el archivo JSON
with open("moon_data.json", encoding="utf-8") as f:
    MOON_DATA = json.load(f)

# Cargar datos científicos
with open("moon_science_data.json", encoding="utf-8") as f:
    MOON_SCIENCE_DATA = json.load(f)

locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

def get_moon_phase():
    """Calculate the current moon phase index (0-3)."""
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day
    r = year % 100
    r %= 19
    if r > 9:
        r -= 19
    phase = ((r * 11) % MOON_CYCLE_DAYS) + month + day
    if month < 3:
        phase += 2
    phase -= 8.3
    phase = int(phase + 0.5) % MOON_CYCLE_DAYS
    if phase < NEW_MOON_THRESHOLD:
        return 0  # Luna Nueva
    if phase < FIRST_QUARTER_THRESHOLD:
        return 1  # Cuarto Creciente
    if phase < FULL_MOON_THRESHOLD:
        return 2  # Luna Llena
    return 3      # Cuarto Menguante

def days_until_new_moon():
    """Calculate days remaining until the next New Moon."""
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day
    r = year % 100
    r %= 19
    if r > 9:
        r -= 19
    phase = ((r * 11) % MOON_CYCLE_DAYS) + month + day
    if month < 3:
        phase += 2
    phase -= 8.3
    phase = int(phase + 0.5) % MOON_CYCLE_DAYS
    days = (MOON_CYCLE_DAYS - phase) % MOON_CYCLE_DAYS
    if days == 0:
        days = MOON_CYCLE_DAYS
    return days

def get_moon_illumination():
    """Get current moon illumination percentage."""
    now = datetime.now()
    moon_phase_value = phase(now)
    # Convert phase (0-1) to illumination percentage
    illumination = abs(math.sin(moon_phase_value * math.pi)) * 100
    return round(illumination, 1)

def get_moon_distance():
    """Get approximate distance to moon in km."""
    # Simplified calculation - moon distance varies between ~356,000 and ~406,000 km
    now = datetime.now()
    # Use day of year to approximate distance variation
    day_of_year = now.timetuple().tm_yday
    base_distance = 384400  # Average distance in km
    variation = 25000 * math.sin(2 * math.pi * day_of_year / 365.25)
    distance = base_distance + variation
    return round(distance, -3)  # Round to nearest 1000

def get_zodiac_sign():
    """Get current zodiac sign for the moon."""
    # Simplified zodiac calculation based on date
    now = datetime.now()
    month = now.month
    day = now.day
    
    zodiac_signs = [
        ("Capricornio", 1, 19), ("Acuario", 1, 20), ("Piscis", 2, 19),
        ("Aries", 3, 20), ("Tauro", 4, 20), ("Géminis", 5, 21),
        ("Cáncer", 6, 21), ("Leo", 7, 22), ("Virgo", 8, 22),
        ("Libra", 9, 22), ("Escorpio", 10, 22), ("Sagitario", 11, 21),
        ("Capricornio", 12, 22)
    ]
    
    for sign, start_month, start_day in zodiac_signs:
        if (month == start_month and day >= start_day) or \
           (month == (start_month % 12) + 1 and day < zodiac_signs[zodiac_signs.index((sign, start_month, start_day)) + 1][2] if zodiac_signs.index((sign, start_month, start_day)) < len(zodiac_signs) - 1 else zodiac_signs[0][2]):
            return sign
    
    return "Capricornio"  # Default fallback

# Fragmento reutilizable para recordar los comandos disponibles
COMMANDS_REMINDER = (
    "\n━━━━━━━━━━━━━━\n"
    "Comandos disponibles:\n"
    "/luna – Mensaje lunar\n"
    "/anotar – Registrar avance o idea\n"
    "/logros – Ver historial\n"
    "/meditacion [tema] – Inspiración personalizada\n"
    "/mantra [tema] – Mantra lunar\n"
    "/conjuro [tema] – Conjuro lunar\n"
    "/contacto – Contactar o info\n"
)

async def moon(update, context):
    """Send the current day in Spanish, the lunar message, and moonrise times for Madrid and Buenos Aires."""
    idx = get_moon_phase()
    phase_name = MOON_PHASE_NAMES[idx]
    phase_data = MOON_DATA[phase_name]
    science_data = MOON_SCIENCE_DATA[phase_name]
    days = days_until_new_moon()
    illumination = get_moon_illumination()
    distance = get_moon_distance()
    zodiac = get_zodiac_sign()
    now = datetime.now().strftime('%A, %-d de %B de %Y')
    date_formatted = datetime.now().strftime('%-d %B %Y')

    # Moonrise for Madrid (hemisferio norte)
    madrid = LocationInfo("Madrid", "Spain", "Europe/Madrid", 40.4168, -3.7038)
    buenos_aires = LocationInfo("Buenos Aires", "Argentina", "America/Argentina/Buenos_Aires", -34.61, -58.38)
    today = datetime.now().date()
    try:
        moonrise_madrid = moonrise(madrid.observer, date=today)
        moonrise_madrid_str = moonrise_madrid.strftime('%H:%M') if moonrise_madrid else "No visible"
    except Exception:
        moonrise_madrid_str = "No visible"
    try:
        moonrise_ba = moonrise(buenos_aires.observer, date=today)
        moonrise_ba_str = moonrise_ba.strftime('%H:%M') if moonrise_ba else "No visible"
    except Exception:
        moonrise_ba_str = "No visible"

    # Determinar emoji de fase lunar
    phase_emoji = {
        "Luna Nueva": "🌑",
        "Cuarto Creciente": "🌓", 
        "Luna Llena": "🌕",
        "Cuarto Menguante": "🌗"
    }

    message = (
        f"{phase_emoji[phase_name]} *{phase_name} en {zodiac} – {date_formatted}* {phase_emoji[phase_name]}\n\n"
        f"✨ *Iluminación:* {illumination}%\n"
        f"🌍 *Distancia Tierra-Luna:* ~{distance:,} km\n\n"
        f"👉 *Dato curioso:*\n"
        f"{science_data['curiosidad']}\n\n"
        f"✨ *Ritual breve para hoy:*\n"
        f"{science_data['ritual_breve']}\n\n"
        f"*Es momento de:*\n"
    )

    # Agregar recomendaciones específicas según la fase
    if phase_name == "Luna Nueva":
        message += "🌱 Comenzar nuevos proyectos.\n🎯 Establecer intenciones.\n💫 Planificar el futuro.\n"
    elif phase_name == "Cuarto Creciente":
        message += "🌱 Desarrollar y expandir.\n🎯 Tomar acción.\n💪 Construir momentum.\n"
    elif phase_name == "Luna Llena":
        message += "🌱 Cerrar ciclos.\n🎯 Ordenar prioridades.\n💪 Tomar decisiones con madurez.\n"
    else:  # Cuarto Menguante
        message += "🌱 Liberar y soltar.\n🎯 Limpiar y organizar.\n💪 Reflexionar y descansar.\n"

    message += f"\n¿Quieres inspiración personalizada, mantras, meditaciones o anotar tus logros?\n"
    message += f"Habla conmigo en privado: @lun_ia_my_bot"

    await update.message.reply_text(message, parse_mode='Markdown')
    keyboard = [
        ["/luna", "/anotar", "/logros"],
        ["/meditacion", "/mantra", "/conjuro"],
        ["/contacto"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "¿Te gustaría anotar algo sobre tu proyecto hoy? Usa /anotar para registrar tu avance, idea o logro.",
        reply_markup=reply_markup
    )

async def start(update, context):
    await update.message.reply_text("¡Bienvenid@! Usa /luna para ver el mensaje lunar de hoy, /intro para más información sobre el bot, y únete al canal oficial: @lun_ia_oficial")

async def intro(update, context):
    msg = (
        "🌙 ¡Bienvenid@ a LUN.IA!\n\n"
        "Aquí puedes recibir inspiración lunar diaria, recomendaciones, rituales, mantras, meditaciones y tips para tus proyectos y bienestar.\n\n"
        "✨ ¿Qué puedes hacer?\n"
        "- Usa /luna para ver el mensaje lunar del día.\n"
        "- Usa /anotar para registrar tus avances, ideas o logros personales.\n"
        "- Usa /logros para ver tu historial de notas.\n"
        "- Usa /meditacion [tema], /mantra [tema] o /conjuro [tema] para recibir inspiración personalizada según la fase lunar y el tema que elijas.\n"
        "  Ejemplos de temas: proyectos, amor, creatividad, protección, abundancia, limpieza...\n"
        "- Usa /contacto para saber cómo contactar o apoyar el proyecto.\n\n"
        "Únete al canal oficial para recibir novedades y mensajes diarios: @lun_ia_oficial\n\n"
        "¿List@ para conectar tus proyectos y tu bienestar con la energía de la Luna? 🌕\n\n"
        "¡Escribe /luna para comenzar!"
    )
    await update.message.reply_text(msg)

NOTE, = range(1)

async def ask_note(update, context):
    await update.message.reply_text(
        "¿Te gustaría anotar algo sobre tu proyecto hoy? Escribe tu avance, bloqueo, idea o logro y lo guardaré para ti.\n\nSi no quieres anotar nada, escribe /cancelar.")
    return NOTE

async def save_note(update, context):
    user_id = str(update.effective_user.id)
    note_text = update.message.text
    now = datetime.now()
    phase_idx = get_moon_phase()
    phase_name = MOON_PHASE_NAMES[phase_idx]
    note_entry = {
        "date": now.strftime('%Y-%m-%d'),
        "phase": phase_name,
        "note": note_text
    }
    # Cargar y guardar en user_notes.json
    try:
        with open("user_notes.json", "r", encoding="utf-8") as f:
            notes = json.load(f)
    except Exception:
        notes = {}
    if user_id not in notes:
        notes[user_id] = []
    notes[user_id].append(note_entry)
    with open("user_notes.json", "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)
    await update.message.reply_text("¡Nota guardada! Puedes ver tu historial con /logros.")
    return ConversationHandler.END

async def cancel_note(update, context):
    await update.message.reply_text("Anotación cancelada.")
    return ConversationHandler.END

async def show_logros(update, context):
    user_id = str(update.effective_user.id)
    try:
        with open("user_notes.json", "r", encoding="utf-8") as f:
            notes = json.load(f)
    except Exception:
        notes = {}
    user_notes = notes.get(user_id, [])
    if not user_notes:
        await update.message.reply_text("Aún no tienes logros ni notas guardadas. Usa /anotar para registrar tu avance.")
        return
    msg = "📒 *Tu historial de notas y logros:*\n\n"
    for n in user_notes[-10:][::-1]:
        msg += f"{n['date']} ({n['phase']}):\n{n['note']}\n\n"
    await update.message.reply_text(msg, parse_mode='Markdown')

async def meditacion(update, context):
    args = context.args
    tema = args[0].lower() if args else 'proyectos'
    phase_idx = get_moon_phase()
    phase_name = MOON_PHASE_NAMES[phase_idx]
    try:
        with open("rituals_db.json", "r", encoding="utf-8") as f:
            rituals_db = json.load(f)
        meditaciones = rituals_db[phase_name]["meditaciones"].get(tema, [])
    except Exception:
        meditaciones = []
    if meditaciones:
        texto = random.choice(meditaciones)
        await update.message.reply_text(f"🧘 Meditación para {tema} en {phase_name}:\n\n{texto}")
    else:
        await update.message.reply_text(f"No hay meditaciones para el tema '{tema}' en {phase_name}.")

async def mantra(update, context):
    args = context.args
    tema = args[0].lower() if args else 'proyectos'
    phase_idx = get_moon_phase()
    phase_name = MOON_PHASE_NAMES[phase_idx]
    try:
        with open("rituals_db.json", "r", encoding="utf-8") as f:
            rituals_db = json.load(f)
        mantras = rituals_db[phase_name]["mantras"].get(tema, [])
    except Exception:
        mantras = []
    if mantras:
        texto = random.choice(mantras)
        await update.message.reply_text(f"🧘 Mantra para {tema} en {phase_name}:\n\n{texto}")
    else:
        await update.message.reply_text(f"No hay mantras para el tema '{tema}' en {phase_name}.")

async def conjuro(update, context):
    args = context.args
    tema = args[0].lower() if args else 'proteccion'
    phase_idx = get_moon_phase()
    phase_name = MOON_PHASE_NAMES[phase_idx]
    try:
        with open("rituals_db.json", "r", encoding="utf-8") as f:
            rituals_db = json.load(f)
        conjuros = rituals_db[phase_name]["conjuros"].get(tema, [])
    except Exception:
        conjuros = []
    if conjuros:
        texto = random.choice(conjuros)
        await update.message.reply_text(f"✨ Conjuro para {tema} en {phase_name}:\n\n{texto}")
    else:
        await update.message.reply_text(f"No hay conjuros para el tema '{tema}' en {phase_name}.")

async def contacto(update, context):
    msg = (
        "Puedes contactarme directamente en Telegram: @divae\n\n"
        "Transparencia: este bot utiliza IA y experiencia personal para inspirar y acompañar proyectos y bienestar.\n"
    )
    await update.message.reply_text(msg)

# Conversation handler para anotar
note_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('anotar', ask_note)],
    states={
        NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_note)]
    },
    fallbacks=[CommandHandler('cancelar', cancel_note)]
)

CHANNEL_CHAT_ID = '@lun_ia_oficial'

async def send_daily_moon_message(app):
    idx = get_moon_phase()
    phase_name = MOON_PHASE_NAMES[idx]
    phase_data = MOON_DATA[phase_name]
    science_data = MOON_SCIENCE_DATA[phase_name]
    days = days_until_new_moon()
    illumination = get_moon_illumination()
    distance = get_moon_distance()
    zodiac = get_zodiac_sign()
    now = datetime.now().strftime('%A, %-d de %B de %Y')
    date_formatted = datetime.now().strftime('%-d %B %Y')

    # Determinar emoji de fase lunar
    phase_emoji = {
        "Luna Nueva": "🌑",
        "Cuarto Creciente": "🌓", 
        "Luna Llena": "🌕",
        "Cuarto Menguante": "🌗"
    }

    message = (
        f"{phase_emoji[phase_name]} *{phase_name} en {zodiac} – {date_formatted}* {phase_emoji[phase_name]}\n\n"
        f"✨ *Iluminación:* {illumination}%\n"
        f"🌍 *Distancia Tierra-Luna:* ~{distance:,} km\n\n"
        f"👉 *Dato curioso:*\n"
        f"{science_data['curiosidad']}\n\n"
        f"✨ *Ritual breve para hoy:*\n"
        f"{science_data['ritual_breve']}\n\n"
        f"*Es momento de:*\n"
    )

    # Agregar recomendaciones específicas según la fase
    if phase_name == "Luna Nueva":
        message += "🌱 Comenzar nuevos proyectos.\n🎯 Establecer intenciones.\n💫 Planificar el futuro.\n"
    elif phase_name == "Cuarto Creciente":
        message += "🌱 Desarrollar y expandir.\n🎯 Tomar acción.\n💪 Construir momentum.\n"
    elif phase_name == "Luna Llena":
        message += "🌱 Cerrar ciclos.\n🎯 Ordenar prioridades.\n💪 Tomar decisiones con madurez.\n"
    else:  # Cuarto Menguante
        message += "🌱 Liberar y soltar.\n🎯 Limpiar y organizar.\n💪 Reflexionar y descansar.\n"

    message += f"\n¿Quieres inspiración personalizada, mantras, meditaciones o anotar tus logros?\n"
    message += f"Habla conmigo en privado: [@lun_ia_my_bot](https://t.me/lun_ia_my_bot)"
    
    await app.bot.send_message(chat_id=CHANNEL_CHAT_ID, text=message, parse_mode='Markdown')

async def post_init(app):
    commands = [
        BotCommand('luna', 'Mensaje lunar del día'),
        BotCommand('lunarhoy', 'Reenviar mensaje lunar de hoy'),
        BotCommand('anotar', 'Registrar avance o idea'),
        BotCommand('logros', 'Ver historial de notas'),
        BotCommand('meditacion', 'Inspiración personalizada'),
        BotCommand('mantra', 'Mantra lunar'),
        BotCommand('conjuro', 'Conjuro lunar'),
        BotCommand('contacto', 'Contactar o info'),
        BotCommand('intro', 'Información sobre el bot'),
        BotCommand('cancelar', 'Cancelar anotación')
    ]
    await app.bot.set_my_commands(commands)

# Nuevo comando para enviar el mensaje lunar diario manualmente al canal, solo para la administradora
ADMIN_USERNAMES = ["divae", "EstelaYoMisma"]
async def enviarluna(update, context):
    if update.effective_user.username not in ADMIN_USERNAMES:
        await update.message.reply_text("⛔ Este comando solo está disponible para la administradora.")
        return
    await send_daily_moon_message(context.application)
    await update.message.reply_text("✅ Mensaje lunar enviado al canal.")

async def generarluna(update, context):
    if update.effective_user.username not in ADMIN_USERNAMES:
        await update.message.reply_text("⛔ Este comando solo está disponible para la administradora.")
        return
    idx = get_moon_phase()
    phase_name = MOON_PHASE_NAMES[idx]
    phase_data = MOON_DATA[phase_name]
    days = days_until_new_moon()
    recommendation = random.choice(phase_data["recommendations"])
    ritual = random.choice(phase_data["rituals"])
    quote = random.choice(phase_data["quotes"])
    tip = random.choice(phase_data["tips"])
    now = datetime.now().strftime('%A, %-d de %B de %Y')
    message = (
        f"✨ *LUN.IA - Mensaje Lunar Diario* ✨\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📅 *{now.capitalize()}*\n"
        f"🌙 *Fase lunar:* {phase_name}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔮 *Recomendación:*\n{recommendation}\n\n"
        f"🧘 *Ritual:*\n{ritual}\n\n"
        f"💬 *Cita del día:*\n_{quote}_\n\n"
        f"🗓️ *Próxima Luna Nueva:* Faltan {days} días\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 *Tip lunar:* {tip}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"¿Quieres inspiración personalizada, mantras, meditaciones o anotar tus logros?\n"
        f"Habla conmigo en privado: [@lun_ia_my_bot](https://t.me/lun_ia_my_bot)"
    )
    await update.message.reply_text(message, parse_mode='Markdown')

async def lunarhoy(update, context):
    if update.effective_user.username not in ADMIN_USERNAMES:
        await update.message.reply_text("⛔ Este comando solo está disponible para la administradora.")
        return
    await moon(update, context)

def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_TOKEN is not set in the environment.")
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('luna', moon))
    app.add_handler(CommandHandler('lunarhoy', lunarhoy))
    app.add_handler(CommandHandler('logros', show_logros))
    app.add_handler(note_conv_handler)
    app.add_handler(CommandHandler('meditacion', meditacion))
    app.add_handler(CommandHandler('mantra', mantra))
    app.add_handler(CommandHandler('conjuro', conjuro))
    app.add_handler(CommandHandler('contacto', contacto))
    app.add_handler(CommandHandler('intro', intro))
    app.add_handler(CommandHandler('enviarluna', enviarluna))
    app.add_handler(CommandHandler('generarluna', generarluna))
    app.run_polling()

if __name__ == "__main__":
    main() 