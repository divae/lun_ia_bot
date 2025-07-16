# 🌙 LUN.IA - Bot Lunar Inteligente

Un bot de Telegram que combina astronomía real, datos científicos y rituales prácticos para conectar tus proyectos y bienestar con la energía de la Luna.

## ✨ Características

### 🌕 **Mensajes Lunares Inteligentes**
- **Datos astronómicos reales**: Iluminación lunar, distancia Tierra-Luna
- **Información zodiacal**: Signo actual de la Luna
- **Datos científicos curiosos**: Información educativa sobre cada fase lunar
- **Rituales prácticos**: Instrucciones claras y accesibles
- **Orientación específica**: Recomendaciones según la fase lunar

### 🧘 **Funcionalidades Espirituales**
- **Meditaciones personalizadas** por tema y fase lunar
- **Mantras específicos** para diferentes propósitos
- **Conjuros lunares** adaptados a cada fase
- **Sistema de anotaciones** para registrar avances y logros
- **Historial personal** de notas y reflexiones

### 📱 **Comandos Disponibles**
- `/luna` - Mensaje lunar del día con formato mejorado
- `/anotar` - Registrar avance, idea o logro personal
- `/logros` - Ver historial de notas guardadas
- `/meditacion [tema]` - Meditación personalizada por fase lunar
- `/mantra [tema]` - Mantra específico para diferentes propósitos
- `/conjuro [tema]` - Ritual/conjuro lunar personalizado
- `/contacto` - Información de contacto
- `/intro` - Información sobre el bot

### 🎯 **Temas Disponibles**
- **proyectos** - Para desarrollo personal y profesional
- **amor** - Para relaciones y conexiones
- **creatividad** - Para inspiración y expresión artística
- **abundancia** - Para prosperidad y abundancia
- **proteccion** - Para protección y seguridad
- **limpieza** - Para limpieza energética y renovación

## 🚀 Instalación

### Prerrequisitos
- Python 3.9+
- Token de Telegram Bot
- Entorno virtual (recomendado)

### Pasos de instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd lun_IA_bot
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
echo 'TELEGRAM_TOKEN="tu_token_aqui"' > .env
```

5. **Ejecutar el bot**
```bash
python main.py
```

## 📊 Estructura del Proyecto

```
lun_IA_bot/
├── main.py                # Archivo principal del bot
├── moon_data.json         # Base de datos de contenido lunar
├── moon_science_data.json # Datos científicos y rituales
├── rituals_db.json        # Base de datos de rituales
├── user_notes.json        # Notas de usuarios (se crea automáticamente)
├── requirements.txt       # Dependencias de Python
├── .env                   # Variables de entorno (no incluido en git)
├── LICENSE                # Licencia MIT del proyecto
└── README.md             # Este archivo
```

## 🔧 Tecnologías Utilizadas

- **Python 3.9+** - Lenguaje principal
- **python-telegram-bot** - API de Telegram
- **astral** - Cálculos astronómicos
- **python-dotenv** - Gestión de variables de entorno
- **Pillow** - Manejo y detección de imágenes (reemplazo estándar de imghdr en Python 3.13+)
- **JSON** - Almacenamiento de datos

## 🌟 Características Técnicas

### **Cálculos Astronómicos**
- Fase lunar en tiempo real
- Porcentaje de iluminación
- Distancia Tierra-Luna aproximada
- Horarios de salida de la luna para Madrid y Buenos Aires

### **Sistema de Datos**
- Base de datos JSON para contenido lunar
- Datos científicos específicos por fase
- Rituales prácticos y accesibles
- Sistema de anotaciones por usuario

### **Funcionalidades Avanzadas**
- Sistema robusto de manejo de errores
- Logging detallado para monitoreo
- Validación de archivos JSON y configuración
- Sistema de conversación para anotaciones
- Comandos administrativos para gestión de contenido
- Envío automático de mensajes al canal oficial

## 📈 Roadmap

### **Próximas Funcionalidades**
- [ ] Integración con APIs de LLM para contenido dinámico
- [ ] Predicciones astrológicas más precisas
- [ ] Sistema de recordatorios personalizados
- [ ] Análisis de patrones en las anotaciones
- [ ] Integración con calendarios personales

### **Mejoras Técnicas**
- [ ] Base de datos SQL para mejor rendimiento
- [ ] API REST para integraciones externas
- [ ] Sistema de caché para cálculos astronómicos
- [ ] Logs estructurados para monitoreo

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'feat: add amazing feature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### **Convenciones de Commits**
Seguimos [Conventional Commits](https://carlosazaustre.es/conventional-commits):
- `feat:` nuevas funcionalidades
- `fix:` correcciones de bugs
- `docs:` cambios en documentación
- `style:` cambios de formato
- `refactor:` refactorización de código
- `test:` agregar o modificar tests
- `chore:` cambios en build o herramientas

## 📞 Contacto

- **Desarrollador**: @divae
- **Canal oficial**: @lun_ia_oficial
- **Bot**: @lun_ia_my_bot

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. El archivo `LICENSE` ya está incluido y nombra explícitamente a Estela García como autora del código.

## 🙏 Agradecimientos

- Comunidad de usuarios que inspiran nuevas funcionalidades
- Librerías de código abierto que hacen posible este proyecto
- La Luna por ser nuestra inspiración constante

---

**¿List@ para conectar tus proyectos y tu bienestar con la energía de la Luna?** 🌕✨ 