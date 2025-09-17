"""Tests for Jupyter notebook models."""

import pytest
import uuid
from unittest.mock import Mock
import nbformat

from src.javanotebook.nb_models import (
    JupyterCell, JupyterMarkdownCell, JupyterCodeCell, JupyterRawCell,
    JupyterNotebook, JupyterExecutionRequest, JupyterExecutionResult,
    JupyterStream, JupyterError, JupyterExecuteResult,
    JupyterNotebookInfo
)


class TestJupyterCell:
    """Test JupyterCell base model."""

    def test_cell_id_generation(self):
        """Test automatic cell ID generation."""
        cell = JupyterMarkdownCell(source="Test markdown")
        assert cell.id is not None
        assert len(cell.id) == 8  # UUID truncated to 8 chars
        assert cell.id.replace('-', '').replace('_', '').isalnum()

    def test_cell_id_validation(self):
        """Test cell ID validation rules."""
        # Valid ID
        cell = JupyterMarkdownCell(id="test-123", source="Test")
        assert cell.id == "test-123"

        # Invalid IDs
        with pytest.raises(ValueError, match="Cell ID must be 1-64 characters"):
            JupyterMarkdownCell(id="", source="Test")

        with pytest.raises(ValueError, match="Cell ID must be 1-64 characters"):
            JupyterMarkdownCell(id="x" * 65, source="Test")

        with pytest.raises(ValueError, match="alphanumeric"):
            JupyterMarkdownCell(id="test@123", source="Test")

    def test_source_normalization(self):
        """Test source content normalization."""
        # Single line string
        cell = JupyterMarkdownCell(source="Single line")
        assert cell.source == ["Single line"]

        # Multi-line string
        cell = JupyterMarkdownCell(source="Line 1\nLine 2\n")
        assert cell.source == ["Line 1\n", "Line 2\n"]

        # Already a list
        cell = JupyterMarkdownCell(source=["Line 1", "Line 2"])
        assert cell.source == ["Line 1", "Line 2"]


class TestJupyterNotebook:
    """Test JupyterNotebook model."""

    def test_default_notebook_creation(self):
        """Test creating empty notebook with defaults."""
        notebook = JupyterNotebook()

        assert notebook.nbformat == 4
        assert notebook.nbformat_minor == 5
        assert notebook.cells == []
        assert "kernelspec" in notebook.metadata
        assert "language_info" in notebook.metadata
        assert notebook.metadata["kernelspec"]["name"] == "java"

    def test_notebook_with_cells(self):
        """Test notebook with various cell types."""
        markdown_cell = JupyterMarkdownCell(source="# Title")
        code_cell = JupyterCodeCell(source="System.out.println(\"Hello\");")
        raw_cell = JupyterRawCell(source="Raw content")

        notebook = JupyterNotebook(cells=[markdown_cell, code_cell, raw_cell])

        assert len(notebook.cells) == 3
        assert len(notebook.markdown_cells) == 1
        assert len(notebook.code_cells) == 1
        assert len(notebook.raw_cells) == 1

    def test_to_notebook_node_conversion(self):
        """Test conversion to nbformat NotebookNode."""
        markdown_cell = JupyterMarkdownCell(id="md1", source="# Test")
        code_cell = JupyterCodeCell(
            id="code1",
            source="System.out.println(\"test\");",
            execution_count=1
        )

        notebook = JupyterNotebook(cells=[markdown_cell, code_cell])
        nb_node = notebook.to_notebook_node()

        assert isinstance(nb_node, nbformat.NotebookNode)
        assert nb_node.nbformat == 4
        assert len(nb_node.cells) == 2

        # Check markdown cell
        md_cell = nb_node.cells[0]
        assert md_cell.cell_type == "markdown"
        assert md_cell.id == "md1"
        assert md_cell.source == "# Test"

        # Check code cell
        code_cell_node = nb_node.cells[1]
        assert code_cell_node.cell_type == "code"
        assert code_cell_node.id == "code1"
        assert code_cell_node.execution_count == 1

    def test_from_notebook_node_conversion(self):
        """Test creation from nbformat NotebookNode."""
        # Create a mock NotebookNode
        nb_node = nbformat.v4.new_notebook()
        nb_node.cells = [
            nbformat.v4.new_markdown_cell("# Title", id="md1"),
            nbformat.v4.new_code_cell("print('hello')", id="code1")
        ]

        notebook = JupyterNotebook.from_notebook_node(nb_node)

        assert isinstance(notebook, JupyterNotebook)
        assert len(notebook.cells) == 2
        assert notebook.cells[0].id == "md1"
        assert notebook.cells[1].id == "code1"


class TestJupyterOutputs:
    """Test Jupyter output models."""

    def test_stream_output(self):
        """Test stream output creation."""
        output = JupyterStream(name="stdout", text="Hello World\n")

        assert output.output_type == "stream"
        assert output.name == "stdout"
        assert output.text == "Hello World\n"

    def test_error_output(self):
        """Test error output creation."""
        traceback = ["CompilationError", "Missing semicolon"]
        output = JupyterError(
            ename="CompilationError",
            evalue="Missing semicolon at line 5",
            traceback=traceback
        )

        assert output.output_type == "error"
        assert output.ename == "CompilationError"
        assert output.evalue == "Missing semicolon at line 5"
        assert output.traceback == traceback

    def test_execute_result_output(self):
        """Test execute result output creation."""
        output = JupyterExecuteResult(
            execution_count=1,
            data={"text/plain": "Result"}
        )

        assert output.output_type == "execute_result"
        assert output.execution_count == 1
        assert output.data == {"text/plain": "Result"}


class TestJupyterExecutionModels:
    """Test execution-related models."""

    def test_execution_request(self):
        """Test execution request model."""
        request = JupyterExecutionRequest(
            code="System.out.println(\"test\");",
            cell_id="test-cell",
            execution_count=5
        )

        assert request.code == "System.out.println(\"test\");"
        assert request.cell_id == "test-cell"
        assert request.execution_count == 5

    def test_execution_result(self):
        """Test execution result model."""
        outputs = [
            JupyterStream(name="stdout", text="Hello\n"),
            JupyterStream(name="stderr", text="Warning\n")
        ]

        result = JupyterExecutionResult(
            success=True,
            execution_count=1,
            outputs=outputs,
            execution_time=0.5
        )

        assert result.success is True
        assert result.execution_count == 1
        assert len(result.outputs) == 2
        assert result.execution_time == 0.5


class TestJupyterNotebookInfo:
    """Test notebook info model."""

    def test_notebook_info_creation(self):
        """Test notebook info model creation."""
        info = JupyterNotebookInfo(
            filename="test.ipynb",
            title="Test Notebook",
            total_cells=10,
            code_cells_count=5,
            markdown_cells_count=4,
            raw_cells_count=1,
            nbformat_version="4.5",
            kernel_name="java",
            language="java"
        )

        assert info.filename == "test.ipynb"
        assert info.title == "Test Notebook"
        assert info.total_cells == 10
        assert info.code_cells_count == 5
        assert info.markdown_cells_count == 4
        assert info.raw_cells_count == 1
        assert info.nbformat_version == "4.5"
        assert info.kernel_name == "java"
        assert info.language == "java"

    def test_notebook_info_optional_fields(self):
        """Test notebook info with optional fields."""
        info = JupyterNotebookInfo(
            filename="test.ipynb",
            total_cells=5,
            code_cells_count=3,
            markdown_cells_count=2,
            raw_cells_count=0,
            nbformat_version="4.5"
        )

        assert info.title is None
        assert info.kernel_name is None
        assert info.language is None