# forecast_alert.py
# Evalúa condiciones adversas en el forecast usando thresholds dinámicos y dispara acciones

forecast = data.get("forecast", [])
location = data.get("location", "home")

if not forecast:
    logger.warning(f"[{location}] No se recibió forecast en forecast_alert")

# ---- Leer umbrales desde HA ----
def get_input_number(entity_id, default):
    """Lee un input_number y devuelve float"""
    s = hass.states.get(entity_id)
    if s is None:
        return default
    try:
        return float(s.state)
    except:
        return default

THRESHOLDS = {
    "wind_speed": get_input_number("input_number.forecast_threshold_wind_speed", 50),
    "precipitation": get_input_number("input_number.forecast_threshold_precipitation", 5),
    "temperature_low": get_input_number("input_number.forecast_threshold_temperature_low", -5),
    "temperature_high": get_input_number("input_number.forecast_threshold_temperature_high", 35),
    "humidity_high": get_input_number("input_number.forecast_threshold_humidity_high", 95),
}

# ---- Revisar próximas 12h ----
next12 = forecast[:12]
alertas = []

for f in next12:
    dt = f.get("datetime")[11:16]

    wind = f.get("wind_speed")
    if wind is not None and wind >= THRESHOLDS["wind_speed"]:
        alertas.append(f"💨 Viento fuerte: {wind} km/h a las {dt}")

    rain = f.get("precipitation")
    if rain is not None and rain >= THRESHOLDS["precipitation"]:
        alertas.append(f"🌧️ Precipitación intensa: {rain} mm/h a las {dt}")

    temp = f.get("temperature")
    if temp is not None:
        if temp <= THRESHOLDS["temperature_low"]:
            alertas.append(f"🥶 Temperatura baja: {temp}°C a las {dt}")
        elif temp >= THRESHOLDS["temperature_high"]:
            alertas.append(f"🥵 Temperatura alta: {temp}°C a las {dt}")

    hum = f.get("humidity")
    if hum is not None and hum >= THRESHOLDS["humidity_high"]:
        alertas.append(f"💦 Humedad alta: {hum}% a las {dt}")

# ---- Si hay alertas ----
if alertas:
    alerts_text = "\n".join(alertas)

    # 1️⃣ Disparar evento forecast_alert
    hass.bus.fire("forecast_alert", {"location": location, "details": alerts_text})
    logger.warning(f"[{location}] ALERTA meteorológica:\n{alerts_text}")

