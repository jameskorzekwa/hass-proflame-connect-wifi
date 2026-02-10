"""Provides sensor entities for Proflame fireplaces."""
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, PROFLAME_COORDINATOR, ApiAttrs
from .coordinator import ProflameDataCoordinator
from .entity import ProflameEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create sensors for Proflame fireplaces."""
    # No sensors are currently available from the fireplace device.
    # The ESP module does not broadcast diagnostic values (free_heap,
    # min_free_heap, wifi_signal_str) over the WebSocket protocol.
