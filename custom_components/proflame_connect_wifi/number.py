"""Provides light control for Proflame fireplaces."""
from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    MAX_FAN_SPEED,
    MAX_FLAME_HEIGHT,
    MIN_FAN_SPEED,
    MIN_FLAME_HEIGHT,
    PROFLAME_COORDINATOR,
)
from .coordinator import ProflameDataCoordinator
from .entity import ProflameEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create the number for Proflame fireplaces."""
    entry_id = config_entry.entry_id
    coordinator: ProflameDataCoordinator = hass.data[DOMAIN][entry_id][
        PROFLAME_COORDINATOR
    ]
    flame = ProflameFlame(coordinator)
    fan_speed = ProflameFanSpeed(coordinator)
    async_add_entities([flame, fan_speed])


class ProflameFlame(ProflameEntity, NumberEntity):
    """Creates a device to control fireplace lights."""

    _attr_native_max_value: float = MAX_FLAME_HEIGHT
    _attr_native_min_value: float = MIN_FLAME_HEIGHT
    _attr_native_step: float = 1
    _attr_mode: NumberMode = NumberMode.SLIDER

    def __init__(self, coordinator: ProflameDataCoordinator) -> None:
        """Create new instance of the ProflameFlame class."""
        super().__init__(
            coordinator,
            NumberEntityDescription(
                icon="mdi:fire",
                key="burner",
                translation_key="burner",
            ),
        )

    @property
    def native_value(self) -> float | None:
        """Returns the current flame height."""
        return self._device.flame_height

    async def async_set_native_value(self, value: float) -> None:
        """Update the desired height of the flame."""
        self._device.set_flame_height(int(value))


class ProflameFanSpeed(ProflameEntity, NumberEntity):
    """Direct 0-6 control of the comfort fan speed."""

    _attr_native_max_value: float = MAX_FAN_SPEED
    _attr_native_min_value: float = MIN_FAN_SPEED
    _attr_native_step: float = 1
    _attr_mode: NumberMode = NumberMode.SLIDER

    def __init__(self, coordinator: ProflameDataCoordinator) -> None:
        """Create new instance of the ProflameFanSpeed class."""
        super().__init__(
            coordinator,
            NumberEntityDescription(
                icon="mdi:fan",
                key="fan_speed",
                translation_key="fan_speed",
            ),
        )

    @property
    def native_value(self) -> float | None:
        """Return the current fan speed (0 while the fireplace is off)."""
        return self._device.fan_speed

    async def async_set_native_value(self, value: float) -> None:
        """Set the comfort fan speed."""
        self._device.set_fan_speed(int(value))
