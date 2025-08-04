import unittest
from unittest.mock import patch, Mock
import os
import sys
# Add the parent directory (project root) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api import call_price_api

class TestCallPriceApi(unittest.TestCase):

    @patch('growwapi.api.requests.get')
    def test_successful_response(self, mock_get):
        # Mock JSON data
        mock_response_data = {
            "candles": [[1754019900000, 630, 630, 625, 629.1, 115278]],
            "meta": {"ticker": "TCS"}
        }

        # Mock requests.get return
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: mock_response_data,
            url="mock_url"
        )
        mock_get.return_value.raise_for_status = Mock()

        result = call_price_api("TCS", 1754019900000, 1754042400000, 5)
        self.assertEqual(result, mock_response_data)
        self.assertIn("candles", result)

    @patch('growwapi.api.requests.get')
    def test_failed_request(self, mock_get):
        mock_get.side_effect = Exception("Connection error")
        result = call_price_api("TCS", 1754019900000, 1754042400000, 5)
        self.assertIsNone(result)

    @patch('growwapi.api.requests.get')
    def test_debug_output_on_success(self, mock_get):
        mock_response_data = {
            "candles": [[1754019900000, 630, 630, 625, 629.1, 115278]],
            "meta": {"ticker": "TCS"}
        }
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: mock_response_data,
            url="mock_url"
        )
        mock_get.return_value.raise_for_status = Mock()

        # Call with debug=True to ensure it prints (no assertion for print here)
        result = call_price_api("TCS", 1754019900000, 1754042400000, 5, debug=True)
        self.assertIsInstance(result, dict)
        self.assertIn("candles", result)

    @patch('growwapi.api.requests.get')
    def test_empty_candles_response(self, mock_get):
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {"candles": []},
            url="mock_url"
        )
        mock_get.return_value.raise_for_status = Mock()

        result = call_price_api("TCS", 1754019900000, 1754042400000, 5)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["candles"], [])

