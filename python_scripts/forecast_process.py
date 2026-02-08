# forecast_process.py
# Este script procesa el forecast horario y genera sensores personalizados.

forecast = data.get("forecast", [])

if not forecast:
    logger.warning("No se recibió forecast")
else:
    logger.warning("Si se recibió forecast")
    # ---- 1. Próxima hora ----
    first = forecast[0]
    temp = first.get("temperature")
    cond = first.get("condition")
    hass.states.set(
        "sensor.forecast_home_next_hour",
        temp,
        {"condition": cond, "datetime": first.get("datetime")}
    )

    next6  = forecast[:6]
    next12 = forecast[:12]
    next24 = forecast[:24]
    # ---- 2.1 Temperatura máxima próximas 12h ----
    max_temp12 = max([f.get("temperature") for f in next12 if f.get("temperature") is not None], default=None)
    hass.states.set(
        "sensor.forecast_home_max_temp_12h",
        max_temp12,
        {"hours_analyzed": 12}
    )
    # ---- 2.2 Temperatura máxima próximas 24h ----
    max_temp24 = max([f.get("temperature") for f in next24 if f.get("temperature") is not None], default=None)
    hass.states.set(
        "sensor.forecast_home_max_temp_24h",
        max_temp24,
        {"hours_analyzed": 24}
    )


    rain_conditions = ['rainy','pouring','hail','lightning','lightning-rainy','snowy-rainy']
    # ---- 3.1 Lluvia prevista próximas 12h ----
    rain_fc12 = [f for f in next12 if f.get("condition") in rain_conditions]
    lluvia = "yes" if rain_fc12 else "no"
    hass.states.set(
        "sensor.forecast_home_rain_next_12h",
        lluvia,
        {"matches": len(rain_fc12)}
    )
    # ---- 3.2 Lluvia prevista próximas 24h ----
    rain_fc24 = [f for f in next24 if f.get("condition") in rain_conditions]
    lluvia = "yes" if rain_fc24 else "no"
    hass.states.set(
        "sensor.forecast_home_rain_next_24h",
        lluvia,
        {"matches": len(rain_fc24)}
    )

    # ---- 4. Condición dominante próximas 6h ----
    conds = [f.get("condition") for f in next6 if f.get("condition")]
    if conds:
        from collections import Counter  # ⚠️ no permitido en python_scripts
        # → así que hacemos un conteo manual:
        counts = {}
        for c in conds:
            counts[c] = counts.get(c, 0) + 1
        dominant = max(counts, key=counts.get)
    else:
        dominant = "unknown"

    hass.states.set(
        "sensor.forecast_home_dominant_condition_6h",
        dominant,
        {"hours_analyzed": 6}
    )

    logger.info("Forecast procesado y sensores creados")
