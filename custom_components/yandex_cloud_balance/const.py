"""Constants for Yandex Cloud Balance integration."""

from __future__ import annotations

from homeassistant.const import CONF_SCAN_INTERVAL

DOMAIN = "yandex_cloud_balance"

CONF_OAUTH_TOKEN = "oauth_token"

DEFAULT_SCAN_INTERVAL = 60  # minutes

IAM_URL = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
BILLING_URL = "https://billing.api.cloud.yandex.net/billing/v1/billingAccounts"

DATA_COORDINATOR = "coordinator"
