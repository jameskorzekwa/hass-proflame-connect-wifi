"""Test the config flow."""
import sys
from unittest.mock import AsyncMock, MagicMock, patch

# Mock DhcpServiceInfo module before ANY imports that might use it
mock_dhcp_module = MagicMock()


class MockDhcpServiceInfo:
    """Mock DhcpServiceInfo class."""

    def __init__(self, ip, hostname, macaddress) -> None:
        """Initialize."""
        self.ip = ip
        self.hostname = hostname
        self.macaddress = macaddress


mock_dhcp_module.DhcpServiceInfo = MockDhcpServiceInfo
sys.modules["homeassistant.helpers.service_info.dhcp"] = mock_dhcp_module

import pytest  # noqa: E402
from homeassistant import config_entries, data_entry_flow  # noqa: E402
from homeassistant.const import (  # noqa: E402
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
)
from homeassistant.core import HomeAssistant  # noqa: E402

from custom_components.proflame_connect_wifi.const import DOMAIN  # noqa: E402
from custom_components.proflame_connect_wifi.config_flow import ConfigFlow  # noqa: E402


class MockConfigEntry:
    """Mock ConfigEntry class."""

    def __init__(self, domain, data, unique_id, source=config_entries.SOURCE_USER, options=None) -> None:
        """Initialize."""
        self.domain = domain
        self.data = data
        self.unique_id = unique_id
        self.source = source
        self.options = options or {}


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock(spec=HomeAssistant)
    hass.config_entries = MagicMock()
    hass.config_entries.async_entries.return_value = []
    return hass


@pytest.fixture
def flow(mock_hass):
    """Create the ConfigFlow instance."""
    flow = ConfigFlow()
    flow.hass = mock_hass
    flow.handler = DOMAIN  # Needed for async_entries filtering
    flow.context = {}      # Needed for storing state
    return flow


@pytest.mark.asyncio
async def test_dhcp_discovery_already_configured_by_host(flow, mock_hass) -> None:
    """Test we abort if the device is already configured by host, even if unique_id differs."""
    # Mock an existing entry with the same Host but NO unique ID (or different)
    existing_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "192.168.1.13",
            CONF_PORT: 3000,
            CONF_NAME: "Living Room",
        },
        unique_id="some_random_id"
    )
    mock_hass.config_entries.async_entries.return_value = [existing_entry]

    # DHCP discovery info with same IP but new/valid MAC
    discovery_info = MockDhcpServiceInfo(
        ip="192.168.1.13",
        hostname="espressif",
        macaddress="00:11:22:33:44:55"
    )

    # The abort happens before test_connectivity is reached, but we mock it anyway
    with patch(  # noqa: SIM117
        "custom_components.proflame_connect_wifi.config_flow.resolve_host",
        return_value="192.168.1.13"
    ), patch(
        "custom_components.proflame_connect_wifi.config_flow.resolve_ip",
        return_value="192.168.1.13"
    ), patch(
        "custom_components.proflame_connect_wifi.config_flow.test_connectivity",
        new_callable=AsyncMock,
        return_value=True,
    ):
        # We simulate the flow call
        # ConfigFlow.async_step_dhcp raises AbortFlow if it aborts
        with pytest.raises(data_entry_flow.AbortFlow) as excinfo:
            await flow.async_step_dhcp(discovery_info)

    # We EXPECT this to abort because the host matches an existing entry
    assert excinfo.value.reason == "already_configured"


@pytest.mark.asyncio
async def test_dhcp_discovery_legacy_ip_match(flow, mock_hass) -> None:
    """Test we abort if the device is already configured by IP (legacy entry), even if host mismatch."""
    # Mock an existing entry with IP as host, but NO CONF_IP_ADDRESS (legacy case)
    existing_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "192.168.1.13",
            # Intentionally omitting CONF_IP_ADDRESS to simulate old config
            CONF_PORT: 3000,
            CONF_NAME: "Living Room",
        },
        unique_id="some_random_id"
    )
    mock_hass.config_entries.async_entries.return_value = [existing_entry]

    # DHCP discovery info with same IP but resolved to hostname "espressif"
    discovery_info = MockDhcpServiceInfo(
        ip="192.168.1.13",
        hostname="espressif",
        macaddress="00:11:22:33:44:55"
    )

    # The abort happens before test_connectivity is reached, but we mock it anyway
    # resolve_host returns hostname, resolve_ip returns IP
    with patch(  # noqa: SIM117
        "custom_components.proflame_connect_wifi.config_flow.resolve_host",
        return_value="espressif"
    ), patch(
        "custom_components.proflame_connect_wifi.config_flow.resolve_ip",
        return_value="192.168.1.13"
    ), patch(
        "custom_components.proflame_connect_wifi.config_flow.test_connectivity",
        new_callable=AsyncMock,
        return_value=True,
    ):
        # We EXPECT this to abort because the IP matches an existing entry's CONF_HOST
        with pytest.raises(data_entry_flow.AbortFlow) as excinfo:
            await flow.async_step_dhcp(discovery_info)

    assert excinfo.value.reason == "already_configured"


@pytest.mark.asyncio
async def test_dhcp_discovery_non_proflame_device(flow, mock_hass) -> None:
    """Test we abort if the discovered ESP device is NOT a Proflame fireplace.

    The DHCP matcher uses hostname "espressif" which matches ANY ESP32/ESP8266
    device. Only devices that respond to the Proflame protocol should proceed.
    """
    # No existing entries
    mock_hass.config_entries.async_entries.return_value = []

    # DHCP discovery for a generic ESP device (smart plug, ESPHome sensor, etc.)
    discovery_info = MockDhcpServiceInfo(
        ip="192.168.0.59",
        hostname="espressif",
        macaddress="84:0d:8e:0f:1c:20"
    )

    with patch(  # noqa: SIM117
        "custom_components.proflame_connect_wifi.config_flow.resolve_host",
        return_value="192.168.0.59"
    ), patch(
        "custom_components.proflame_connect_wifi.config_flow.resolve_ip",
        return_value="192.168.0.59"
    ), patch(
        "custom_components.proflame_connect_wifi.config_flow.test_connectivity",
        new_callable=AsyncMock,
        return_value=False,  # Device does NOT speak Proflame protocol
    ):
        result = await flow.async_step_dhcp(discovery_info)

    assert result["type"] == "abort"
    assert result["reason"] == "not_proflame_device"
