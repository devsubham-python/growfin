import unittest
from datetime import datetime, timedelta
import os 
import sys
# Add the parent directory (project root) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import validate_parameters
from constants import SUPPORTED_INTERVALS, API_LOOKBACK_LIMITS
from utils import ParameterValidationError, DateTimeValidationError
from unittest.mock import patch

class TestValidateParameters(unittest.TestCase):

    def setUp(self):
        self.valid_start = "2024-01-01"
        self.valid_end = "2024-01-30"

    def test_valid_lookback(self):
        validate_parameters(5, lookback_days=30)  # Should not raise

    def test_valid_date_range(self):
        validate_parameters(15, start_date_str=self.valid_start, end_date_str=self.valid_end)

    def test_unsupported_interval(self):
        with self.assertRaises(ParameterValidationError):
            validate_parameters(10, lookback_days=10)

    def test_both_lookback_and_range_provided(self):
        with self.assertRaises(ParameterValidationError):
            validate_parameters(5, lookback_days=5, start_date_str=self.valid_start, end_date_str=self.valid_end)

    def test_neither_lookback_nor_range_provided(self):
        with self.assertRaises(ParameterValidationError):
            validate_parameters(5)

    def test_lookback_exceeds_limit(self):
        with self.assertRaises(ParameterValidationError):
            validate_parameters(1, lookback_days=40)  # Exceeds 30-day limit for 1-min

    def test_date_range_exceeds_limit(self):
        too_old_start = (datetime.now() - timedelta(days=200)).strftime('%Y-%m-%d')
        too_old_end = (datetime.now() - timedelta(days=190)).strftime('%Y-%m-%d')

        with self.assertRaises(ParameterValidationError):
            validate_parameters(5, start_date_str=too_old_start, end_date_str=too_old_end)

    def test_start_after_end_date(self):
        with self.assertRaises(ParameterValidationError):
            validate_parameters(5, start_date_str="2024-01-31", end_date_str="2024-01-01")

    def test_invalid_date_format(self):
        with self.assertRaises(ParameterValidationError):
            validate_parameters(5, start_date_str="2024/01/01", end_date_str="2024-01-31")


# ---------------------
# Monkey Tests
# ---------------------
class TestMonkeyPatching(unittest.TestCase):

    def test_mock_validate_datetime_format_failure(self):
        with patch("utils.validate_datetime_format", side_effect=DateTimeValidationError("bad format")):
            with self.assertRaises(ParameterValidationError) as ctx:
                validate_parameters(15, start_date_str="2024-01-01", end_date_str="2024-01-31")
            self.assertIn("Date validation failed", str(ctx.exception))

    def test_mock_api_limit_to_low_value(self):
        with patch("constants.API_LOOKBACK_LIMITS", {5: 1}):
            with self.assertRaises(ParameterValidationError):
                validate_parameters(5, lookback_days=5)

    def test_mock_datetime_now_to_shift_range(self):
        with patch("utils.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 1)
            mock_datetime.strptime.side_effect = lambda s, f: datetime.strptime(s, f)

            # Date range appears to exceed limit in this mocked context
            with self.assertRaises(ParameterValidationError):
                validate_parameters(5, start_date_str="2024-01-01", end_date_str="2024-01-10")

    def test_mock_datetime_format_return_static(self):
        # Always return Jan 1st, 2000 — should trigger range violation
        with patch("utils.validate_datetime_format", return_value=datetime(2000, 1, 1)):
            with self.assertRaises(ParameterValidationError):
                validate_parameters(15, start_date_str="2024-01-01", end_date_str="2024-01-02")

    def test_mock_supported_intervals_excludes_current(self):
        with patch("constants.SUPPORTED_INTERVALS", {1, 15}):
            with self.assertRaises(ParameterValidationError):
                validate_parameters(5, lookback_days=10)


if __name__ == "__main__":
    unittest.main()

