import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json

# Add the proofcheck directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../proofcheck')))

from src.search import search_mathlib, validate_query, format_search_results

class TestSearch(unittest.TestCase):

    def test_validate_query(self):
        # Test valid queries
        self.assertTrue(validate_query("Nat.add")[0])
        self.assertTrue(validate_query("prime number")[0])
        self.assertTrue(validate_query("∀ x, x + 0 = x")[0])
        
        # Test invalid queries
        self.assertFalse(validate_query("")[0])
        self.assertFalse(validate_query("   ")[0])
        self.assertFalse(validate_query("x" * 501)[0])  # Too long

    @patch('src.search.requests.get')
    @patch('src.search.console')
    def test_search_mathlib_success(self, mock_console, mock_requests_get):
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'hits': [
                {
                    'name': 'Nat.add',
                    'type': 'ℕ → ℕ → ℕ',
                    'module': 'Mathlib.Data.Nat.Basic',
                    'doc': 'Addition of natural numbers.'
                }
            ]
        }
        mock_requests_get.return_value = mock_response

        # Act
        result = search_mathlib("Nat.add")

        # Assert
        self.assertTrue(result)
        mock_requests_get.assert_called_once()
        # Check that URL encoding is applied
        call_args = mock_requests_get.call_args[0][0]
        self.assertIn("Nat.add", call_args)

    @patch('src.search.requests.get')
    @patch('src.search.console')
    def test_search_mathlib_no_results(self, mock_console, mock_requests_get):
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'hits': []}
        mock_requests_get.return_value = mock_response

        # Act
        result = search_mathlib("nonexistent_term")

        # Assert
        self.assertTrue(result)  # Still returns True, just no results

    @patch('src.search.requests.get')
    @patch('src.search.console')
    def test_search_mathlib_timeout(self, mock_console, mock_requests_get):
        # Arrange
        import requests
        mock_requests_get.side_effect = requests.exceptions.Timeout()

        # Act
        result = search_mathlib("test", max_retries=1)

        # Assert
        self.assertFalse(result)

    @patch('src.search.requests.get')
    @patch('src.search.console')
    def test_search_mathlib_connection_error(self, mock_console, mock_requests_get):
        # Arrange
        import requests
        mock_requests_get.side_effect = requests.exceptions.ConnectionError()

        # Act
        result = search_mathlib("test")

        # Assert
        self.assertFalse(result)

    @patch('src.search.requests.get')
    @patch('src.search.console')
    def test_search_mathlib_invalid_json(self, mock_console, mock_requests_get):
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("test", "doc", 0)
        mock_requests_get.return_value = mock_response

        # Act
        result = search_mathlib("test")

        # Assert
        self.assertFalse(result)

    @patch('src.search.requests.get')
    @patch('src.search.console')
    def test_search_mathlib_error_in_response(self, mock_console, mock_requests_get):
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'error': 'Invalid query syntax'}
        mock_requests_get.return_value = mock_response

        # Act
        result = search_mathlib("test")

        # Assert
        self.assertFalse(result)

    def test_search_mathlib_invalid_query(self):
        # Act
        with patch('src.search.console'):
            result = search_mathlib("")

        # Assert
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()