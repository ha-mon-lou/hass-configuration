# forecast_home.py
# Crea sensores dinámicos para el forecast de weather.forecast_home_2

entity_id = 'weather.forecast_home_2'

# Llamamos al servicio para obtener forecast diario
forecast_data = hass.services.call(
    'weather', 'get_forecasts',
    service_data={
        'entity_id': entity_id,
        'type': 'daily'
    },
    blocking=True
)

# forecast_data ahora tiene la lista de días
forecast = forecast_data if forecast_data else []

if not forecast:
    logger.warning("⚠️ forecast vacío o no disponible")
else:
    for i, day in enumerate(forecast[:7]):
        day_index = i + 1
        # Temperatura máxima
        hass.states.set(f'sensor.fc{day_index}_temp', day.get('temperature', 'unknown'), {
            'friendly_name': f'Temperatura día {day_index}',
            'unit_of_measurement': '°C'
        })
        # Temperatura mínima
        hass.states.set(f'sensor.fc{day_index}_templow', day.get('templow', 'unknown'), {
            'friendly_name': f'Temperatura min día {day_index}',
            'unit_of_measurement': '°C'
        })
        # Condición
        hass.states.set(f'sensor.fc{day_index}_condition', day.get('condition', 'unknown'), {
            'friendly_name': f'Condición día {day_index}'
        })
        # Precipitación
        hass.states.set(f'sensor.fc{day_index}_precip', day.get('precipitation', 0), {
            'friendly_name': f'Precipitación día {day_index}',
            'unit_of_measurement': 'mm'
        })

logger.info("✅ Sensores forecast creados correctamente")
