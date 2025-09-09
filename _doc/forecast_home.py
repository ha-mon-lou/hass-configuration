import appdaemon.plugins.hass.hassapi as hass

class ForecastHome(hass.Hass):

    def initialize(self):
        # Primera ejecución 5s después de iniciar AppDaemon
        self.run_in(self.update_forecast, 5)

        # Repetir cada 30 minutos
        self.run_every(self.update_forecast, "now", 30 * 60)

        # Servicio manual para forzar actualización desde HA
        self.register_service("forecast_home/run_now", self.update_forecast)

    def update_forecast(self, kwargs):
        entity_id = "weather.forecast_home_2"

        # Leer directamente el atributo forecast
        forecast = self.get_state(entity_id, attribute="forecast")

        if not forecast:
            self.log("⚠️ forecast vacío o no existe")
            return

        self.log(f"✅ Forecast recibido: {len(forecast)} días")

        # Crear sensores para los primeros 7 días
        for i, day in enumerate(forecast[:7]):
            idx = i + 1
            attrs = {
                "datetime": day.get("datetime"),
                "condition": day.get("condition"),
                "temperature": day.get("temperature"),
                "templow": day.get("templow"),
                "precipitation": day.get("precipitation"),
                "wind_speed": day.get("wind_speed"),
                "humidity": day.get("humidity"),
            }

            # Temperatura máxima
            self.set_state(
                f"sensor.fc{idx}_temp",
                state=day.get("temperature", "unknown"),
                attributes={**attrs, "friendly_name": f"Temperatura máxima día {idx}", "unit_of_measurement": "°C"}
            )

            # Temperatura mínima
            self.set_state(
                f"sensor.fc{idx}_templow",
                state=day.get("templow", "unknown"),
                attributes={**attrs, "friendly_name": f"Temperatura mínima día {idx}", "unit_of_measurement": "°C"}
            )

            # Precipitación
            self.set_state(
                f"sensor.fc{idx}_precip",
                state=day.get("precipitation", 0),
                attributes={**attrs, "friendly_name": f"Precipitación día {idx}", "unit_of_measurement": "mm"}
            )

            # Condición
            self.set_state(
                f"sensor.fc{idx}_condition",
                state=day.get("condition", "unknown"),
                attributes={**attrs, "friendly_name": f"Condición día {idx}"}
            )
