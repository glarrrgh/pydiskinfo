from unittest import TestCase
from src.pydiskinfo.human_readable_units import human_readable_units


class TestHumanReadableUnits(TestCase):
    def test_auto_1000_to_1KB(self) -> None:
        self.assertEqual(human_readable_units(999), '999B')
        self.assertEqual(human_readable_units(1000), '1.00KB')

# import pytest
# from human_readable_units import (
#     human_readable_units,
#     ReadableUnitError,
#     _calculate_auto_unit
# )


# @pytest.fixture
# def value():
#     """Default value for most tests"""
#     return 1234567890


# def test_hru_units(value) -> None:
#     """Test with specific unit types"""
#     assert human_readable_units(value=value, unit='') == '1234567890'
#     assert human_readable_units(value=1, unit='B') == '1B'
#     assert human_readable_units(value=-1.9, unit='B') == '-2B'
#     assert human_readable_units(value=value, unit='M') == '1234.57M'
#     assert human_readable_units(value=value, unit='MiB') == '1177.38MiB'
#     with pytest.raises(ReadableUnitError):
#         human_readable_units(value=value, unit='FiB')


# def test_hru_auto_unit(value) -> None:
#     """Test with the auto unit type"""
#     assert human_readable_units(value=value) == '1.23GB'
#     with pytest.raises(ReadableUnitError):
#         human_readable_units(value=value, value_type='P')


# def test_hru_decimal_places(value) -> None:
#     """Test of the decimal places feature"""
#     assert human_readable_units(
#         value=value,
#         unit='M',
#         decimal_places=3
#     ) == '1234.568M'
#     assert human_readable_units(
#         value=value,
#         decimal_places=3
#     ) == '1.235GB'
#     assert human_readable_units(
#         value=value,
#         decimal_places=11
#     ) == '1.23GB'
#     assert human_readable_units(
#         value=1999999999,
#         decimal_places=0
#     ) == '2GB'


# def test_hru_auto_unit_value_type(value) -> None:
#     """Test of auto unit with value types"""
#     assert human_readable_units(
#         value=value,
#         value_type='B'
#     ) == '1.23GB'
#     assert human_readable_units(
#         value=value,
#         value_type='M'
#     ) == '1.23G'
#     assert human_readable_units(
#         value=value,
#         value_type='I'
#     ) == '1.15GiB'
#     with pytest.raises(ReadableUnitError):
#         human_readable_units(value=value, value_type='P')


# def test_calculate_auto_unit(value) -> None:
#     """Test of the calculate auto unit private function"""
#     assert _calculate_auto_unit(
#         value,
#         value_type='I'
#     ) == (1.1497809458523989, 'GiB')
#     assert _calculate_auto_unit(value, value_type='B') == (1.23456789, 'GB')
#     assert _calculate_auto_unit(value, value_type='M') == (1.23456789, 'G')
#     assert _calculate_auto_unit(1, value_type='I') == (1.0, 'B')
#     assert _calculate_auto_unit(1, value_type='B') == (1.0, 'B')
#     assert _calculate_auto_unit(1, value_type='M') == (1.0, '')
