"""Sensor platform for Yandex Cloud Balance."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import BillingAccount
from .const import DATA_COORDINATOR, DOMAIN
from .coordinator import YandexCloudBalanceCoordinator

SENSOR_DESCRIPTION = SensorEntityDescription(
    key="balance",
    native_unit_of_measurement="RUB",
    state_class=SensorStateClass.MEASUREMENT,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Yandex Cloud Balance sensors."""
    coordinator: YandexCloudBalanceCoordinator = hass.data[DOMAIN][entry.entry_id][
        DATA_COORDINATOR
    ]

    entities: list[YandexCloudBalanceSensor] = []

    for account_id in coordinator.data:
        entities.append(
            YandexCloudBalanceSensor(
                coordinator=coordinator,
                entry=entry,
                account_id=account_id,
            )
        )

    async_add_entities(entities)


class YandexCloudBalanceSensor(
    CoordinatorEntity[YandexCloudBalanceCoordinator],
    SensorEntity,
):
    """Yandex Cloud billing balance sensor."""

    entity_description = SENSOR_DESCRIPTION
    _attr_has_entity_name = True
    _attr_icon = "mdi:cash"
    _attr_suggested_display_precision = 2

    def __init__(
        self,
        coordinator: YandexCloudBalanceCoordinator,
        entry: ConfigEntry,
        account_id: str,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)

        self.entry = entry
        self.account_id = account_id

        account = self._account

        self._attr_unique_id = f"{entry.entry_id}_{account_id}_balance"
        self._attr_name = account.name if account else "Balance"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Yandex Cloud Billing",
            manufacturer="Yandex Cloud",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def _account(self) -> BillingAccount | None:
        """Return billing account data."""
        return self.coordinator.data.get(self.account_id)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return super().available and self._account is not None

    @property
    def native_value(self) -> float | None:
        """Return balance."""
        account = self._account
        if account is None:
            return None

        return float(f"{float(account.balance):.2f}")

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        account = self._account
        if account is None:
            return {}

        return {
            "account_id": account.account_id,
            "account_name": account.name,
            "status": account.status,
            "created_at": account.created_at,
        }
