import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import subprocess
from pathlib import Path

# Add the proofcheck directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../proofcheck')))

from src.lean import check_file, VerificationResult, check_lean_installation, find_project_root

class TestLean(unittest.TestCase):

    @patch('src.lean.Path.exists')
    @patch('src.lean.find_project_root')
    @patch('src.lean.check_lean_installation')
    @patch('src.lean.subprocess.run')
    def test_check_file_success(self, mock_subprocess_run, mock_check_lean, mock_find_root, mock_exists):
        # Arrange
        mock_exists.return_value = True
        mock_check_lean.return_value = (True, "Lean installed")
        mock_find_root.return_value = "/dummy/project"
        mock_subprocess_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        # Act
        result = check_file("/dummy/project/file.lean")

        # Assert
        self.assertTrue(result.success)
        self.assertIn("successfully", result.message.lower())

    @patch('src.lean.Path.exists')
    @patch('src.lean.find_project_root')
    @patch('src.lean.check_lean_installation')
    @patch('src.lean.subprocess.run')
    def test_check_file_build_failed(self, mock_subprocess_run, mock_check_lean, mock_find_root, mock_exists):
        # Arrange
        mock_exists.return_value = True
        mock_check_lean.return_value = (True, "Lean installed")
        mock_find_root.return_value = "/dummy/project"
        error_output = "file.lean:1:1: error: something went wrong"
        mock_subprocess_run.return_value = MagicMock(returncode=1, stdout="", stderr=error_output)

        # Act
        result = check_file("/dummy/project/file.lean")

        # Assert
        self.assertFalse(result.success)
        self.assertIn("Build failed", result.message)
        self.assertIn(error_output, result.message)

    @patch('src.lean.Path.exists')
    @patch('src.lean.check_lean_installation')
    def test_check_file_lean_not_installed(self, mock_check_lean, mock_exists):
        # Arrange
        mock_exists.return_value = True
        mock_check_lean.return_value = (False, "Lean not found")

        # Act
        result = check_file("/dummy/project/file.lean")

        # Assert
        self.assertFalse(result.success)
        self.assertIn("Lean not found", result.message)
    
    def test_check_file_invalid_path(self):
        # Act
        result = check_file("/nonexistent/file.lean")
        
        # Assert
        self.assertFalse(result.success)
        self.assertIn("not found", result.message.lower())
    
    @patch('src.lean.subprocess.run')
    def test_check_lean_installation_success(self, mock_run):
        # Arrange
        mock_run.return_value = MagicMock(returncode=0)
        
        # Act
        success, message = check_lean_installation()
        
        # Assert
        self.assertTrue(success)
        self.assertEqual(mock_run.call_count, 2)  # Called for lake and lean
    
    @patch('src.lean.subprocess.run')
    def test_check_lean_installation_not_found(self, mock_run):
        # Arrange
        mock_run.side_effect = FileNotFoundError
        
        # Act
        success, message = check_lean_installation()
        
        # Assert
        self.assertFalse(success)
        self.assertIn("not found", message.lower())

if __name__ == '__main__':
    unittest.main()
