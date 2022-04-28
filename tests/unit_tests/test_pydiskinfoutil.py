from unittest import TestCase


class PackageTests(TestCase):
    def test_package_execution(self) -> None:
        try:
            import src.pydiskinfo.__main__
        except ImportError:
            raise AssertionError(
                'src/pydiskinfo/__main__.py does not seem to exist'
                )
