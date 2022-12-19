"""Support for Balboa Spa switches."""
from __future__ import annotations

from typing import Any

from pybalboa import SpaClient

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import BalboaControlEntity, BalboaEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up the spa switch devices."""
    spa: SpaClient = hass.data[DOMAIN][entry.entry_id]
    entities=[BalboaFilterSwitchEntity(spa,"Filter cycle 2 enabled")]
    entities.extend(BalboaSwitchEntity(control) for control in (*spa.aux, *spa.misters))
    async_add_entities(entities)


class BalboaSwitchEntity(BalboaControlEntity, SwitchEntity):
    """Representation of a Balboa switch entity."""

    _attr_device_class = SwitchDeviceClass.SWITCH

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


class BalboaFilterSwitchEntity(BalboaEntity, SwitchEntity):
    """Representation of a Balboa filter switch entity."""

    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_entity_category = EntityCategory.CONFIG

    @property
    def is_on(self) -> bool:
        """Return True if entity is on."""
        return self._client.filter_cycle_2_enabled

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        await self._client.set_filter_cycle(filter_cycle_2_enabled=True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        await self._client.set_filter_cycle(filter_cycle_2_enabled=False)
