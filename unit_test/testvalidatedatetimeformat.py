import unittest
from unittest.mock import patch, Mock
import os
import sys
from datetime import datetime
# Add the parent directory (project root) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import validate_datetime_format
from utils import DateTimeValidationError

class TestValidateDatetimeFormat(unittest.TestCase):

    def test_valid_date(self):
        dt = validate_datetime_format("2023-12-25")
        self.assertIsInstance(dt, datetime)
        self.assertEqual(dt.year, 2023)
        self.assertEqual(dt.month, 12)
        self.assertEqual(dt.day, 25)

    def test_invalid_format_missing_zero(self):
        with self.assertRaises(DateTimeValidationError):
            validate_datetime_format("2023-1-5")

    def test_invalid_format_extra_characters(self):
        with self.assertRaises(DateTimeValidationError):
            validate_datetime_format("2023/12/25")

    def test_invalid_type_integer(self):
        with self.assertRaises(TypeError):
            validate_datetime_format(20230803)

    def test_invalid_type_none(self):
        with self.assertRaises(TypeError):
            validate_datetime_format(None)

    def test_invalid_format_empty_string(self):
        with self.assertRaises(DateTimeValidationError):
            validate_datetime_format("")

    def test_invalid_date_nonexistent(self):
        with self.assertRaises(DateTimeValidationError):
            validate_datetime_format("2023-02-30")

    def test_valid_leap_year(self):
        dt = validate_datetime_format("2024-02-29")
        self.assertEqual(dt.day, 29)

    def test_invalid_leap_year(self):
        with self.assertRaises(DateTimeValidationError):
            validate_datetime_format("2023-02-29")

    def test_valid_date_edge(self):
        dt = validate_datetime_format("2000-01-01")
        self.assertEqual(dt.year, 2000)

    # Monkey Testing 

    def test_fuzz_inputs(self):
        test_inputs = [
            123,                        # integer
            12.34,                     # float
            True,                      # bool
            None,                      # NoneType
            "25-12-2023",              # wrong format
            "2023-13-01",              # invalid month
            "2023-00-01",              # invalid month
            "2023-12-32",              # invalid day
            "2023-02-29",              # non-leap year
            "abcd-ef-gh",              # alphabets
            "",                        # empty string
            "2023-05-10 ",             # trailing space
            " 2023-05-10",             # leading space
            "2023-5-1",                # single digit month/day   
            "-1000-01-01",             # negative year
            "0000-00-00",              # invalid zero date
            [], {}, (), object(),     # other types
        ]

        for input_val in test_inputs:
            with self.subTest(input_val=input_val):
                with self.assertRaises((TypeError, DateTimeValidationError)):
                    validate_datetime_format(input_val)

if __name__ == '__main__':
    unittest.main()