"""Balboa entities."""
from __future__ import annotations

from datetime import timedelta

from pybalboa import EVENT_UPDATE, SpaClient, SpaControl

from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.helpers.entity import DeviceInfo, Entity

from .const import DOMAIN

TWO_MINUTES = timedelta(minutes=2)


class BalboaBaseEntity(Entity):
    """Balboa base entity."""

    def __init__(self, client: SpaClient, name: str | None = None) -> None:
        """Initialize the control."""
        mac = client.mac_address
        model = client.model

        self._attr_should_poll = False
        self._attr_unique_id = f"{mac}-{model}{'' if name is None else f'-{name}'}"
        self._attr_name = name
        self._attr_has_entity_name = True
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, mac)},
            name=model,
            manufacturer="Balboa Water Group",
            model=model,
            sw_version=client.software_version,
            connections={(CONNECTION_NETWORK_MAC, mac)},
        )
        self._client = client

    @property
    def assumed_state(self) -> bool:
        """Return whether the state is based on actual reading from device."""
        return not self._client.available


class BalboaEntity(BalboaBaseEntity):
    """Balboa entity."""

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        self.async_on_remove(self._client.on(EVENT_UPDATE, self.async_write_ha_state))


class BalboaControlEntity(BalboaBaseEntity):
    """Balboa spa control entity."""

    def __init__(self, control: SpaControl) -> None:
        """Initialize the control."""
        super().__init__(control.client, control.name)
        self._control = control

    @property
    def available(self) -> bool:
        """Return whether the entity is available or not."""
        return self._client.connected

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        self.async_on_remove(self._control.on(EVENT_UPDATE, self.async_write_ha_state))
