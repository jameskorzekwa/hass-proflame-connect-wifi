"""Tests for the util module."""
from custom_components.proflame_connect_wifi.util import coalesce, constrain, Temperature

def test_coalesce():
    """Test coalesce returns the first non-null argument."""
    assert coalesce(1, 2) == 1
    assert coalesce(None, 2) == 2
    assert coalesce(None, None) is None
    assert coalesce(None, 0, 2) == 0

def test_constrain():
    """Test constrain limits numbers to a range."""
    assert constrain(5, 0, 10) == 5
    assert constrain(-5, 0, 10) == 0
    assert constrain(15, 0, 10) == 10
    assert constrain(0, 0, 10) == 0
    assert constrain(10, 0, 10) == 10

def test_temperature_conversion():
    """Test temperature conversion between Celcius and Fahrenheit."""
    # Test C -> C/F
    temp = Temperature(25)
    assert temp.to_celcius() == 25
    assert temp.to_fahrenheit() == 77.0

    # Test F -> C/F
    temp = Temperature.fahrenheit(32)
    assert temp.to_celcius() == 0
    assert temp.to_fahrenheit() == 32.0

    # Test with static method
    temp_c = Temperature.celcius(100)
    assert temp_c.to_celcius() == 100
    assert temp_c.to_fahrenheit() == 212.0
