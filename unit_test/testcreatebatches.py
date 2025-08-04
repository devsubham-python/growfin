import unittest
from datetime import datetime, timedelta
from unittest.mock import patch
from io import StringIO
import os
import sys


# This line is correct and necessary. It adds the project's root folder to the path.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Assuming a standard project structure where 'grow_api' is a source root
from utils import create_batches, validate_datetime_format
from constants import BATCH_LIMITS, API_LOOKBACK_LIMITS

class TestCreateBatches(unittest.TestCase):

    def test_lookback_mode_uneven_split(self):
        """
        Tests lookback mode where the total days are not an even multiple of the batch size.
        Input: interval=1 (7-day batches), lookback_days=30
        Expected: 4 batches of 7 days, and 1 final batch of 2 days.
        """
        interval = 1
        lookback_days = 30
        max_days_per_batch = BATCH_LIMITS[interval]['max_days_per_request']  # 7
        
        mock_now = datetime(2025, 8, 31, 15, 0)
        with patch('utils.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now
            # Ensure strptime still works for internal calls if any
            mock_datetime.strptime.side_effect = lambda d, f: datetime.strptime(d, f)

            batches = create_batches(interval_minutes=interval, lookback_days=lookback_days)

        self.assertEqual(len(batches), 5) # 30 days / 7 = 4 full batches + 1 remainder
        
        expected_start_date = mock_now - timedelta(days=lookback_days)
        self.assertEqual(batches[0]['start'], expected_start_date)
        self.assertEqual(batches[0]['end'], expected_start_date + timedelta(days=max_days_per_batch))
        self.assertEqual(batches[4]['start'], expected_start_date + timedelta(days=max_days_per_batch * 4))
        self.assertEqual(batches[4]['end'], mock_now) # Final batch ends at 'now'

    def test_date_range_mode_even_split(self):
        """
        Tests date range mode where the total days are an even multiple of the batch size.
        Input: interval=5 (15-day batches), range='2025-06-01' to '2025-07-16' (45 days)
        Expected: 3 batches of exactly 15 days each.
        """
        interval = 5
        start_str = '2025-06-01 00:00'
        end_str = '2025-07-16 00:00' # This is a 45-day range
        
        batches = create_batches(interval_minutes=interval, start_date_str=start_str, end_date_str=end_str)
        
        self.assertEqual(len(batches), 3) # 45 days / 15 days_per_batch = 3
        
        start_dt = validate_datetime_format(start_str)
        self.assertEqual(batches[0]['start'], start_dt)
        self.assertEqual(batches[0]['end'], start_dt + timedelta(days=15))
        self.assertEqual(batches[1]['end'], start_dt + timedelta(days=30))
        self.assertEqual(batches[2]['end'], start_dt + timedelta(days=45))

    def test_range_smaller_than_batch_size(self):
        """Tests when the requested range is smaller than a single batch, expecting one batch."""
        batches = create_batches(interval_minutes=30, lookback_days=10) # 30-day batch limit
        self.assertEqual(len(batches), 1)
        self.assertEqual((batches[0]['end'] - batches[0]['start']).days, 10)

    def test_invalid_parameters_return_empty_list_and_prints_error(self):
        """
        Ensures that if validate_parameters fails, create_batches returns an empty list
        and prints the validation error.
        """
        # Using mutually exclusive parameters
        with patch('sys.stdout', new=StringIO()) as fake_out:
            batches = create_batches(
                interval_minutes=60, 
                lookback_days=10, 
                start_date_str='2025-01-01 00:00'
            )
            self.assertEqual(batches, [])
            output = fake_out.getvalue().strip()
            self.assertIn("Validation failed", output)
            self.assertIn("Provide either lookback_days or both start_date and end_date, but not both.", output)

    def test_lookback_exceeds_limit_returns_empty(self):
        """Ensures an empty list is returned if lookback exceeds the API limit."""
        interval = 60 # Max lookback is 80 days
        with patch('sys.stdout', new=StringIO()) as fake_out:
            batches = create_batches(interval_minutes=interval, lookback_days=90)
            self.assertEqual(batches, [])
            self.assertIn("exceeds the maximum allowed", fake_out.getvalue())

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

