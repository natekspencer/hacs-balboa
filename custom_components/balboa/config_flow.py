"""Config flow for Balboa Spa Client integration."""
from __future__ import annotations

import logging
from typing import Any

from pybalboa import SpaClient
from pybalboa.exceptions import SpaConnectionError
import voluptuous as vol

from homeassistant import config_entries, exceptions
from homeassistant.components.dhcp import DhcpServiceInfo
from homeassistant.const import CONF_HOST
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.device_registry import format_mac

from .const import CONF_SYNC_TIME, DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({vol.Required(CONF_HOST): str})


async def validate_input(data: dict[str, Any]) -> dict[str, str]:
    """Validate the user input allows us to connect."""
    _LOGGER.debug("Attempting to connect to %s", data[CONF_HOST])
    try:
        async with SpaClient(data[CONF_HOST]) as spa:
            if not await spa.async_configuration_loaded():
                raise CannotConnect
            mac = format_mac(spa.mac_address)
            model = spa.model
    except SpaConnectionError as err:
        raise CannotConnect from err

    return {"title": model, "formatted_mac": mac}


class BalboaSpaClientFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Balboa Spa Client config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    _host: str | None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Get the options flow for this handler."""
        return BalboaSpaClientOptionsFlowHandler(config_entry)

    async def async_step_dhcp(self, discovery_info: DhcpServiceInfo) -> FlowResult:
        """Handle dhcp discovery."""
        _LOGGER.debug("Balboa device found via DHCP: %s", discovery_info)
        await self.async_set_unique_id(format_mac(discovery_info.macaddress))
        self._abort_if_unique_id_configured(updates={CONF_HOST: discovery_info.ip})
        self._host = discovery_info.ip
        return await self.async_step_confirm()

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle user-confirmation of discovered Balboa spa."""
        _LOGGER.debug("Confirm Balboa device found via DHCP: %s", user_input)
        if user_input is not None:
            return await self.async_step_user({CONF_HOST: self._host})

        return self.async_show_form(
            step_id="confirm", description_placeholders={"device": self._host}
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        errors = {}
        if user_input is not None:
            self._async_abort_entries_match({CONF_HOST: user_input[CONF_HOST]})
            try:
                info = await validate_input(user_input)
                _LOGGER.debug("Balboa validated input: %s", user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info["formatted_mac"])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class BalboaSpaClientOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Balboa Spa Client options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize Balboa Spa Client options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage Balboa Spa Client options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SYNC_TIME,
                        default=self.config_entry.options.get(CONF_SYNC_TIME, False),
                    ): bool,
                }
            ),
        )
