import unittest
from unittest.mock import patch, MagicMock
import os
import shutil

# This is a bit of a hack to get the src directory into the python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../proofcheck')))

from src.project import create_project

class TestProject(unittest.TestCase):

    def tearDown(self):
        # Clean up any created directories
        if os.path.exists("test_project_dir"):
            shutil.rmtree("test_project_dir")

    @patch('src.project.subprocess.run')
    @patch('src.project.click.echo')
    def test_create_project_success(self, mock_echo, mock_subprocess_run):
        # Arrange
        mock_subprocess_run.return_value = MagicMock(check=True)

        # Act
        create_project("test_project_dir")

        # Assert
        mock_subprocess_run.assert_called_once_with(
            ["lake", "init", "test_project_dir", "math"], 
            check=True, 
            capture_output=True, 
            text=True
        )
        # Check that success messages are printed
        self.assertIn("Successfully created project 'test_project_dir'.", ' '.join(call[0][0] for call in mock_echo.call_args_list))

    @patch('src.project.subprocess.run')
    @patch('src.project.click.echo')
    def test_create_project_lake_not_found(self, mock_echo, mock_subprocess_run):
        # Arrange
        mock_subprocess_run.side_effect = FileNotFoundError

        # Act
        create_project("test_project_dir")

        # Assert
        self.assertIn("Error: `lake` command not found.", ' '.join(call[0][0] for call in mock_echo.call_args_list if call.kwargs.get('err')))

    @patch('src.project.os.path.exists')
    @patch('src.project.click.echo')
    def test_create_project_dir_exists(self, mock_echo, mock_path_exists):
        # Arrange
        mock_path_exists.return_value = True

        # Act
        create_project("test_project_dir")

        # Assert
        self.assertIn("Error: Directory 'test_project_dir' already exists.", ' '.join(call[0][0] for call in mock_echo.call_args_list if call.kwargs.get('err')))

if __name__ == '__main__':
    unittest.main()
