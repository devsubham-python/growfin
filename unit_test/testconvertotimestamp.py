import unittest
from datetime import datetime
from unittest.mock import patch,MagicMock
import os
import sys

import pytz
# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import convert_to_unixtimestamp 
from utils import DateTimeValidationError
from utils import _resolve_timezone  # Adjust if your file is named differently

class TestConvertToUnixTimestamp(unittest.TestCase):
    
    def test_valid_with_timezone(self):
        ts = convert_to_unixtimestamp("2024-01-01 12:00", "Asia/Kolkata")
        self.assertIsInstance(ts, int)

    def test_valid_with_local_timezone(self):
        ts = convert_to_unixtimestamp("2024-01-01 12:00")
        self.assertIsInstance(ts, int)

    def test_leap_year_date(self):
        ts = convert_to_unixtimestamp("2020-02-29 00:00", "UTC")
        self.assertIsInstance(ts, int)

    def test_dst_transition(self):
        # For regions with DST like US/Eastern
        ts = convert_to_unixtimestamp("2023-03-12 02:30", "US/Eastern")
        self.assertIsInstance(ts, int)

    def test_non_string_input_int(self):
        with self.assertRaises(TypeError):
            convert_to_unixtimestamp(20240101)

    def test_non_string_input_none(self):
        with self.assertRaises(TypeError):
            convert_to_unixtimestamp(None)

    def test_invalid_datetime_format(self):
        with self.assertRaises(DateTimeValidationError):
            convert_to_unixtimestamp("01-01-2024 12:00")

    def test_invalid_timezone(self):
        with self.assertRaises(ValueError):
            convert_to_unixtimestamp("2024-01-01 12:00", "Invalid/Zone")

    def test_empty_string(self):
        with self.assertRaises(DateTimeValidationError):
            convert_to_unixtimestamp("")

    def test_timezone_aware_datetime(self):
        dt = datetime.strptime("2024-01-01 12:00", "%Y-%m-%d %H:%M")
        aware_dt = pytz.timezone("Asia/Kolkata").localize(dt)
        ts = convert_to_unixtimestamp(aware_dt.strftime('%Y-%m-%d %H:%M'), "Asia/Kolkata")
        self.assertIsInstance(ts, int)

    def test_localization_failure(self):
        with patch("your_module._resolve_timezone") as mock_resolve:
            tz = pytz.timezone("UTC")
            mock_resolve.return_value = tz

            with patch("pytz.tzinfo.BaseTzInfo.localize", side_effect=Exception("Localization error")):
                with self.assertRaises(Exception):
                    convert_to_unixtimestamp("2024-01-01 12:00", "UTC")


class TestMonkeyPatchingConvertToUnixTimestamp(unittest.TestCase):

    def test_monkey_patch_strptime_returns_none(self):
        with patch("your_module.datetime.strptime", return_value=None):
            with self.assertRaises(AttributeError):
                convert_to_unixtimestamp("2024-01-01 12:00")

    def test_monkey_patch_get_localzone_none(self):
        with patch("your_module.tzlocal.get_localzone", return_value=None):
            with self.assertRaises(ValueError):
                convert_to_unixtimestamp("2024-01-01 12:00", None)

    def test_monkey_patch_pytz_timezone_raises(self):
        with patch("your_module.pytz.timezone", side_effect=pytz.UnknownTimeZoneError):
            with self.assertRaises(ValueError):
                convert_to_unixtimestamp("2024-01-01 12:00", "Fake/Zone")

    def test_monkey_patch_timestamp_failure(self):
        mock_dt = MagicMock()
        mock_dt.timestamp.side_effect = Exception("Failed to get timestamp")

        with patch("your_module.datetime.strptime", return_value=datetime(2024, 1, 1, 12, 0)):
            with patch("your_module._resolve_timezone", return_value=pytz.timezone("UTC")):
                with patch("your_module.pytz.timezone", return_value=pytz.timezone("UTC")):
                    with patch("your_module.pytz.timezone('UTC').localize", return_value=mock_dt):
                        with self.assertRaises(Exception):
                            convert_to_unixtimestamp("2024-01-01 12:00", "UTC")


    def test_monkey_patch_localize_exception(self):
        with patch("your_module._resolve_timezone") as mock_resolve:
            mock_tz = MagicMock()
            mock_tz.localize.side_effect = Exception("Localization fail")
            mock_resolve.return_value = mock_tz

            with self.assertRaises(Exception):
                convert_to_unixtimestamp("2024-01-01 12:00", "Asia/Kolkata")


if __name__ == "__main__":
    unittest.main()
