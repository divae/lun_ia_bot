# Lun IA Bot 🌙

Bot de Telegram que proporciona información lunar, rituales y meditaciones basadas en las fases de la luna.

## Estado Actual

✅ **Código funcional restaurado** - Se ha vuelto al código original que funcionaba correctamente antes del refactor a arquitectura hexagonal.

## Características

- 🌙 Información de fases lunares en tiempo real
- 📅 Cálculo de salida de luna para Madrid y Buenos Aires
- ✨ Rituales y meditaciones personalizadas
- 📝 Sistema de anotaciones y logros
- 🎯 Mantras y conjuros lunares
- 🌍 Datos científicos sobre la luna

## Instalación

1. Clonar el repositorio
2. Crear entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En macOS/Linux
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configurar variables de entorno:
   ```bash
   cp config.env.example config.env
   # Editar config.env con tu TOKEN de Telegram
   ```

## Uso

```bash
python bot.py
```

## Comandos Disponibles

- `/luna` - Información lunar del día
- `/anotar` - Registrar avance o idea
- `/logros` - Ver historial de anotaciones
- `/meditacion [tema]` - Meditación personalizada
- `/mantra [tema]` - Mantra lunar
- `/conjuro [tema]` - Conjuro lunar
- `/contacto` - Información de contacto

## Estructura del Proyecto

```
lun_IA_bot/
├── bot.py                 # Código principal del bot
├── requirements.txt       # Dependencias
├── moon_data.json        # Datos de fases lunares
├── moon_science_data.json # Datos científicos
├── rituals_db.json       # Base de datos de rituales
├── config.env.example    # Ejemplo de configuración
└── luniabot/            # Código original (backup)
```

## Notas Importantes

- El código ha sido restaurado a su estado funcional original
- Se eliminó la estructura de arquitectura hexagonal que causaba problemas
- Todas las funcionalidades están operativas
- El bot está listo para usar con la configuración correcta

## Próximos Pasos

Si deseas implementar arquitectura hexagonal en el futuro, se recomienda:
1. Crear una rama separada para el refactor
2. Implementar cambios incrementales
3. Mantener el código funcional en la rama principal
4. Probar exhaustivamente antes de hacer merge 