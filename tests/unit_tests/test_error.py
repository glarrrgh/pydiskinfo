from unittest import TestCase
from exceptions import PyDiskInfoParseError


class ErrorTests(TestCase):
    """Testing the errors..."""
    def test_pydiskinfoparseerror_no_error(self) -> None:
        """Test that the exception can be raised without the error parameter"""
        with self.assertRaises(
            PyDiskInfoParseError
        ):
            raise PyDiskInfoParseError('testing')
