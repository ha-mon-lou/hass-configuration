# forecast_trip.py
# Script Python para resumir el forecast del trayecto casa->trabajo y vuelta
# Usando thresholds dinámicos desde Home Assistant

# ---- Obtener datos de entrada ----
home_forecast = data.get("forecast_home", [])
work_forecast = data.get("forecast_work", [])
departure_hour = int(data.get("departure_hour", 8))
trip_duration = int(data.get("trip_duration", 6))
current_hour_str = data.get("current_hour", "0:00")
current_hour = int(current_hour_str.split(":")[0])
temp_exterior = data.get("temperature", "??")
hum_exterior = data.get("humidity", "??")
location = data.get("location", "home")

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

# ---- Funciones auxiliares ----
rain_conditions = [
    "rainy", "pouring", "hail",
    "lightning", "lightning-rainy", "snowy-rainy"
]

def next_hours(forecast, start_hour, duration):
    """Devuelve los próximos `duration` elementos a partir de la hora >= start_hour"""
    hours = []
    for f in forecast:
        dt_hour = int(f.get("datetime")[11:13])
        if dt_hour >= start_hour:
            hours.append(f)
        if len(hours) >= duration:
            break
    return hours

def rain_level(f):
    """Clasifica la lluvia según umbral dinámico"""
    cond = f.get("condition", "")
    precip = f.get("precipitation", 0) or 0
    if cond not in rain_conditions or precip < THRESHOLDS["precipitation"]:
        return None
    if precip < THRESHOLDS["precipitation"]*2:
        return "🌧️ lluvia moderada"
    else:
        return "⛈️ lluvia fuerte"

def wind_info(f):
    """Devuelve información de viento solo si supera el threshold"""
    ws = f.get("wind_speed", 0) or 0
    wb = f.get("wind_bearing", 0) or 0
    if ws >= THRESHOLDS["wind_speed"]:
        return f"💨 {ws} km/h, {wb:.0f}°"
    return ""

def temp_alert(f):
    """Devuelve alerta de temperatura según thresholds"""
    temp = f.get("temperature")
    if temp is None:
        return None
    if temp <= THRESHOLDS["temperature_low"]:
        return f"🥶 {temp}°C"
    elif temp >= THRESHOLDS["temperature_high"]:
        return f"🥵 {temp}°C"
    return None

def hum_alert(f):
    """Devuelve alerta de humedad según thresholds"""
    hum = f.get("humidity")
    if hum is not None and hum >= THRESHOLDS["humidity_high"]:
        return f"💦 {hum}%"
    return None

# ---- Selección de forecast para ida y vuelta ----
ida = next_hours(home_forecast, departure_hour, trip_duration // 2)
vuelta = next_hours(work_forecast, departure_hour + trip_duration // 2, trip_duration // 2)

# ---- Comprobar si hay alerta en el trayecto ----
alertas = []
for f in ida + vuelta:
    extras = []
    for fn in [rain_level, wind_info, temp_alert, hum_alert]:
        val = fn(f)
        if val:
            extras.append(val)
    if extras:
        alertas.append(f"{f.get('datetime')[11:16]}: " + ", ".join(extras))

# ---- Construir mensaje ----
msg = ""
if alertas:
    msg += "⚠️ Atención: Condiciones significativas durante el trayecto:\n"
    msg += "\n".join(f"- {a}" for a in alertas)
else:
    msg += "☀️ Buenas noticias: No se esperan condiciones significativas durante el trayecto.\n"

msg += f"\nHora de aviso: {current_hour:02d}:00, Temp exterior: {temp_exterior}°C, Hum. exterior: {hum_exterior}%\n"

# ---- Detalle ida ----
msg += "\n🔹 Pronóstico ida (casa->trabajo):\n"
for f in ida:
    extras = [v for v in [rain_level(f), wind_info(f), temp_alert(f), hum_alert(f)] if v]
    msg += (
        f"- {f.get('datetime')[11:16]}: {f.get('condition')}, "
        f"T: {f.get('temperature')}°C, H: {f.get('humidity')}%, "
        f"P: {f.get('precipitation')} mm"
        + (", " + ", ".join(extras) if extras else "") + "\n"
    )

# ---- Detalle vuelta ----
msg += "\n🔹 Pronóstico vuelta (trabajo->casa):\n"
for f in vuelta:
    extras = [v for v in [rain_level(f), wind_info(f), temp_alert(f), hum_alert(f)] if v]
    msg += (
        f"- {f.get('datetime')[11:16]}: {f.get('condition')}, "
        f"T: {f.get('temperature')}°C, H: {f.get('humidity')}%, "
        f"P: {f.get('precipitation')} mm"
        + (", " + ", ".join(extras) if extras else "") + "\n"
    )

# ---- Enviar mensaje a Telegram ----
hass.services.call("script", "notifica_telegram", {"message": msg})
