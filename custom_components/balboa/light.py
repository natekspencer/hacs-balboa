"""Support for Balboa lights."""
from __future__ import annotations

from typing import Any

from pybalboa import SpaClient

from homeassistant.components.light import LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import BalboaControlEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the spa light devices."""
    spa: SpaClient = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(BalboaLightEntity(light) for light in spa.lights)


class BalboaLightEntity(BalboaControlEntity, LightEntity):
    """Representation of a Balboa light entity."""

    @property
    def is_on(self) -> bool:
        """Return True if entity is on."""
        return self._control.state > 0

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        await self._control.set_state(1)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        await self._control.set_state(0)
