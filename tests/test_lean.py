import unittest
from unittest.mock import patch, MagicMock
import os
import subprocess

# This is a bit of a hack to get the src directory into the python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../proofcheck')))

from src.lean import check_file, VerificationResult

class TestLean(unittest.TestCase):

    @patch('src.lean.subprocess.run')
    def test_check_file_success(self, mock_subprocess_run):
        # Arrange
        mock_subprocess_run.return_value = MagicMock(check=True, stderr="")

        # Act
        result = check_file("dummy/path/file.lean")

        # Assert
        self.assertTrue(result.success)
        self.assertEqual(result.message, "✓ Proof verified successfully!")

    @patch('src.lean.subprocess.run')
    def test_check_file_proof_failed(self, mock_subprocess_run):
        # Arrange
        error_output = "file.lean:1:1: error: something went wrong"
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(1, ["lean"], stderr=error_output)

        # Act
        result = check_file("dummy/path/file.lean")

        # Assert
        self.assertFalse(result.success)
        self.assertIn("✗ Proof failed:", result.message)
        self.assertIn(error_output, result.message)

    @patch('src.lean.subprocess.run')
    def test_check_file_lean_not_found(self, mock_subprocess_run):
        # Arrange
        mock_subprocess_run.side_effect = FileNotFoundError

        # Act
        result = check_file("dummy/path/file.lean")

        # Assert
        self.assertFalse(result.success)
        self.assertIn("Error: `lean` command not found.", result.message)

if __name__ == '__main__':
    unittest.main()
