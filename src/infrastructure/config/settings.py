"""
Configuración centralizada de la aplicación
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno de forma segura
try:
    load_dotenv()
    print("✅ Variables de entorno cargadas desde .env")
except Exception as e:
    print(f"⚠️  Advertencia: No se pudo cargar .env: {e}")

class Settings:
    """Configuración de la aplicación"""
    env = SimpleEnviron()

    # Configuración de Telegram (OBLIGATORIA)
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME", "@lun_ia_my_bot")
    
    # Configuración de datos
    DATA_DIR = Path("data")
    LUNAR_DATA_FILE = DATA_DIR / "lunar_data" / "lunar_components.json"
    USER_DATA_DIR = DATA_DIR / "user_data"
    
    # Configuración de ubicación (Madrid por defecto)
    try:
        DEFAULT_LATITUDE = float(os.getenv("DEFAULT_LATITUDE", "40.4168"))
        DEFAULT_LONGITUDE = float(os.getenv("DEFAULT_LONGITUDE", "-3.7038"))
    except ValueError:
        print("⚠️  Advertencia: Valores de latitud/longitud inválidos, usando valores por defecto")
        DEFAULT_LATITUDE = 40.4168
        DEFAULT_LONGITUDE = -3.7038
    
    # Configuración de logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "bot.log")
    
    # Configuración de mensajes
    MAX_MESSAGE_LENGTH = 4096
    DEFAULT_LANGUAGE = "es"
    
    @classmethod
    def validate(cls) -> bool:
        """Valida que la configuración sea correcta"""
        # Validar TELEGRAM_TOKEN (OBLIGATORIO)
        if not cls.TELEGRAM_TOKEN or cls.TELEGRAM_TOKEN == "tu_token_de_telegram_aqui":
            print("❌ Error: TELEGRAM_TOKEN no está configurado correctamente")
            print("💡 Configura la variable TELEGRAM_TOKEN en tu archivo .env")
            print("💡 Ejemplo: TELEGRAM_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
            return False
        
        # Validar formato del token (debe tener formato bot_id:bot_token)
        if ":" not in cls.TELEGRAM_TOKEN:
            print("❌ Error: TELEGRAM_TOKEN tiene formato inválido")
            print("💡 El token debe tener el formato: bot_id:bot_token")
            return False
        
        print(f"✅ Token de Telegram configurado: {cls.TELEGRAM_TOKEN[:10]}...")
        print(f"✅ Username del bot: {cls.TELEGRAM_BOT_USERNAME}")
        print(f"✅ Ubicación: {cls.DEFAULT_LATITUDE}, {cls.DEFAULT_LONGITUDE}")
        print(f"✅ Nivel de logging: {cls.LOG_LEVEL}")
        
        # Crear directorios si no existen de forma más robusta
        try:
            # Crear directorio de datos principal
            if not cls.DATA_DIR.exists():
                cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
                print(f"✅ Directorio creado: {cls.DATA_DIR}")
            
            # Crear directorio de datos lunares
            lunar_data_dir = cls.LUNAR_DATA_FILE.parent
            if not lunar_data_dir.exists():
                lunar_data_dir.mkdir(parents=True, exist_ok=True)
                print(f"✅ Directorio creado: {lunar_data_dir}")
            
            # Crear directorio de datos de usuario
            if not cls.USER_DATA_DIR.exists():
                cls.USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
                print(f"✅ Directorio creado: {cls.USER_DATA_DIR}")
                
        except Exception as e:
            print(f"⚠️  Advertencia: No se pudieron crear directorios de datos: {e}")
            # Continuar aunque falle la creación de directorios
        
        if not cls.LUNAR_DATA_FILE.exists():
            print(f"⚠️  Advertencia: Archivo de datos no encontrado: {cls.LUNAR_DATA_FILE}")
            print("💡 El bot funcionará con datos por defecto")
        
        return True
    
    @classmethod
    def get_data_paths(cls) -> dict:
        """Obtiene las rutas de datos"""
        return {
            "lunar_data": cls.LUNAR_DATA_FILE,
            "user_data": cls.USER_DATA_DIR,
            "data_dir": cls.DATA_DIR
        }
    
    @classmethod
    def print_config(cls):
        """Imprime la configuración actual (sin mostrar el token completo)"""
        print("🔧 Configuración actual:")
        print(f"   - Token: {cls.TELEGRAM_TOKEN[:10]}..." if cls.TELEGRAM_TOKEN else "   - Token: NO CONFIGURADO")
        print(f"   - Username: {cls.TELEGRAM_BOT_USERNAME}")
        print(f"   - Ubicación: {cls.DEFAULT_LATITUDE}, {cls.DEFAULT_LONGITUDE}")
        print(f"   - Log Level: {cls.LOG_LEVEL}")
        print(f"   - Log File: {cls.LOG_FILE}") 