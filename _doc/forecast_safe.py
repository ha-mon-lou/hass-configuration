import appdaemon.plugins.hass.hassapi as hass
import json

class ForecastSafe(hass.Hass):

    def initialize(self):
        self.run_every(self.update_forecast, "now", 30*60)
        # Servicio manual para forzar actualización desde HA
        self.register_service("forecast_safe/run_now", self.update_forecast)

    def update_forecast(self, kwargs):
        forecast_json = self.get_state("sensor.forecast_home_safe", attribute="forecast")
        if not forecast_json:
            self.log("⚠️ Forecast safe vacío o no existe")
            return
        try:
            forecast = json.loads(forecast_json)
        except Exception as e:
            self.log(f"❌ Error parseando JSON: {e}")
            return

        self.log(f"✅ Forecast recibido: {len(forecast)} días")
        # Aquí procesas forecast como quieras
