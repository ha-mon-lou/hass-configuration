# forecast_process.py
# Procesa el forecast horario y crea sensores personalizados en Home Assistant.

forecast = data.get("forecast", [])

if not forecast:
    logger.warning("No se recibió forecast")
else:
    logger.warning("Si se recibió forecast")

    # Subconjuntos de datos
    next1  = forecast[:1]
    next6  = forecast[:6]
    next12 = forecast[:12]
    next24 = forecast[:24]

    # ---- 1. Próxima hora ----
    if next1:
        f = next1[0]
        hass.states.set(
            "sensor.forecast_home_next_hour",
            f.get("temperature"),
            {
                "condition": f.get("condition"),
                "datetime": f.get("datetime")
            }
        )

    # ---- 2. Temperaturas máximas y mínimas ----
    def max_temp(entries):
        temps = [f.get("temperature") for f in entries if f.get("temperature") is not None]
        return max(temps) if temps else None

    def min_temp(entries):
        temps = [f.get("temperature") for f in entries if f.get("temperature") is not None]
        return min(temps) if temps else None

    for subset, hours in [(next12, 12), (next24, 24)]:
        max_temp_val = max_temp(subset)
        min_temp_val = min_temp(subset)

        hass.states.set(
            f"sensor.forecast_home_max_temp_{hours}h",
            max_temp_val,
            {"hours_analyzed": hours}
        )

        hass.states.set(
            f"sensor.forecast_home_min_temp_{hours}h",
            min_temp_val,
            {"hours_analyzed": hours}
        )

    # ---- 3. Lluvia prevista ----
    rain_conditions = ['rainy', 'pouring', 'hail', 'lightning', 'lightning-rainy', 'snowy-rainy']

    def rain_check(entries, hours):
        matches = [f for f in entries if f.get("condition") in rain_conditions]
        lluvia = "yes" if matches else "no"
        hass.states.set(
            f"sensor.forecast_home_rain_next_{hours}h",
            lluvia,
            {"matches": len(matches)}
        )

    rain_check(next12, 12)
    rain_check(next24, 24)

    # ---- 4. Condición dominante próximas 6h ----
    conds = [f.get("condition") for f in next6 if f.get("condition")]
    if conds:
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
