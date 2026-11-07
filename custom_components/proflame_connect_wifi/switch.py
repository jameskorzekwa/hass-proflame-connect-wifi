"""Provides light control for Proflame fireplaces."""
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, PROFLAME_COORDINATOR, OperatingMode, Preset
from .coordinator import ProflameDataCoordinator
from .entity import ProflameEntity
from .util import coalesce


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
    power = ProflamePower(coordinator)
    light = ProflameAuxLight(coordinator)
    async_add_entities([power, light])


class ProflamePower(ProflameEntity, SwitchEntity):
    """Creates a device to control fireplace lights."""

    def __init__(self, coordinator: ProflameDataCoordinator) -> None:
        """Create new instance of the ProflameFlame class."""
        super().__init__(
            coordinator,
            SwitchEntityDescription(
                icon="mdi:fireplace",
                key="fireplace",
                translation_key="fireplace",
            ),
        )
        self._attr_name = None

    @property
    def is_on(self) -> bool | None:
        """Return the current fireplace mode."""
        operating_mode = coalesce(self._device.operating_mode, OperatingMode.OFF)
        preset = self._device.preset
        if operating_mode == OperatingMode.OFF or preset == Preset.OFF:
            return False
        return True

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the fireplace off."""
        self._device.turn_off()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the fireplace on."""
        self._device.turn_on()


class ProflameAuxLight(ProflameEntity, SwitchEntity):
    """The fireplace light, driven by the IFC auxiliary (AUX) output.

    On fireplaces whose light is wired to the AUX relay this is the light
    control; the light entity drives the separate dimmable lamp output.
    """

    def __init__(self, coordinator: ProflameDataCoordinator) -> None:
        """Create new instance of the ProflameAuxLight class."""
        super().__init__(
            coordinator,
            SwitchEntityDescription(
                icon="mdi:lightbulb",
                key="aux_light",
                translation_key="aux_light",
            ),
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if the AUX output (light) is on."""
        return self._device.auxiliary_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light (AUX output) on."""
        self._device.set_auxiliary(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light (AUX output) off."""
        self._device.set_auxiliary(False)
