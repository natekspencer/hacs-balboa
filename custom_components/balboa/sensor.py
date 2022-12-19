"""Support for Balboa spa sensors."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from pybalboa import SpaClient

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TIME_SECONDS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.util.dt import now

from .const import DOMAIN
from .entity import BalboaEntity

ONE_DAY = timedelta(days=1)


def get_start_datetime(start: time, duration: timedelta) -> datetime:
    """Get start datetime."""
    _dt = datetime.combine((_now := now()), start, _now.tzinfo)
    if _dt + duration < _now:
        return _dt + ONE_DAY
    if _dt + duration - _now > ONE_DAY:
        return _dt - ONE_DAY
    return _dt


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the spa's  sensors."""
    spa: SpaClient = hass.data[DOMAIN][entry.entry_id]
    entities = [
        BalboaSensorEntity(spa, description)
        for description in FILTER_CYCLE_DESCRIPTIONS
    ]
    async_add_entities(entities)


@dataclass
class BalboaSensorEntityDescriptionMixin:
    """Mixin for required keys."""

    value_fn: Callable[[SpaClient], datetime | float | None]


@dataclass
class BalboaSensorEntityDescription(
    SensorEntityDescription, BalboaSensorEntityDescriptionMixin
):
    """A class that describes Balboa switch entities."""


FILTER_CYCLE_DESCRIPTIONS = (
    BalboaSensorEntityDescription(
        key="filter_cycle_1_start",
        name="Filter cycle 1 start",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda spa: get_start_datetime(
            spa.filter_cycle_1_start, spa.filter_cycle_1_duration
        ),
    ),
    BalboaSensorEntityDescription(
        key="filter_cycle_1_duration",
        name="Filter cycle 1 duration",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=TIME_SECONDS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda spa: spa.filter_cycle_1_duration.total_seconds(),
    ),
    BalboaSensorEntityDescription(
        key="filter_cycle_2_start",
        name="Filter cycle 2 start",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda spa: get_start_datetime(
            spa.filter_cycle_2_start, spa.filter_cycle_2_duration
        ),
    ),
    BalboaSensorEntityDescription(
        key="filter_cycle_2_duration",
        name="Filter cycle 2 duration",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=TIME_SECONDS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda spa: spa.filter_cycle_2_duration.total_seconds(),
    ),
)


class BalboaSensorEntity(BalboaEntity, SensorEntity):
    """Representation of a Balboa Spa sensor entity."""

    entity_description: BalboaSensorEntityDescription

    def __init__(
        self, spa: SpaClient, description: BalboaSensorEntityDescription
    ) -> None:
        """Initialize a Balboa sensor entity."""
        super().__init__(spa, description.name)
        self.entity_description = description

    @property
    def native_value(self) -> StateType | date | datetime | Decimal:
        """Return the value reported by the sensor."""
        return self.entity_description.value_fn(self._client)
