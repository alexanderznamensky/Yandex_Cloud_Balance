"""API client for Yandex Cloud Billing."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import aiohttp

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import IAM_URL, BILLING_URL


class YandexCloudBillingError(Exception):
    """Base Yandex Cloud Billing error."""


class YandexCloudBillingAuthError(YandexCloudBillingError):
    """Authentication error."""


class YandexCloudBillingConnectionError(YandexCloudBillingError):
    """Connection error."""


@dataclass(slots=True)
class BillingAccount:
    """Yandex Cloud billing account."""

    account_id: str
    name: str
    balance: float
    status: str | None = None
    created_at: str | None = None


class YandexCloudBillingApi:
    """Yandex Cloud Billing API client."""

    def __init__(self, hass, oauth_token: str) -> None:
        """Initialize API client."""
        self.hass = hass
        self.oauth_token = oauth_token
        self.session = async_get_clientsession(hass)

        self._iam_token: str | None = None
        self._iam_expires_at: datetime | None = None

    async def async_get_iam_token(self) -> str:
        """Get or refresh IAM token."""
        if self._iam_token and self._iam_expires_at:
            if datetime.now(timezone.utc) < self._iam_expires_at - timedelta(minutes=5):
                return self._iam_token

        payload = {
            "yandexPassportOauthToken": self.oauth_token,
        }

        try:
            async with self.session.post(
                IAM_URL,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=20),
            ) as response:
                if response.status in (400, 401, 403):
                    raise YandexCloudBillingAuthError(
                        f"IAM auth failed with status {response.status}"
                    )

                if response.status >= 400:
                    text = await response.text()
                    raise YandexCloudBillingConnectionError(
                        f"IAM request failed with status {response.status}: {text}"
                    )

                data = await response.json()

        except aiohttp.ClientError as err:
            raise YandexCloudBillingConnectionError(str(err)) from err

        iam_token = data.get("iamToken")
        if not iam_token:
            raise YandexCloudBillingAuthError("IAM token is missing in response")

        self._iam_token = iam_token

        expires_at_raw = data.get("expiresAt")
        if expires_at_raw:
            try:
                self._iam_expires_at = datetime.fromisoformat(
                    expires_at_raw.replace("Z", "+00:00")
                )
            except ValueError:
                self._iam_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        else:
            self._iam_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        return iam_token

    async def async_get_billing_accounts(self) -> dict[str, BillingAccount]:
        """Get billing accounts with balances."""
        iam_token = await self.async_get_iam_token()

        headers = {
            "Authorization": f"Bearer {iam_token}",
        }

        try:
            async with self.session.get(
                BILLING_URL,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=20),
            ) as response:
                if response.status in (401, 403):
                    self._iam_token = None
                    self._iam_expires_at = None
                    raise YandexCloudBillingAuthError(
                        f"Billing auth failed with status {response.status}"
                    )

                if response.status >= 400:
                    text = await response.text()
                    raise YandexCloudBillingConnectionError(
                        f"Billing request failed with status {response.status}: {text}"
                    )

                data: dict[str, Any] = await response.json()

        except aiohttp.ClientError as err:
            raise YandexCloudBillingConnectionError(str(err)) from err

        accounts_raw = data.get("billingAccounts", [])
        accounts: dict[str, BillingAccount] = {}

        for index, item in enumerate(accounts_raw):
            account_id = (
                item.get("id")
                or item.get("billingAccountId")
                or f"account_{index + 1}"
            )

            name = item.get("name") or account_id
            raw_balance = item.get("balance")

            if raw_balance is None:
                continue

            try:
                balance = float(raw_balance)
            except (TypeError, ValueError):
                continue

            accounts[account_id] = BillingAccount(
                account_id=account_id,
                name=name,
                balance=balance,
                status=item.get("status"),
                created_at=item.get("createdAt"),
            )

        if not accounts:
            raise YandexCloudBillingConnectionError("No billing accounts found")

        return accounts
