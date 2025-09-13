# forecast_process.py
# Procesa el forecast horario y crea sensores dinámicos en Home Assistant con unique_id.
# Ahora también crea sensores horarios de viento (speed y bearing) y precipitación para WindRoseCard y gráficos.
# version 1.0 - 2025/09/13

forecast = data.get("forecast", [])
location = data.get("location", "home")  # permite distinguir forecast_home o forecast_work

def state_attributes(attrs, unique_id):
    """Añade unique_id a los atributos"""
    attrs = attrs.copy()
    attrs["unique_id"] = unique_id
    return attrs



if not forecast:
    logger.warning(f"[{location}] No se recibió forecast")
else:
    logger.info(f"[{location}] Forecast recibido con {len(forecast)} entradas")

    # Subconjuntos
    next1  = forecast[:1]
    next6  = forecast[:6]
    next12 = forecast[:12]
    next24 = forecast[:24]

    # ---- 0b. Sensores actuales (bloque current del weather entity) ----
    weather_entity = hass.states.get(f"weather.forecast_{location}")
    if weather_entity:
        attrs = weather_entity.attributes

        current_map = {
            "temperature": ("°C", "temperature"),
            "dew_point": ("°C", "temperature"),
            "humidity": ("%", "humidity"),
            "pressure": ("hPa", "pressure"),
            "wind_speed": ("km/h", "wind_speed"),
            "wind_bearing": ("°", "wind_direction"),
            "cloud_coverage": ("%", None),
            "uv_index": (None, None),
            "visibility": ("km", None),
        }

        for key, (unit, device_class) in current_map.items():
            if key in attrs:
                hass.states.set(
                    f"sensor.weather_{location}_{key}",
                    attrs.get(key),
                    state_attributes({
                        "unit_of_measurement": unit,
                        "device_class": device_class,
                        "source": f"weather.forecast_{location}",
                    }, f"multi_forecast_{location}_{key}")
                )


    # ---- 0. Sensores horarios de viento y precipitación ----
    for i, f in enumerate(next12, start=1):
        # viento: usa wind_gust_speed si existe, si no wind_speed
        wind_value = f.get("wind_gust_speed")
        if wind_value is None:
            wind_value = f.get("wind_speed")
        hass.states.set(
            f"sensor.multi_forecast_{location}_wind_speed_{i}h",
            wind_value,
            state_attributes({
                "datetime": f.get("datetime"),
                "unit_of_measurement": "km/h",
                "device_class": "wind_speed",
            }, f"multi_forecast_{location}_wind_speed_{i}h")
        )
        hass.states.set(
            f"sensor.multi_forecast_{location}_wind_bearing_{i}h",
            f.get("wind_bearing"),
            state_attributes({
                "datetime": f.get("datetime"),
                "unit_of_measurement": "°",
                "device_class": "wind_direction",
            }, f"multi_forecast_{location}_wind_bearing_{i}h")
        )
        # precipitación
        hass.states.set(
            f"sensor.multi_forecast_{location}_precipitation_{i}h",
            f.get("precipitation"),
            state_attributes({
                "datetime": f.get("datetime"),
                "unit_of_measurement": "mm",
                "device_class": "precipitation",
            }, f"multi_forecast_{location}_precipitation_{i}h")
        )
        # probabilidad de precipitación (solo si existe)
        precipitation_probability = f.get("precipitation_probability")
        if precipitation_probability is not None:
            hass.states.set(
                f"sensor.multi_forecast_{location}_precipitation_probability_{i}h",
                precipitation_probability,
                state_attributes({
                    "datetime": f.get("datetime"),
                    "unit_of_measurement": "%",
                    "device_class": "probability",
                }, f"multi_forecast_{location}_precipitation_probability_{i}h")
            )

    # ---- 1. Próxima hora ----
    if next1:
        f = next1[0]
        hass.states.set(
            f"sensor.multi_forecast_{location}_next_hour_temperature",
            f.get("temperature"),
            state_attributes({
                "condition": f.get("condition"),
                "datetime": f.get("datetime"),
                "unit_of_measurement": "°C",
                "device_class": "temperature",
            }, f"multi_forecast_{location}_next_hour_temperature")
        )
        hass.states.set(
            f"sensor.multi_forecast_{location}_next_hour_humidity",
            f.get("humidity"),
            state_attributes({
                "condition": f.get("condition"),
                "datetime": f.get("datetime"),
                "unit_of_measurement": "%",
                "device_class": "humidity",
            }, f"multi_forecast_{location}_next_hour_humidity")
        )

    # ---- 2. Temperaturas máximas y mínimas ----
    def max_temp(entries):
        temps = [f.get("temperature") for f in entries if f.get("temperature") is not None]
        return max(temps) if temps else None

    def min_temp(entries):
        temps = [f.get("temperature") for f in entries if f.get("temperature") is not None]
        return min(temps) if temps else None

    for subset, hours in [(next12, 12), (next24, 24)]:
        hass.states.set(
            f"sensor.multi_forecast_{location}_max_temp_{hours}h",
            max_temp(subset),
            state_attributes({
                "hours_analyzed": hours,
                "unit_of_measurement": "°C",
                "device_class": "temperature",
            }, f"multi_forecast_{location}_max_temp_{hours}h")
        )
        hass.states.set(
            f"sensor.multi_forecast_{location}_min_temp_{hours}h",
            min_temp(subset),
            state_attributes({
                "hours_analyzed": hours,
                "unit_of_measurement": "°C",
                "device_class": "temperature",
            }, f"multi_forecast_{location}_min_temp_{hours}h")
        )

    # ---- 3. Humedad máxima y mínima ----
    def max_hum(entries):
        hums = [f.get("humidity") for f in entries if f.get("humidity") is not None]
        return max(hums) if hums else None

    def min_hum(entries):
        hums = [f.get("humidity") for f in entries if f.get("humidity") is not None]
        return min(hums) if hums else None

    for subset, hours in [(next12, 12), (next24, 24)]:
        hass.states.set(
            f"sensor.multi_forecast_{location}_max_humidity_{hours}h",
            max_hum(subset),
            state_attributes({
                "hours_analyzed": hours,
                "unit_of_measurement": "%",
                "device_class": "humidity",
            }, f"multi_forecast_{location}_max_humidity_{hours}h")
        )
        hass.states.set(
            f"sensor.multi_forecast_{location}_min_humidity_{hours}h",
            min_hum(subset),
            state_attributes({
                "hours_analyzed": hours,
                "unit_of_measurement": "%",
                "device_class": "humidity",
            }, f"multi_forecast_{location}_min_humidity_{hours}h")
        )

    # ---- 4. Lluvia prevista ----
    rain_conditions = ['rainy','pouring','hail','lightning','lightning-rainy','snowy-rainy']

    def rain_check(entries, hours):
        matches = [f for f in entries if f.get("condition") in rain_conditions]
        lluvia = "yes" if matches else "no"
        hass.states.set(
            f"sensor.multi_forecast_{location}_rain_next_{hours}h",
            lluvia,
            state_attributes({
                "matches": len(matches),
                "hours_analyzed": hours,
            }, f"multi_forecast_{location}_rain_next_{hours}h")
        )

    rain_check(next12, 12)
    rain_check(next24, 24)

    # ---- 5. Condición dominante próximas 6h ----
    conds = [f.get("condition") for f in next6 if f.get("condition")]
    if conds:
        counts = {}
        for c in conds:
            counts[c] = counts.get(c, 0) + 1
        dominant = max(counts, key=counts.get)
    else:
        dominant = "unknown"

    hass.states.set(
        f"sensor.multi_forecast_{location}_dominant_condition_6h",
        dominant,
        state_attributes({
            "hours_analyzed": 6,
        }, f"multi_forecast_{location}_dominant_condition_6h")
    )


 # ---- 6. Enviar forecast a forecast_alert.py por si hay condiciones críticas ----
    if location == "home":
        if hass.states.get('input_boolean.forecast_alert_active').state != 'on':
            hass.services.call(
                "python_script",
                "forecast_alert",
                {"forecast": forecast}
            )


    logger.info(f"[{location}] Forecast procesado y sensores creados con unique_id, viento y precipitación")
