from datetime import datetime
import logging
from typing import List

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    UnitOfTemperature
)
from homeassistant.core import HomeAssistant, callback

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.sensor import (
  RestoreSensor,
  SensorDeviceClass,
  SensorStateClass,
)

from .base import (BaseOctopusEnergyHeatPumpSensor)
from ..utils.attributes import dict_to_typed_dict
from ..api_client.heat_pump import HeatPump
from ..coordinators.heat_pump_configuration_and_status import HeatPumpCoordinatorResult

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyHeatPumpSensorLiveOutdoorTemperature(CoordinatorEntity, BaseOctopusEnergyHeatPumpSensor, RestoreSensor):
  """Sensor for displaying the live heat output of a heat pump."""

  def __init__(self, hass: HomeAssistant, coordinator, heat_pump_id: str, heat_pump: HeatPump):
    """Init sensor."""
    # Pass coordinator to base class
    CoordinatorEntity.__init__(self, coordinator)
    BaseOctopusEnergyHeatPumpSensor.__init__(self, hass, heat_pump_id, heat_pump)

    self._state = None
    self._last_updated = None

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_heat_pump_{self._heat_pump_id}_live_outdoor_temperature"

  @property
  def name(self):
    """Name of the sensor."""
    return f"Live Outdoor Temperature Heat Pump ({self._heat_pump_id})"

  @property
  def state_class(self):
    """The state class of sensor"""
    return SensorStateClass.MEASUREMENT

  @property
  def device_class(self):
    """The type of sensor"""
    return SensorDeviceClass.TEMPERATURE

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:thermometer"

  @property
  def native_unit_of_measurement(self):
    """Unit of measurement of the sensor."""
    return UnitOfTemperature.CELSIUS

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes
  
  @property
  def native_value(self):
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """Retrieve the live heat output for the heat pump."""
    current = now()
    result: HeatPumpCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    
    if (result is not None 
        and result.data is not None 
        and result.data.octoHeatPumpLivePerformance is not None
        and result.data.octoHeatPumpLivePerformance.outdoorTemperature is not None):
      _LOGGER.debug(f"Updating OctopusEnergyHeatPumpSensorLiveOutdoorTemperature for '{self._heat_pump_id}'")

      self._state = float(result.data.octoHeatPumpLivePerformance.outdoorTemperature.value)
      self._attributes["read_at"] = datetime.fromisoformat(result.data.octoHeatPumpLivePerformance.readAt)
      self._last_updated = current

    self._attributes = dict_to_typed_dict(self._attributes)
    super()._handle_coordinator_update()

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    last_sensor_state = await self.async_get_last_sensor_data()
    
    if state is not None and last_sensor_state is not None and self._state is None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else last_sensor_state.native_value
      self._attributes = dict_to_typed_dict(state.attributes, [])
    
      _LOGGER.debug(f'Restored OctopusEnergyHeatPumpSensorLiveOutdoorTemperature state: {self._state}')