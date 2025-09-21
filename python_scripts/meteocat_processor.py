# meteocat_processor.py
# Procesa forecast horario de Meteocat y crea sensores en Home Assistant
# Versión 1.1 - 2025/09/19

import datetime

raw = data.get("raw", [])
location = data.get("location", "meteocat")

def state_attributes(attrs, unique_id):
    """Añade unique_id a los atributos"""
    attrs = attrs.copy()
    attrs["unique_id"] = unique_id
    return attrs

if not raw:
    logger.warning(f"[{location}] No se recibió forecast Meteocat")
else:
    logger.info(f"[{location}] Forecast Meteocat recibido con {len(raw)} entradas")

    try:
        entry = raw[0]  # siempre es lista de municipios
        dies = entry.get("dies", [])
        if not dies:
            logger.warning(f"[{location}] No hay días en forecast Meteocat")
        else:
            for day_index, dia in enumerate(dies):
                date = dia.get("data")
                variables = dia.get("variables", {})

                # ---- Mapeo de variables ----
                mapping = {
                    "temp": ("temperature", "°C", "temperature"),
                    "tempXafogor": ("apparent_temperature", "°C", "temperature"),
                    "precipitacio": ("precipitation", "mm", "precipitation"),
                    "estatCel": ("condition_code", None, None),  # se mapea a condición HA
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


                # ---- Crear sensores por hora ----
                for key, (name, unit, device_class) in mapping.items():
                    var = variables.get(key)
                    if not var:
                        continue
                    valores = var.get("valors") or var.get("valor")
                    if not valores:
                        continue

                    for i, v in enumerate(valores, start=1):
                        valor_raw = v.get("valor")
                        fecha = v.get("data")
                        # Convertir a float si no es estatCel
                        if key != "estatCel":
                            try:
                                valor = float(valor_raw)
                            except:
                                valor = valor_raw
                        else:
                            # Mapear condición
                            valor = estatcel_map.get(int(valor_raw), "unknown")

                        hass.states.set(
                            f"sensor.meteocat_{location}_{name}_{i}h",
                            valor,
                            state_attributes({
                                "datetime": fecha,
                                "unit_of_measurement": unit,
                                "device_class": device_class if key != "estatCel" else "condition",
                                "raw_code": valor_raw if key == "estatCel" else None,
                                "source": "meteocat_api"
                            }, f"meteocat_{location}_{name}_{i}h")
                        )

                # ---- Sensores diarios resumidos ----
                def max_val(var_name):
                    vals = [float(v.get("valor")) for v in variables.get(var_name, {}).get("valors", []) if v.get("valor") is not None]
                    return max(vals) if vals else None

                def min_val(var_name):
                    vals = [float(v.get("valor")) for v in variables.get(var_name, {}).get("valors", []) if v.get("valor") is not None]
                    return min(vals) if vals else None

                # Temperatura
                hass.states.set(
                    f"sensor.meteocat_{location}_max_temperature_day{day_index+1}",
                    max_val("temp"),
                    state_attributes({"unit_of_measurement":"°C","device_class":"temperature"}, f"meteocat_{location}_max_temp_day{day_index+1}")
                )
                hass.states.set(
                    f"sensor.meteocat_{location}_min_temperature_day{day_index+1}",
                    min_val("temp"),
                    state_attributes({"unit_of_measurement":"°C","device_class":"temperature"}, f"meteocat_{location}_min_temp_day{day_index+1}")
                )

                # Humedad
                hass.states.set(
                    f"sensor.meteocat_{location}_max_humidity_day{day_index+1}",
                    max_val("humitat"),
                    state_attributes({"unit_of_measurement":"%","device_class":"humidity"}, f"meteocat_{location}_max_hum_day{day_index+1}")
                )
                hass.states.set(
                    f"sensor.meteocat_{location}_min_humidity_day{day_index+1}",
                    min_val("humitat"),
                    state_attributes({"unit_of_measurement":"%","device_class":"humidity"}, f"meteocat_{location}_min_hum_day{day_index+1}")
                )

            logger.info(f"[{location}] Sensores Meteocat creados por hora y resumen diario")
    except Exception as e:
        logger.error(f"[{location}] Error procesando Meteocat: {e}")
