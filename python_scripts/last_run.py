# last_run.py
# Crea o actualiza un sensor con la fecha/hora de la última ejecución
# usando sensores nativos de HA (no imports)

# Leemos el estado del sensor de fecha y hora de HA
now = hass.states.get("sensor.date_time")
if now is None:
    value = "unknown"
else:
    value = now.state

# Creamos/actualizamos un sensor con ese valor
hass.states.set(
    "sensor.python_last_run",
    value,
    {
        "friendly_name": "Última ejecución script",
        "icon": "mdi:clock-outline"
    }
)

logger.info(f"✅ python_script last_run ejecutado, valor: {value}")
