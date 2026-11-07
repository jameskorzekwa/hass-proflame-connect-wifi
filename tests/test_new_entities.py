"""Tests for the AUX light switch and fan speed number entities."""
from unittest.mock import MagicMock

import pytest

from custom_components.proflame_connect_wifi.const import MAX_FAN_SPEED, MIN_FAN_SPEED
from custom_components.proflame_connect_wifi.number import ProflameFanSpeed
from custom_components.proflame_connect_wifi.switch import ProflameAuxLight


def _coordinator():
    coordinator = MagicMock()
    coordinator.unique_id = "abc"
    coordinator.device_info = None
    return coordinator


@pytest.mark.asyncio
async def test_aux_light_switch():
    """Light switch reads and writes the AUX output."""
    coordinator = _coordinator()
    entity = ProflameAuxLight(coordinator)
    device = coordinator.client
    device.auxiliary_on = True
    assert entity.is_on is True
    assert entity.unique_id == "aux_light_abc"
    assert entity.entity_description.translation_key == "aux_light"
    await entity.async_turn_off()
    device.set_auxiliary.assert_called_with(False)
    await entity.async_turn_on()
    device.set_auxiliary.assert_called_with(True)


@pytest.mark.asyncio
async def test_fan_speed_number():
    """Fan speed number is a 0-6 slider bound to the fan speed."""
    coordinator = _coordinator()
    entity = ProflameFanSpeed(coordinator)
    device = coordinator.client
    device.fan_speed = 4
    assert entity.native_value == 4
    assert entity.native_min_value == MIN_FAN_SPEED
    assert entity.native_max_value == MAX_FAN_SPEED
    assert entity.native_step == 1
    assert entity.unique_id == "fan_speed_abc"
    await entity.async_set_native_value(5.0)
    device.set_fan_speed.assert_called_with(5)
