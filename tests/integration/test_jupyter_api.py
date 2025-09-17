"""Integration tests for Jupyter API endpoints."""

import pytest
import tempfile
import json
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

from src.javanotebook.main import create_app
from src.javanotebook.format_detector import NotebookFormat


class TestJupyterAPIIntegration:
    """Integration tests for Jupyter API endpoints."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create test notebook file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.notebook_file = Path(self.temp_dir.name) / "test.ipynb"

        notebook_content = {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {
                "kernelspec": {
                    "display_name": "Java",
                    "language": "java",
                    "name": "java"
                }
            },
            "cells": [
                {
                    "cell_type": "markdown",
                    "id": "md1",
                    "metadata": {},
                    "source": ["# Test Notebook"]
                },
                {
                    "cell_type": "code",
                    "id": "code1",
                    "metadata": {"language": "java"},
                    "execution_count": None,
                    "outputs": [],
                    "source": ["System.out.println(\"Hello, World!\");"]
                }
            ]
        }

        self.notebook_file.write_text(json.dumps(notebook_content))

        # Create app with Jupyter format
        self.app = create_app(str(self.notebook_file), NotebookFormat.JUPYTER)
        self.client = TestClient(self.app)

    def teardown_method(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_main_page_jupyter_format(self):
        """Test main page with Jupyter format."""
        response = self.client.get("/")

        assert response.status_code == 200
        assert "test.ipynb" in response.text
        assert "format" in response.text  # Should contain format info

    @patch('src.javanotebook.routers.api.jupyter_executor')
    def test_jupyter_execute_endpoint(self, mock_executor):
        """Test Jupyter execute endpoint."""
        # Mock successful execution
        from src.javanotebook.nb_models import JupyterExecutionResult, JupyterStream

        mock_result = JupyterExecutionResult(
            success=True,
            execution_count=1,
            outputs=[
                JupyterStream(name="stdout", text="Hello, World!\n")
            ],
            execution_time=0.1
        )
        mock_executor.execute_code.return_value = mock_result

        response = self.client.post(
            "/api/v1/jupyter/execute",
            json={
                "code": "System.out.println(\"Hello, World!\");",
                "cell_id": "test-cell"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["execution_count"] == 1
        assert len(data["outputs"]) == 1
        assert data["outputs"][0]["output_type"] == "stream"

    def test_jupyter_notebook_info_endpoint(self):
        """Test Jupyter notebook info endpoint."""
        response = self.client.get(
            f"/api/v1/jupyter/notebook/info?notebook_path={self.notebook_file}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "test.ipynb"
        assert data["total_cells"] == 2
        assert data["code_cells_count"] == 1
        assert data["markdown_cells_count"] == 1
        assert data["nbformat_version"] == "4.5"

    @patch('src.javanotebook.routers.api.jupyter_executor')
    def test_jupyter_validate_endpoint(self, mock_executor):
        """Test Jupyter validate endpoint."""
        response = self.client.post(
            "/api/v1/jupyter/validate",
            json={
                "code": "System.out.println(\"Hello\");"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "valid" in data
        assert "can_auto_wrap" in data
        assert "processed_code" in data

    def test_format_detect_endpoint(self):
        """Test format detection endpoint."""
        response = self.client.get(
            f"/api/v1/format/detect?file_path={self.notebook_file}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["detected_format"] == "ipynb"
        assert "md" in data["supported_formats"]
        assert "ipynb" in data["supported_formats"]

    def test_jupyter_execution_reset_endpoint(self):
        """Test Jupyter execution reset endpoint."""
        response = self.client.get("/api/v1/jupyter/execution/reset")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["execution_count"] == 0

    def test_convert_md_to_ipynb_endpoint(self):
        """Test markdown to Jupyter conversion endpoint."""
        markdown_content = """# Test

```java
System.out.println("Hello");
```
"""

        response = self.client.post(
            "/api/v1/jupyter/convert/md-to-ipynb",
            json=markdown_content,
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["format"] == "ipynb"
        assert data["cells_count"] > 0
        assert "notebook" in data

    def test_convert_ipynb_to_md_endpoint(self):
        """Test Jupyter to markdown conversion endpoint."""
        response = self.client.post(
            f"/api/v1/jupyter/convert/ipynb-to-md?notebook_path={self.notebook_file}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["format"] == "md"
        assert data["cells_count"] == 2
        assert "# Test Notebook" in data["markdown"]
        assert "```java" in data["markdown"]

    @patch('src.javanotebook.routers.api.jupyter_executor')
    def test_jupyter_execute_compilation_error(self, mock_executor):
        """Test Jupyter execute with compilation error."""
        from src.javanotebook.nb_models import JupyterExecutionResult, JupyterError

        mock_result = JupyterExecutionResult(
            success=False,
            execution_count=1,
            outputs=[
                JupyterError(
                    ename="CompilationError",
                    evalue="';' expected",
                    traceback=["Error at line 1", "';' expected"]
                )
            ],
            execution_time=0.1,
            error_message="';' expected"
        )
        mock_executor.execute_code.return_value = mock_result

        response = self.client.post(
            "/api/v1/jupyter/execute",
            json={
                "code": "System.out.println(\"Hello\")",  # Missing semicolon
                "cell_id": "test-cell"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert len(data["outputs"]) == 1
        assert data["outputs"][0]["output_type"] == "error"
        assert data["outputs"][0]["ename"] == "CompilationError"

    def test_jupyter_notebook_info_file_not_found(self):
        """Test notebook info with non-existent file."""
        response = self.client.get(
            "/api/v1/jupyter/notebook/info?notebook_path=non_existent.ipynb"
        )

        assert response.status_code == 400
        assert "Failed to get notebook info" in response.json()["detail"]

    def test_format_detect_file_not_found(self):
        """Test format detection with non-existent file."""
        response = self.client.get(
            "/api/v1/format/detect?file_path=non_existent.file"
        )

        assert response.status_code == 400
        assert "Format detection failed" in response.json()["detail"]

    def test_health_endpoint_with_jupyter(self):
        """Test health endpoint returns Java availability."""
        with patch('src.javanotebook.routers.api.executor') as mock_executor:
            mock_executor._verify_java_installation.return_value = None

            response = self.client.get("/api/v1/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["java_available"] is True


class TestJupyterAPIWithMockJava:
    """Test Jupyter API with mocked Java environment."""

    def setup_method(self):
        """Set up test fixtures with mocked Java."""
        with patch('subprocess.run') as mock_run:
            # Mock Java verification
            mock_run.return_value = Mock(returncode=0)

            # Create simple test app
            self.app = create_app()
            self.client = TestClient(self.app)

    @patch('src.javanotebook.routers.api.jupyter_executor')
    def test_jupyter_execute_with_auto_wrap(self, mock_executor):
        """Test Jupyter execution with auto-wrapping."""
        from src.javanotebook.nb_models import JupyterExecutionResult, JupyterStream

        mock_result = JupyterExecutionResult(
            success=True,
            execution_count=1,
            outputs=[
                JupyterStream(name="stdout", text="Hello from simple code!\n30\n")
            ],
            execution_time=0.1
        )
        mock_executor.execute_code.return_value = mock_result

        # Test simple code that should be auto-wrapped
        response = self.client.post(
            "/api/v1/jupyter/execute",
            json={
                "code": "System.out.println(\"Hello from simple code!\");\nint x = 10;\nint y = 20;\nSystem.out.println(x + y);",
                "cell_id": "simple-cell"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_jupyter_validate_auto_wrap_detection(self):
        """Test validation with auto-wrap detection."""
        response = self.client.post(
            "/api/v1/jupyter/validate",
            json={
                "code": "int x = 10;\nSystem.out.println(x);"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["can_auto_wrap"] is True
        assert "public class Main" in data["processed_code"]