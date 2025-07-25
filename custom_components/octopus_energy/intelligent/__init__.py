import logging
from datetime import (datetime, timedelta, time)
import re

from homeassistant.util.dt import (utcnow, parse_datetime)

from ..utils import get_active_tariff

from ..const import CONFIG_MAIN_INTELLIGENT_RATE_MODE_STARTED_DISPATCHES_ONLY, CONFIG_MAIN_INTELLIGENT_RATE_MODE_PENDING_AND_STARTED_DISPATCHES, INTELLIGENT_SOURCE_BUMP_CHARGE_OPTIONS, INTELLIGENT_SOURCE_SMART_CHARGE_OPTIONS, REFRESH_RATE_IN_MINUTES_INTELLIGENT

from ..api_client.intelligent_settings import IntelligentSettings
from ..api_client.intelligent_dispatches import IntelligentDispatchItem, IntelligentDispatches, SimpleIntelligentDispatchItem
from ..api_client.intelligent_device import IntelligentDevice

mock_intelligent_data_key = "MOCK_INTELLIGENT_DATA"

_LOGGER = logging.getLogger(__name__)

def mock_intelligent_dispatches() -> IntelligentDispatches:
  planned: list[IntelligentDispatchItem] = []
  completed: list[IntelligentDispatchItem] = []
  current_state = "SMART_CONTROL_CAPABLE"

  dispatches = [
    IntelligentDispatchItem(
      utcnow().replace(hour=19, minute=0, second=0, microsecond=0),
      utcnow().replace(hour=20, minute=0, second=0, microsecond=0),
      1,
      INTELLIGENT_SOURCE_SMART_CHARGE_OPTIONS[0],
      "home"
    ),
    IntelligentDispatchItem(
      utcnow().replace(hour=7, minute=0, second=0, microsecond=0),
      utcnow().replace(hour=8, minute=0, second=0, microsecond=0),
      4.6,
      None,
      "home"
    ),

    IntelligentDispatchItem(
      utcnow().replace(hour=12, minute=0, second=0, microsecond=0),
      utcnow().replace(hour=13, minute=0, second=0, microsecond=0),
      4.6,
      INTELLIGENT_SOURCE_BUMP_CHARGE_OPTIONS[-1].upper(),
      "home"
    )
  ]

  # Simulate a pending dispatch being removed just before it begins
  if (utcnow() <= utcnow().replace(hour=11, minute=0, second=0, microsecond=0) - timedelta(minutes=REFRESH_RATE_IN_MINUTES_INTELLIGENT)):
    dispatches.append(
      IntelligentDispatchItem(
        utcnow().replace(hour=11, minute=0, second=0, microsecond=0),
        utcnow().replace(hour=11, minute=20, second=0, microsecond=0),
        1.2,
        INTELLIGENT_SOURCE_SMART_CHARGE_OPTIONS[0].upper(),
        "home"
      )
    ) 

  # Simulate a dispatch coming in late
  if (utcnow() >= utcnow().replace(hour=10, minute=10, second=0, microsecond=0) - timedelta(minutes=REFRESH_RATE_IN_MINUTES_INTELLIGENT)):
    dispatches.append(
      IntelligentDispatchItem(
        utcnow().replace(hour=10, minute=10, second=0, microsecond=0),
        utcnow().replace(hour=10, minute=30, second=0, microsecond=0),
        1.2,
        INTELLIGENT_SOURCE_SMART_CHARGE_OPTIONS[-1].upper(),
        "home"
      )
    )

  if (utcnow() >= utcnow().replace(hour=18, minute=0, second=0, microsecond=0) - timedelta(minutes=REFRESH_RATE_IN_MINUTES_INTELLIGENT)):
    dispatches.append(
      IntelligentDispatchItem(
        utcnow().replace(hour=18, minute=0, second=0, microsecond=0),
        utcnow().replace(hour=18, minute=20, second=0, microsecond=0),
        1.2,
        INTELLIGENT_SOURCE_SMART_CHARGE_OPTIONS[0].upper(),
        "home"
      )
    )

  for dispatch in dispatches:
    if utcnow() >= dispatch.start and utcnow() <= dispatch.end:
      if (dispatch.source.lower() in INTELLIGENT_SOURCE_SMART_CHARGE_OPTIONS if dispatch.source is not None else False):
        current_state = "SMART_CONTROL_IN_PROGRESS"
      elif (dispatch.source.lower() in INTELLIGENT_SOURCE_BUMP_CHARGE_OPTIONS if dispatch.source is not None else False):
        current_state = "BOOSTING"
      else:
        # If there is one without a source, then don't push it to completed dispatch to simulate
        # a planned dispatch not turning into a completed dispatch
        continue

    if (dispatch.end > utcnow()):
      planned.append(dispatch)
    else:
      dispatch.source = None
      completed.append(dispatch)

  return IntelligentDispatches(current_state, planned, completed)

def mock_intelligent_settings():
  return IntelligentSettings(
    True,
    90,
    80,
    time(7,20),
    time(9,10),
  )

def mock_intelligent_device():
  return IntelligentDevice(
    "1",
    "MYENERGI",
    "Myenergi",
    "Zappi smart EV",
    None,
    6.5,
    True
  )

def is_intelligent_product(product_code: str):
  # Need to ignore Octopus Intelligent Go tariffs
  return product_code is not None and (
    "INTELLI-BB-VAR" in product_code.upper() or
    "INTELLI-VAR" in product_code.upper() or
    "INTELLI-FIX" in product_code.upper() or
    re.search("INTELLI-[0-9]", product_code.upper()) is not None
  )

def has_intelligent_tariff(current: datetime, account_info):
  if account_info is not None and len(account_info["electricity_meter_points"]) > 0:
    for point in account_info["electricity_meter_points"]:
      tariff = get_active_tariff(current, point["agreements"])
      if tariff is not None and is_intelligent_product(tariff.product):
        return True

  return False

def __get_dispatch(rate, dispatches: list[IntelligentDispatchItem], expected_sources: list[str]):
  if dispatches is not None:
    for dispatch in dispatches:
      # Source as none counts as smart charge - https://forum.octopus.energy/t/pending-and-completed-octopus-intelligent-dispatches/8510/102
      if ((expected_sources is None or dispatch.source is None or (dispatch.source.lower() in expected_sources if dispatch.source is not None else False)) and 
          ((dispatch.start <= rate["start"] and dispatch.end >= rate["end"]) or # Rate is within dispatch
           (dispatch.start >= rate["start"] and dispatch.start < rate["end"]) or # dispatch starts within rate
           (dispatch.end > rate["start"] and dispatch.end <= rate["end"]) # dispatch ends within rate
          )
        ):
        return dispatch
    
  return None

def adjust_intelligent_rates(rates,
                             planned_dispatches: list[IntelligentDispatchItem],
                             started_dispatches: list[SimpleIntelligentDispatchItem],
                             mode: str):
  off_peak_rate = min(rates, key = lambda x: x["value_inc_vat"])
  adjusted_rates = []

  for rate in rates:
    if rate["value_inc_vat"] == off_peak_rate["value_inc_vat"]:
      adjusted_rates.append(rate)
      continue

    is_planned_dispatch = __get_dispatch(rate, planned_dispatches, INTELLIGENT_SOURCE_SMART_CHARGE_OPTIONS) is not None
    is_started_dispatch = __get_dispatch(rate, started_dispatches, None) is not None

    if ((mode == CONFIG_MAIN_INTELLIGENT_RATE_MODE_PENDING_AND_STARTED_DISPATCHES and (is_planned_dispatch or is_started_dispatch)) or
        (mode == CONFIG_MAIN_INTELLIGENT_RATE_MODE_STARTED_DISPATCHES_ONLY and is_started_dispatch)):
      adjusted_rates.append({
        "start": rate["start"],
        "end": rate["end"],
        "tariff_code": rate["tariff_code"],
        "value_inc_vat": off_peak_rate["value_inc_vat"],
        "is_capped": rate["is_capped"] if "is_capped" in rate else False,
        "is_intelligent_adjusted": True
      })
    else:
      adjusted_rates.append(rate)
    
  return adjusted_rates

def is_in_bump_charge(current_date: datetime, dispatches: list[IntelligentDispatchItem]) -> bool:
  for dispatch in dispatches:
    if (dispatch.start <= current_date and dispatch.end >= current_date):
      return (dispatch.source.lower() in INTELLIGENT_SOURCE_BUMP_CHARGE_OPTIONS if dispatch.source is not None else False)
  
  return False

def clean_previous_dispatches(time: datetime, dispatches: list[IntelligentDispatchItem]) -> list[IntelligentDispatchItem]:
  min_time = (time - timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)

  new_dispatches = {}
  for dispatch in dispatches:
    if (dispatch.start >= min_time):
      new_dispatches[(dispatch.start, dispatch.end)] = dispatch

  return list(new_dispatches.values())

def dictionary_list_to_dispatches(dispatches: list):
  items = []
  if (dispatches is not None):
    for dispatch in dispatches:
      items.append(
        IntelligentDispatchItem(
          parse_datetime(dispatch["start"]),
          parse_datetime(dispatch["end"]),
          float(dispatch["charge_in_kwh"]) if "charge_in_kwh" in dispatch and dispatch["charge_in_kwh"] is not None else None,
          dispatch["source"] if "source" in dispatch else "",
          dispatch["location"] if "location" in dispatch else ""
        )
      )

  return items

def dispatches_to_dictionary_list(dispatches: list[IntelligentDispatchItem], ignore_none: bool):
  items = []
  if (dispatches is not None):
    for dispatch in dispatches:
      items.append(dispatch.to_dict(ignore_none))

  return items

def simple_dispatches_to_dictionary_list(dispatches: list[SimpleIntelligentDispatchItem]):
  items = []
  if (dispatches is not None):
    for dispatch in dispatches:
      items.append(dispatch.to_dict())

  return items

class IntelligentFeatures:
  def __init__(self,
               is_default_features: bool,
               bump_charge_supported: bool,
               charge_limit_supported: bool,
               planned_dispatches_supported: bool,
               ready_time_supported: bool,
               smart_charge_supported: bool,
               current_state_supported: bool):
    self.is_default_features = is_default_features
    self.bump_charge_supported = bump_charge_supported
    self.charge_limit_supported = charge_limit_supported
    self.planned_dispatches_supported = planned_dispatches_supported
    self.ready_time_supported = ready_time_supported
    self.smart_charge_supported = smart_charge_supported
    self.current_state_supported = current_state_supported

FULLY_SUPPORTED_INTELLIGENT_PROVIDERS = [
  "DAIKIN",
  "ECOBEE",
  "ENERGIZER",
  "ENPHASE",
  "ENODE",
  "FORD",
  "GIVENERGY",
  "HUAWEI",
  "JEDLIX",
  "JEDLIX-V2",
  "MYENERGI",
  "OCPP_WALLBOX",
  "SENSI",
  "SMARTCAR",
  "TESLA",
  "SMART_PEAR",
  "HYPERVOLT",
  "INDRA"
]

def get_intelligent_features(provider: str) -> IntelligentFeatures:
  normalised_provider = provider.upper() if provider is not None else None
  if normalised_provider == "OHME":
    return IntelligentFeatures(False, False, False, False, False, False, False)
  
  if normalised_provider is not None:
    for provider in FULLY_SUPPORTED_INTELLIGENT_PROVIDERS:
      if normalised_provider == provider or re.search(f"{provider}_V[0-9]+", normalised_provider) is not None:
        return IntelligentFeatures(False, True, True, True, True, True, True)

  return IntelligentFeatures(True, False, False, False, False, False, False)