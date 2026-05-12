"""Button platform for Yandex Cloud Balance."""

from __future__ import annotations

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA_COORDINATOR, DOMAIN
from .coordinator import YandexCloudBalanceCoordinator

BUTTON_DESCRIPTION = ButtonEntityDescription(
    key="manual_update",
    translation_key="manual_update",
    device_class=ButtonDeviceClass.UPDATE,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Yandex Cloud Balance buttons."""
    coordinator: YandexCloudBalanceCoordinator = hass.data[DOMAIN][entry.entry_id][
        DATA_COORDINATOR
    ]

    async_add_entities(
        [
            YandexCloudBalanceUpdateButton(
                coordinator=coordinator,
                entry=entry,
            )
        ]
    )


class YandexCloudBalanceUpdateButton(
    CoordinatorEntity[YandexCloudBalanceCoordinator],
    ButtonEntity,
):
    """Button for manually refreshing Yandex Cloud balance."""

    entity_description = BUTTON_DESCRIPTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: YandexCloudBalanceCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize button."""
        super().__init__(coordinator)

        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_manual_update"
        self._attr_translation_key = "manual_update"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Yandex Cloud Billing",
            manufacturer="Yandex Cloud",
            entry_type=DeviceEntryType.SERVICE,
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_request_refresh()
