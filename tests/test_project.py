import unittest
from unittest.mock import patch, MagicMock, call
import os
import sys
import shutil
from pathlib import Path

# Add the proofcheck directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../proofcheck')))

from src.project import create_project, check_lean_installation, validate_project_name

class TestProject(unittest.TestCase):

    def tearDown(self):
        # Clean up any created directories
        test_dirs = ["test_project_dir", "valid_project", "TestProject"]
        for dir_name in test_dirs:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)

    def test_validate_project_name(self):
        # Test valid names
        self.assertTrue(validate_project_name("myproject")[0])
        self.assertTrue(validate_project_name("my_project")[0])
        self.assertTrue(validate_project_name("Project123")[0])
        self.assertTrue(validate_project_name("_private")[0])
        
        # Test invalid names
        self.assertFalse(validate_project_name("")[0])
        self.assertFalse(validate_project_name("my project")[0])  # space
        self.assertFalse(validate_project_name("my/project")[0])  # slash
        self.assertFalse(validate_project_name("123project")[0])  # starts with number
        self.assertFalse(validate_project_name("my:project")[0])  # colon

    @patch('src.project.subprocess.run')
    @patch('src.project.Path.mkdir')
    @patch('src.project.Path.exists')
    @patch('src.project.check_lean_installation')
    def test_create_project_success(self, mock_check_lean, mock_exists, mock_mkdir, mock_subprocess_run):
        # Arrange
        mock_check_lean.return_value = (True, "Lean installed")
        mock_exists.return_value = False
        mock_subprocess_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        # Mock the file write
        with patch('src.project.Path.write_text'):
            # Act
            result = create_project("test_project_dir")

        # Assert
        self.assertTrue(result)
        mock_subprocess_run.assert_called_once()
        
    @patch('src.project.check_lean_installation')
    @patch('src.project.Path.exists')
    def test_create_project_lean_not_installed(self, mock_exists, mock_check_lean):
        # Arrange
        mock_exists.return_value = False
        mock_check_lean.return_value = (False, "Lean not found")

        # Act
        result = create_project("test_project_dir")

        # Assert
        self.assertFalse(result)

    @patch('src.project.Path.exists')
    def test_create_project_dir_exists(self, mock_exists):
        # Arrange
        mock_exists.return_value = True

        # Act
        result = create_project("test_project_dir")

        # Assert
        self.assertFalse(result)

    def test_create_project_invalid_name(self):
        # Act
        result = create_project("invalid/name")

        # Assert
        self.assertFalse(result)

    @patch('src.project.subprocess.run')
    def test_check_lean_installation_success(self, mock_run):
        # Arrange
        mock_run.return_value = MagicMock(returncode=0)
        
        # Act
        success, message = check_lean_installation()
        
        # Assert
        self.assertTrue(success)
        mock_run.assert_called_once()
        
    @patch('src.project.subprocess.run')
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