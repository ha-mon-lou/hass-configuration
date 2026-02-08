# meteocat_processor.py
# Procesa forecast horario de Meteocat y crea sensores en Home Assistant
# Version 1.1 - 2025/09/20

raw = data.get("raw", [])
location = data.get("location", "home")

def state_attributes(attrs, unique_id):
    attrs = attrs.copy()
    attrs["unique_id"] = unique_id
    return attrs

if not raw:
    logger.warning(f"[{location}] No se recibió forecast Meteocat")
else:
    logger.info(f"[{location}] Forecast Meteocat recibido")

    try:
        entry = raw[0]
        dies = entry.get("dies", [])
        if not dies:
            logger.warning(f"[{location}] No hay días en forecast Meteocat")
        else:
            dia = dies[0]
            variables = dia.get("variables", {})

            mapping = {
                "temp": ("temperature", "°C", "temperature"),
                "tempXafogor": ("apparent_temperature", "°C", "temperature"),
                "precipitacio": ("precipitation", "mm", "precipitation"),
                "estatCel": ("condition_code", None, None),
                "velVent": ("wind_speed", "km/h", "wind_speed"),
                "dirVent": ("wind_bearing", "°", "wind_direction"),
                "humitat": ("humidity", "%", "humidity"),
            }

            # ---- Mapeo estatCel Meteocat -> condition HA ----
            estatcel_map = {
                1: "sunny",            # Cel serè
                2: "sunny",            # Poc ennuvolat
                3: "partlycloudy",     # Mig ennuvolat
                4: "cloudy",           # Molt ennuvolat
                5: "cloudy",           # Cobert
                6: "rainy",            # Pluges febles
                7: "rainy",            # Pluges moderades
                8: "pouring",          # Pluges fortes
                9: "lightning-rainy",  # Tempesta feble
                10: "lightning-rainy", # Tempesta moderada
                11: "lightning-rainy", # Tempesta forta
                12: "snowy",           # Neu feble
                13: "snowy",           # Neu moderada
                14: "snowy",           # Neu forta
                15: "snowy-rainy",     # Aiguaneu
                16: "fog",             # Boira
                17: "hail",            # Calamarsa / pedra
                18: "exceptional",     # Fenòmens severs (tornada, vent molt fort, etc.)
                19: "clear-night",     # Cel serè (nit)
                20: "partlycloudy",    # Interval variable (nit)
                21: "cloudy",          # Molt ennuvolat (nit)
            }

            hours_map = [1, 6, 12, 24]

            # ---- Sensores horarios ----
            for key, (name, unit, device_class) in mapping.items():
                var = variables.get(key)
                if not var:
                    continue
                valores = var.get("valors") or var.get("valor")
                if not valores:
                    continue

                for i, v in enumerate(valores, start=1):
                    if i not in hours_map:
                        continue
                    valor = v.get("valor")
                    fecha = v.get("data")
                    if key == "estatCel":
                        cond = estatcel_map.get(int(valor), "unknown")
                        hass.states.set(
                            f"sensor.meteocat_{location}_condition_{i}h",
                            cond,
                            state_attributes({
                                "datetime": fecha,
                                "raw_code": valor,
                                "device_class": "condition",
                                "source": "meteocat_api"
                            }, f"meteocat_{location}_condition_{i}h")
                        )
                    else:
                        hass.states.set(
                            f"sensor.meteocat_{location}_{name}_{i}h",
                            valor,
                            state_attributes({
                                "datetime": fecha,
                                "unit_of_measurement": unit,
                                "device_class": device_class,
                                "source": "meteocat_api"
                            }, f"meteocat_{location}_{name}_{i}h")
                        )

            # ---- Máximos y mínimos ----
            def max_val(entries, key):
                vals = [float(v.get("valor")) for v in entries if v.get("valor") is not None]
                return max(vals) if vals else None

            def min_val(entries, key):
                vals = [float(v.get("valor")) for v in entries if v.get("valor") is not None]
                return min(vals) if vals else None

            intervals = [6, 12, 24, 48]
            for hours in intervals:
                # filtrar solo los primeros 'hours' registros
                temp_entries = [v for v in variables.get("temp", {}).get("valors", [])][:hours]
                hum_entries = [v for v in variables.get("humitat", {}).get("valors", [])][:hours]

                hass.states.set(
                    f"sensor.meteocat_{location}_max_temp_{hours}h",
                    max_val(temp_entries, "valor"),
                    state_attributes({
                        "hours_analyzed": hours,
                        "unit_of_measurement": "°C",
                        "device_class": "temperature",
                    }, f"meteocat_{location}_max_temp_{hours}h")
                )
                hass.states.set(
                    f"sensor.meteocat_{location}_min_temp_{hours}h",
                    min_val(temp_entries, "valor"),
                    state_attributes({
                        "hours_analyzed": hours,
                        "unit_of_measurement": "°C",
                        "device_class": "temperature",
                    }, f"meteocat_{location}_min_temp_{hours}h")
                )
                hass.states.set(
                    f"sensor.meteocat_{location}_max_humidity_{hours}h",
                    max_val(hum_entries, "valor"),
                    state_attributes({
                        "hours_analyzed": hours,
                        "unit_of_measurement": "%",
                        "device_class": "humidity",
                    }, f"meteocat_{location}_max_humidity_{hours}h")
                )
                hass.states.set(
                    f"sensor.meteocat_{location}_min_humidity_{hours}h",
                    min_val(hum_entries, "valor"),
                    state_attributes({
                        "hours_analyzed": hours,
                        "unit_of_measurement": "%",
                        "device_class": "humidity",
                    }, f"meteocat_{location}_min_humidity_{hours}h")
                )

            # ---- Condición dominante próximas 6h ----
            cond_entries = [v.get("valor") for v in variables.get("estatCel", {}).get("valors", [])][:6]
            conds = [estatcel_map.get(int(c), "unknown") for c in cond_entries if c is not None]
            if conds:
                counts = {}
                for c in conds:
                    counts[c] = counts.get(c, 0) + 1
                dominant = max(counts, key=counts.get)
            else:
                dominant = "unknown"

            hass.states.set(
                f"sensor.meteocat_{location}_dominant_condition_6h",
                dominant,
                state_attributes({
                    "hours_analyzed": 6,
                }, f"meteocat_{location}_dominant_condition_6h")
            )

            logger.info(f"[{location}] Sensores Meteocat creados con máximos/mínimos y condición dominante")
    except Exception as e:
        logger.error(f"[{location}] Error procesando Meteocat: {e}")
