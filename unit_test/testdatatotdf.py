import unittest
import pandas as pd
import os
import sys
from pandas.testing import assert_frame_equal

# Print to confirm the test file is executing
print("✅ Running test_utils.py")

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import data_to_dataframe  # Adjust if your file is named differently


class TestDataToDataFrame(unittest.TestCase):

    def test_valid_input(self):
        """Should return correct DataFrame with 2 rows and proper column types."""
        data = {
            "candles": [
                [1754019900, 630, 635, 625, 629.1, 115278],
                [1754019960, 628.85, 631.35, 628.35, 630.75, 177106]
            ]
        }
        df = data_to_dataframe(data)

        self.assertEqual(df.shape, (2, 7), "DataFrame shape mismatch: Expected (2, 7)")

        expected_cols = ['unix_timestamp', 'time_ist', 'open', 'high', 'low', 'close', 'volume']
        self.assertListEqual(df.columns.tolist(), expected_cols, f"Unexpected columns: {df.columns.tolist()}")

        self.assertEqual(df.loc[0, 'time_ist'].hour, 9, "IST time hour conversion failed")
        self.assertEqual(df.loc[0, 'time_ist'].minute, 15, "IST time minute conversion failed")

        for col in ['open', 'high', 'low', 'close', 'volume']:
            self.assertTrue(pd.api.types.is_float_dtype(df[col]), f"Column {col} is not float dtype")

    def test_empty_candles(self):
        data = {"candles": []}
        df = data_to_dataframe(data)
        self.assertTrue(df.empty, "Expected empty DataFrame for empty candles")
        self.assertListEqual(
            df.columns.tolist(),
            ['unix_timestamp', 'time_ist', 'open', 'high', 'low', 'close', 'volume'],
            "Column names incorrect for empty dataframe"
        )

    def test_invalid_input_not_dict(self):
        invalid_inputs = [None, [], "string", 123]
        for input_val in invalid_inputs:
            with self.subTest(input=input_val):
                df = data_to_dataframe(input_val)
                self.assertTrue(df.empty, f"Expected empty DataFrame for input: {input_val}")

    def test_missing_candles_key(self):
        data = {"foo": "bar"}
        df = data_to_dataframe(data)
        self.assertTrue(df.empty, "Expected empty DataFrame when 'candles' key is missing")

    def test_malformed_candle_row(self):
        malformed = {
            "candles": [
                [1754019900, 630, 635],  # too short
                "not_a_list",            # not a list
                [1754019960, 628.85, 631.35, 628.35, 630.75, 177106]  # valid
            ]
        }
        try:
            df = data_to_dataframe(malformed)
            self.assertEqual(len(df), 1, "Only valid row should be included")
        except Exception as e:
            self.fail(f"Function should handle malformed input without throwing. Error: {e}")

    def test_non_numeric_values(self):
        data = {
            "candles": [
                [1754019900, '630.0', 'bad', 625, 629.1, 'NaN']
            ]
        }
        df = data_to_dataframe(data)
        self.assertTrue(pd.isna(df.loc[0, 'high']), "Non-numeric 'high' should be NaN")
        self.assertTrue(pd.isna(df.loc[0, 'volume']), "Non-numeric 'volume' should be NaN")
        self.assertEqual(df.loc[0, 'open'], 630.0, "Open value did not convert correctly")

    def test_missing_fields_in_row(self):
        data = {
            "candles": [
                [1754019900, 630, None, 625, 629.1, 115278]
            ]
        }
        df = data_to_dataframe(data)
        self.assertTrue(pd.isna(df.loc[0, 'high']), "Missing value should convert to NaN")

    def test_column_order_and_types(self):
        data = {
            "candles": [
                [1754019900, "630", "635", "625", "629", "115000"]
            ]
        }
        df = data_to_dataframe(data)
        self.assertListEqual(
            df.columns.tolist(),
            ['unix_timestamp', 'time_ist', 'open', 'high', 'low', 'close', 'volume'],
            "Column order is incorrect"
        )
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df['time_ist']), "'time_ist' is not datetime")


if __name__ == "__main__":
    unittest.main(verbosity=2)
