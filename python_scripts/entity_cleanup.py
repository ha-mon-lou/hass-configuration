# forecast_cleanup.py
# Limpia sensores temporales de forecast que ya no se usan

# Lista de patrones de sensores a limpiar
patterns = [
    "sensor.multi_forecast_home_",
    "sensor.multi_forecast_work_",
    "sensor.forecast_home_",
    "sensor.forecast_work_"
]

# Itera sobre todas las entidades
for entity_id in hass.states.entity_ids():
    for pattern in patterns:
        if entity_id.startswith(pattern):
            # Borra el estado de la entidad
            hass.states.set(entity_id, None)
            logger.info(f"Entidad limpiada: {entity_id}")
