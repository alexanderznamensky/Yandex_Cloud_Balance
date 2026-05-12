"""Yandex Cloud Balance integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .api import YandexCloudBillingApi
from .const import CONF_OAUTH_TOKEN, DATA_COORDINATOR, DOMAIN
from .coordinator import YandexCloudBalanceCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BUTTON]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Yandex Cloud Balance from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    api = YandexCloudBillingApi(
        hass=hass,
        oauth_token=entry.data[CONF_OAUTH_TOKEN],
    )

    coordinator = YandexCloudBalanceCoordinator(
        hass=hass,
        entry=entry,
        api=api,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        DATA_COORDINATOR: coordinator,
    }

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload integration when options are changed."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Yandex Cloud Balance."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok
