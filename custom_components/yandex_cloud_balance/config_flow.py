"""Config flow for Yandex Cloud Balance integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .api import (
    YandexCloudBillingApi,
    YandexCloudBillingAuthError,
    YandexCloudBillingConnectionError,
)
from .const import CONF_OAUTH_TOKEN, DEFAULT_SCAN_INTERVAL, DOMAIN


class YandexCloudBalanceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Yandex Cloud Balance."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()

            oauth_token = user_input[CONF_OAUTH_TOKEN]

            try:
                api = YandexCloudBillingApi(self.hass, oauth_token)
                await api.async_get_billing_accounts()

            except YandexCloudBillingAuthError:
                errors["base"] = "invalid_auth"

            except YandexCloudBillingConnectionError:
                errors["base"] = "cannot_connect"

            except Exception:
                errors["base"] = "unknown"

            else:
                return self.async_create_entry(
                    title="Yandex Cloud Balance",
                    data={
                        CONF_OAUTH_TOKEN: oauth_token,
                    },
                    options={
                        CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_OAUTH_TOKEN): str,
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=DEFAULT_SCAN_INTERVAL,
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=1440)),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> YandexCloudBalanceOptionsFlow:
        """Create the options flow."""
        return YandexCloudBalanceOptionsFlow(config_entry)


class YandexCloudBalanceOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Yandex Cloud Balance."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_scan_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            DEFAULT_SCAN_INTERVAL,
        )

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=current_scan_interval,
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=1440)),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )
