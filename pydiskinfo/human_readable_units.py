"""A module for getting integer values as human readable units in
a computer storage context.

Copyright (c) 2022 Lars Henrik Ericson

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from typing import Tuple


UNITS = {
    '': 1,
    'K': 1_000,
    'M': 1_000_000,
    'G': 1_000_000_000,
    'T': 1_000_000_000_000,
    'P': 1_000_000_000_000_000,
    'B': 1,
    'KB': 1_000,
    'MB': 1_000_000,
    'GB': 1_000_000_000,
    'TB': 1_000_000_000_000,
    'PB': 1_000_000_000_000_000,
    'KiB': 1_024,
    'MiB': pow(1_024, 2),
    'GiB': pow(1_024, 3),
    'TiB': pow(1_024, 4),
    'PiB': pow(1_024, 5)
}


class ReadableUnitError(Exception):
    """Exception raised if unit specified is not in dict UNITS"""
    def __init__(self, message):
        super().__init__(message)
        self.message = "unit specified not found in UNITS"


def human_readable_units(value: int,
                         unit: str = 'auto',
                         value_type: str = 'B',
                         decimal_places: int = 2
                         ) -> str:
    """Converts an int to a string with a unit.

       If unit is omitted, the function will choose a fitting unit.
       If unit is omitted, and type is omitted, it will choose something like
       KB. type can be:
            'B': decimal bytes (KB for instance)
            'M': no bytes (K for instance)
            'I': binary bytes (KiB for instance)
       If unit is specified, type will be ignored.
       decimal_places describes number of places after the dot. It must be a
       number between and including 0 and 9.

       Will raise a ReadableUnitError if passed the wrong value in unit
    """
    if unit == 'auto':
        return_value, return_unit = _calculate_auto_unit(
                                        value=value,
                                        value_type=value_type
                                    )
    else:
        return_unit = unit
        try:
            return_value = value/UNITS[unit]
        except KeyError as ke:
            raise ReadableUnitError(f'{unit} is not a valid unit') from ke
    if type(decimal_places) != int or decimal_places < 0 or decimal_places > 9:
        decimal_places = 2
    if return_unit == 'B' or return_unit == '':
        decimal_places = 0
    return f'{return_value:.{decimal_places}f}{return_unit}'


def _calculate_auto_unit(value: int, value_type: str) -> Tuple[float, str]:
    """Evaluates return value and return unit type based on value type and
    value"""
    value_types = {
        'I': ('PiB', 'TiB', 'GiB', 'MiB', 'KiB', 'B'),
        'M': ('P', 'T', 'G', 'M', 'K', ''),
        'B': ('PB', 'TB', 'GB', 'MB', 'KB', 'B')
    }
    try:
        for each_unit_type in value_types[value_type]:
            return_unit_type = each_unit_type
            try:
                return_value = value/UNITS[each_unit_type]
            except KeyError as ke:
                raise ReadableUnitError(
                    message=f'{str(ke)} is not a valid unit type'
                )
            if return_value > 1:
                break
    except KeyError as ke:
        raise ReadableUnitError(
            message=f'{str(ke)} is not a valid value type'
        ) from ke
    return return_value, return_unit_type
