"""Tests for the ProflameClient."""
import pytest
from unittest.mock import MagicMock
from custom_components.proflame_connect_wifi.client import ProflameClient
from custom_components.proflame_connect_wifi.const import (
    ApiAttrs,
    MAX_FAN_SPEED,
    MIN_FAN_SPEED,
    OperatingMode,
    Preset,
)


@pytest.fixture
def client():
    """Fixture to create a client instance."""
    client = ProflameClient("device_id", "127.0.0.1")
    # Mock the queue to verify set_state calls
    client._queue = MagicMock()
    # Commands are only queued while connected
    client._connected = True
    # Populate some initial state
    client._state = {
        ApiAttrs.OPERATING_MODE: OperatingMode.MANUAL,
        ApiAttrs.FAN_SPEED: 0,
        ApiAttrs.FLAME_HEIGHT: 0,
        ApiAttrs.LIGHT_BRIGHTNESS: 0,
    }
    return client


def test_fan_speed_constraints(client):
    """Test fan speed is constrained."""
    client.set_fan_speed(100)
    # set_state puts {field: value} into queue.
    # put_nowait is a method of asyncio.Queue, we mocked it.
    client._queue.put_nowait.assert_called_with({ApiAttrs.FAN_SPEED: MAX_FAN_SPEED})

    client.set_fan_speed(-100)
    client._queue.put_nowait.assert_called_with({ApiAttrs.FAN_SPEED: MIN_FAN_SPEED})


def test_turn_off(client):
    """Test turn_off method."""
    client.turn_off()
    # Mode OFF is sent, and the light (AUX) follows the fireplace off.
    client._queue.put_nowait.assert_any_call(
        {ApiAttrs.OPERATING_MODE: OperatingMode.OFF}
    )
    client._queue.put_nowait.assert_called_with({ApiAttrs.AUXILIARY: 0})


def test_tracking_state(client):
    """Test state tracking for restoring state."""
    # Simulate a state update from the device
    # By calling the callback directly or handle_json_message?
    # client.register_callback(self._track_state) is called in __init__

    # Let's call _track_state directly or simulate state change
    client._track_state(ApiAttrs.FAN_SPEED, 3)
    assert client._stored_fan_speed == 3

    client._track_state(ApiAttrs.FAN_SPEED, 0)
    assert client._stored_fan_speed == 3  # Should not update on 0


def test_unknown_climate_state_is_not_heating_or_celsius():
    """Unknown mode/flame/unit cannot invent heating or encode a setpoint."""
    client = ProflameClient("device_id", "127.0.0.1")
    assert client.hvac_action is None
    assert client.hvac_mode is None
    assert client.temperature_unit is None
    client._state[ApiAttrs.OPERATING_MODE] = OperatingMode.MANUAL
    assert client.hvac_action is None
    assert client.hvac_mode is None


def test_zero_room_temperature_is_known(client):
    """A valid zero reading is not treated as missing state."""
    client._state[ApiAttrs.CURRENT_TEMPERATURE] = 0
    assert client.current_temperature == 0


# ---- AUX light and light-follows-fireplace ----


def _sent(client):
    """Return the list of {field: value} commands queued so far."""
    return [c.args[0] for c in client._queue.put_nowait.call_args_list]


def test_auxiliary_on_reflects_state(client):
    """auxiliary_on is None until reported, then follows auxiliary_out."""
    assert client.auxiliary_on is None
    client._state[ApiAttrs.AUXILIARY] = 1
    assert client.auxiliary_on is True
    client._state[ApiAttrs.AUXILIARY] = 0
    assert client.auxiliary_on is False


def test_set_auxiliary_sends_command(client):
    """The light switch writes auxiliary_out as 1/0."""
    client.set_auxiliary(True)
    client.set_auxiliary(False)
    assert _sent(client) == [{ApiAttrs.AUXILIARY: 1}, {ApiAttrs.AUXILIARY: 0}]


def test_turning_on_from_off_turns_light_on(client):
    """Fireplace on from off also switches the light on."""
    client._state[ApiAttrs.OPERATING_MODE] = OperatingMode.OFF
    client.turn_on()
    assert _sent(client) == [
        {ApiAttrs.OPERATING_MODE: OperatingMode.MANUAL},
        {ApiAttrs.AUXILIARY: 1},
    ]


def test_turning_off_turns_light_off(client):
    """Fireplace off also switches the light off."""
    client._state[ApiAttrs.FLAME_HEIGHT] = 3
    client.turn_off()
    assert _sent(client) == [
        {ApiAttrs.OPERATING_MODE: OperatingMode.OFF},
        {ApiAttrs.AUXILIARY: 0},
    ]


def test_mode_change_while_on_leaves_light_alone(client):
    """Switching Manual -> Thermostat while burning doesn't touch the light."""
    client._state[ApiAttrs.FLAME_HEIGHT] = 3
    client.set_operating_mode(OperatingMode.THERMOSTAT)
    assert _sent(client) == [{ApiAttrs.OPERATING_MODE: OperatingMode.THERMOSTAT}]


def test_thermostat_preset_from_off_turns_light_on(client):
    """Selecting Thermostat from off counts as turning the fireplace on."""
    client._state[ApiAttrs.OPERATING_MODE] = OperatingMode.OFF
    client.set_preset(Preset.THERMOSTAT)
    assert {ApiAttrs.AUXILIARY: 1} in _sent(client)


def test_flame_to_zero_in_manual_turns_light_off(client):
    """Manual with flame 0 is off, so the light follows."""
    client._state[ApiAttrs.FLAME_HEIGHT] = 4
    client.set_flame_height(0)
    assert _sent(client) == [
        {ApiAttrs.FLAME_HEIGHT: 0},
        {ApiAttrs.AUXILIARY: 0},
    ]


def test_flame_change_while_on_leaves_light_alone(client):
    """Adjusting flame while already on doesn't touch the light."""
    client._state[ApiAttrs.FLAME_HEIGHT] = 4
    client.set_flame_height(2)
    assert _sent(client) == [{ApiAttrs.FLAME_HEIGHT: 2}]


def test_heat_from_off_turns_light_on(client):
    """The climate 'heat' action from off turns the light on."""
    client._state[ApiAttrs.OPERATING_MODE] = OperatingMode.OFF
    client.heat()
    assert {ApiAttrs.AUXILIARY: 1} in _sent(client)
    assert {ApiAttrs.AUXILIARY: 0} not in _sent(client)
