"""Coordinator for Yandex Cloud Balance integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    BillingAccount,
    YandexCloudBillingApi,
    YandexCloudBillingAuthError,
    YandexCloudBillingConnectionError,
)
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class YandexCloudBalanceCoordinator(DataUpdateCoordinator[dict[str, BillingAccount]]):
    """Yandex Cloud Balance coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        api: YandexCloudBillingApi,
    ) -> None:
        """Initialize coordinator."""
        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=timedelta(minutes=scan_interval),
            always_update=False,
        )

        self.api = api

    async def _async_update_data(self) -> dict[str, BillingAccount]:
        """Fetch data from Yandex Cloud Billing API."""
        try:
            return await self.api.async_get_billing_accounts()

        except YandexCloudBillingAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err

        except YandexCloudBillingConnectionError as err:
            raise UpdateFailed(str(err)) from err
