"""Support for Balboa lights."""
from __future__ import annotations

from pybalboa import SpaClient, SpaControl

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import BalboaControlEntity

TEMP_RANGE_MAP = {
    "LOW": {"value": 0, "icon": "mdi:thermometer-minus"},
    "HIGH": {"value": 1, "icon": "mdi:thermometer-plus"},
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up the spa select devices."""
    spa: SpaClient = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([BalboaSelectEntity(spa.temperature_range)])


class BalboaSelectEntity(BalboaControlEntity, SelectEntity):
    """Representation of a Balboa select entity."""

    def __init__(self, control: SpaControl) -> None:
        """Initialize the select control."""
        super().__init__(control)
        self._attr_options = [option.name for option in control.options]
        self._attr_entity_category = EntityCategory.CONFIG

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return TEMP_RANGE_MAP[self.current_option]["icon"]

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        return self._control.state.name

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self._control.set_state(TEMP_RANGE_MAP[option]["value"])
