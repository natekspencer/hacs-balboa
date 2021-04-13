"""Support for Balboa Spa Pumps."""
from __future__ import annotations

import math
from typing import Any, Callable, List, Optional

from homeassistant.components.fan import SUPPORT_SET_SPEED, FanEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.util.percentage import (
    int_states_in_range,
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)
from pybalboa import BalboaSpaWifi

from . import BalboaEntity
from .const import _LOGGER, DOMAIN, PUMP, SPA


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Callable[[List[Entity], bool], None],
) -> None:
    """Set up the spa's pumps as FAN entities."""
    spa: BalboaSpaWifi = hass.data[DOMAIN][entry.entry_id][SPA]
    entities = []

    for key, value in enumerate(spa.pump_array, 1):
        if value:
            entities.append(BalboaSpaPump(spa, entry, key, value))

    if entities:
        async_add_entities(entities, True)


class BalboaSpaPump(BalboaEntity, FanEntity):
    """Representation of a Balboa Spa pump device."""

    def __init__(
        self, client: BalboaSpaWifi, entry: ConfigEntry, key: str, states: int
    ) -> None:
        """Initialize the pump."""
        super().__init__(client, entry, PUMP, key)
        self._supported_features = SUPPORT_SET_SPEED if states > 1 else 0
        self._speed_range = (1, states)

    async def async_set_percentage(self, percentage: Optional[int]) -> None:
        """Set the speed percentage of the pump."""
        if percentage is None:
            setto = self._speed_range[0]
        else:
            setto = math.ceil(percentage_to_ranged_value(self._speed_range, percentage))
        await self._client.change_pump(self._num - 1, setto)

    async def async_turn_on(
        self,
        speed: Optional[str] = None,
        percentage: Optional[int] = None,
        preset_mode: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the pump."""
        await self.async_set_percentage(percentage)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the pump."""
        await self.async_set_percentage(0)

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return self._supported_features

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the pump supports."""
        return int_states_in_range(self._speed_range)

    @property
    def percentage(self) -> Optional[int]:
        """Return the current speed percentage."""
        return ranged_value_to_percentage(
            self._speed_range, self._client.get_pump(self._num - 1)
        )

    @property
    def is_on(self) -> bool:
        """Return true if the pump is on."""
        return bool(self._client.get_pump(self._num - 1))

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend, if any."""
        return "mdi:hydro-power"
