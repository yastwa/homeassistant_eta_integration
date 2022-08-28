"""Adds config flow for Blueprint."""
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.const import (CONF_HOST, CONF_PORT)
from .const import (
    DOMAIN,
    USER_MENU_SUFFIX,
    PLATFORMS, REQUEST_TIMEOUT
)

SENSOR_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PATH): cv.,
    }
)

class EtaFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Eta."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        # Uncomment the next 2 lines if only a single instance of the integration is allowed:
        # if self._async_current_entries():
        #     return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            valid = await self._test_url(
                self.hass,
                user_input[CONF_HOST],
                user_input[CONF_PORT]
            )
            if valid:
                return self.async_create_entry(
                    title=f"ETA at {user_input[CONF_HOST]}", data=user_input
                )
            else:
                self._errors["base"] = "url_broken"

            return await self._show_config_form(user_input)

        user_input = {}
        # Provide defaults for form
        user_input[CONF_HOST] = "0.0.0.0"
        user_input[CONF_PORT] = "8080"

        return await self._show_config_form(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return EtaOptionsFlowHandler(config_entry)

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=user_input[CONF_HOST]): str,
                    vol.Required(CONF_PORT, default=user_input[CONF_PORT]): str,
                }
            ),
            errors=self._errors,
        )

    async def _test_url(self, hass, host, port):
        """Return true if host port is valid."""
        session = async_get_clientsession(hass)
        try:
            #with async_timeout.timeout(REQUEST_TIMEOUT):
            #    resp = await session.get(f"http://{host}:{port}")
            return True#resp.status == 200
        except Exception as e:  # pylint: disable=broad-except
            print(e)
            pass
        return False


class EtaOptionsFlowHandler(config_entries.OptionsFlow):
    """Blueprint config flow options handler."""

    def __init__(self, config_entry):
        """Initialize HACS options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(x, default=self.options.get(x, True)): bool
                    for x in sorted(PLATFORMS)
                }
            ),
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title=self.config_entry.data.get(CONF_HOST), data=self.options
        )
