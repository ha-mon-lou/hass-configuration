# forecast_trip.py
# Script Python para resumir el forecast del trayecto casa->trabajo y vuelta
# Sin usar offset manual, ajustando automáticamente según hora local

home_forecast = data.get("forecast_home", [])
work_forecast = data.get("forecast_work", [])
departure_hour = int(data.get("departure_hour", 8))
trip_duration = int(data.get("trip_duration", 6))
current_hour_str = data.get("current_hour", "0:00")
current_hour = int(current_hour_str.split(":")[0])
temp_exterior = data.get("temperature", "??")
hum_exterior = data.get("humidity", "??")

rain_conditions = ['rainy','pouring','hail','lightning','lightning-rainy','snowy-rainy']

def next_hours(forecast, start_hour, duration):
    """Devuelve los próximos `duration` elementos a partir de la hora >= start_hour"""
    hours = []
    for f in forecast:
        # extraer hora local de datetime
        dt_hour = int(f.get("datetime")[11:13])
        if dt_hour >= start_hour:
            hours.append(f)
        if len(hours) >= duration:
            break
    return hours

# Selección de forecast para ida y vuelta
ida = next_hours(home_forecast, departure_hour, trip_duration//2)
vuelta = next_hours(work_forecast, departure_hour + trip_duration//2, trip_duration//2)

# Comprobar si hay lluvia
alerta_lluvia = any(f.get("condition") in rain_conditions for f in ida + vuelta)

# Construir mensaje
msg = ""
if alerta_lluvia:
    msg += "🌧️ Atención: Se espera lluvia durante el trayecto en moto.\nNo olvides el impermeable.\n"
else:
    msg += "☀️ Buenas noticias: No se espera lluvia durante el trayecto.\n"

msg += f"\nHora de aviso: {current_hour:02d}:00, Temp exterior: {temp_exterior}°C, Hum. exterior: {hum_exterior}%\n"

msg += "\n🔹 Pronóstico ida (casa->trabajo):\n"
for f in ida:
    msg += f"- {f.get('datetime')[11:16]}: {f.get('condition')}, T: {f.get('temperature')}°C, H: {f.get('humidity')}%\n"

msg += "\n🔹 Pronóstico vuelta (trabajo->casa):\n"
for f in vuelta:
    msg += f"- {f.get('datetime')[11:16]}: {f.get('condition')}, T: {f.get('temperature')}°C, H: {f.get('humidity')}%\n"

# Enviar mensaje a telegram
hass.services.call("script", "notifica_telegram", {"message": msg})
