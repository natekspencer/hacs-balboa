"""Support for Balboa Spa Wifi adaptor."""
from __future__ import annotations

import math
from typing import Any

from pybalboa import SpaClient
from pybalboa.enums import HeatMode, HeatState, TemperatureUnit

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_TEMPERATURE,
    PRECISION_HALVES,
    PRECISION_WHOLE,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import BalboaEntity

CLIMATE_SUPPORTED_MODES = [HVACMode.HEAT, HVACMode.OFF]
HEAT_HVAC_MODE_MAP = {
    HeatMode.READY: HVACMode.HEAT,
    HeatMode.REST: HVACMode.OFF,
    HeatMode.READY_IN_REST: HVACMode.AUTO,
}
HVAC_HEAT_MODE_MAP = {value: key for key, value in HEAT_HVAC_MODE_MAP.items()}
HEAT_MODE_NAME_MAP = {
    HeatMode.READY: "Ready",
    HeatMode.REST: "Rest",
    HeatMode.READY_IN_REST: "Ready-in-Rest",
}
NAME_HEAT_MODE_MAP = {value: key for key, value in HEAT_MODE_NAME_MAP.items()}
HEAT_STATE_HVAC_ACTION_MAP = {
    HeatState.OFF: HVACAction.OFF,
    HeatState.HEATING: HVACAction.HEATING,
    HeatState.HEAT_WAITING: HVACAction.IDLE,
}
TEMPERATURE_UNIT_MAP = {
    TemperatureUnit.CELSIUS: UnitOfTemperature.CELSIUS,
    TemperatureUnit.FAHRENHEIT: UnitOfTemperature.FAHRENHEIT,
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the spa climate device."""
    spa: SpaClient = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([BalboaClimateEntity(spa)])


class BalboaClimateEntity(BalboaEntity, ClimateEntity):
    """Representation of a Balboa spa climate device."""

    _attr_icon = "mdi:hot-tub"
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE
    )

    @property
    def precision(self) -> float:
        """Return the precision of the system."""
        if self.hass.config.units.temperature_unit == UnitOfTemperature.CELSIUS:
            return PRECISION_HALVES
        return PRECISION_WHOLE

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement used by the platform."""
        return TEMPERATURE_UNIT_MAP[self._client.temperature_unit]

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self._client.temperature

    @property
    def target_temperature(self) -> float:
        """Return the target temperature we try to reach."""
        return self._client.target_temperature

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature supported by the spa."""
        return self._client.temperature_minimum

    @property
    def max_temp(self) -> float:
        """Return the minimum temperature supported by the spa."""
        return self._client.temperature_maximum

    @property
    def preset_modes(self) -> list[str]:
        """Return the valid preset modes."""
        return list(map(HEAT_MODE_NAME_MAP.get, self._client.heat_mode.options))

    @property
    def hvac_action(self) -> str:
        """Return the current operation mode."""
        return HEAT_STATE_HVAC_ACTION_MAP[self._client.heat_state]

    @property
    def hvac_modes(self) -> list[str]:
        """Return the list of supported HVAC modes."""
        return CLIMATE_SUPPORTED_MODES

    @property
    def hvac_mode(self) -> str:
        """Return the current HVAC mode."""
        return HEAT_HVAC_MODE_MAP.get(self._client.heat_mode.state)

    @property
    def preset_mode(self) -> str:
        """Return current preset mode."""
        return HEAT_MODE_NAME_MAP[self._client.heat_mode.state]

    def same_unit(self) -> bool:
        """Return True if the spa and HA temperature units are the same."""
        unit = TEMPERATURE_UNIT_MAP[self._client.temperature_unit]
        return unit == self.hass.config.units.temperature_unit

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set a new target temperature."""
        temperature = kwargs[ATTR_TEMPERATURE]
        if not self.same_unit():
            if self._client.temperature_unit == TemperatureUnit.CELSIUS:
                temperature = 0.5 * round(temperature / 0.5)
            else:
                temperature = math.floor(temperature + 0.5)
        await self._client.set_temperature(temperature)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        await self._client.heat_mode.set_state(NAME_HEAT_MODE_MAP[preset_mode])

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        await self._client.heat_mode.set_state(HVAC_HEAT_MODE_MAP[hvac_mode])
