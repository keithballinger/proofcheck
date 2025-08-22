import unittest
from unittest.mock import patch, MagicMock
import os

# This is a bit of a hack to get the src directory into the python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../proofcheck')))

from src.search import search_mathlib

class TestSearch(unittest.TestCase):

    @patch('src.search.requests.get')
    @patch('src.search.click.echo')
    def test_search_mathlib_success(self, mock_echo, mock_requests_get):
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'hits': [
                {
                    'name': 'Nat.add',
                    'type': 'ℕ → ℕ → ℕ',
                    'doc': 'Addition of natural numbers.'
                }
            ]
        }
        mock_requests_get.return_value = mock_response

        # Act
        search_mathlib("Nat.add")

        # Assert
        mock_requests_get.assert_called_once_with("https://loogle.lean-lang.org/json?q=Nat.add")
        # Check that the output contains the hit's name
        self.assertIn("Nat.add", ' '.join(call[0][0] for call in mock_echo.call_args_list))

    @patch('src.search.requests.get')
    @patch('src.search.click.echo')
    def test_search_mathlib_no_results(self, mock_echo, mock_requests_get):
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {'hits': []}
        mock_requests_get.return_value = mock_response

        # Act
        search_mathlib("nonexistent_term")

        # Assert
        self.assertIn("No results found.", ' '.join(call[0][0] for call in mock_echo.call_args_list))

if __name__ == '__main__':
    unittest.main()
