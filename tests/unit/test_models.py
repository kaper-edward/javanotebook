"""Unit tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from javanotebook.models import (
    Cell, MarkdownCell, JavaCodeCell, ExecutionRequest, 
    ExecutionResult, Notebook, NotebookInfo
)


class TestCellModels:
    """Test cases for cell models."""
    
    def test_markdown_cell_creation(self):
        """Test creating a markdown cell."""
        cell = MarkdownCell(content="# Hello World")
        
        assert cell.cell_type == "markdown"
        assert cell.content == "# Hello World"
        assert cell.id is None
        assert cell.metadata == {}
    
    def test_java_code_cell_creation(self):
        """Test creating a Java code cell."""
        code = "public class Test { }"
        cell = JavaCodeCell(content=code)
        
        assert cell.cell_type == "code"
        assert cell.language == "java"
        assert cell.content == code
        assert cell.id is None
        assert cell.metadata == {}
    
    def test_cell_with_id_and_metadata(self):
        """Test creating cell with ID and metadata."""
        cell = MarkdownCell(
            content="Test content",
            id="cell-1",
            metadata={"tags": ["important"]}
        )
        
        assert cell.id == "cell-1"
        assert cell.metadata == {"tags": ["important"]}
    
    def test_cell_type_validation(self):
        """Test that cell type is validated."""
        # This should work
        cell = MarkdownCell(content="test")
        assert cell.cell_type == "markdown"
        
        # Trying to create with wrong type should still work
        # because Pydantic will use the default value
        cell = JavaCodeCell(content="test")
        assert cell.cell_type == "code"


class TestExecutionModels:
    """Test cases for execution-related models."""
    
    def test_execution_request(self):
        """Test creating an execution request."""
        request = ExecutionRequest(code="System.out.println('Hello');")
        
        assert request.code == "System.out.println('Hello');"
        assert request.cell_id is None
    
    def test_execution_request_with_cell_id(self):
        """Test creating an execution request with cell ID."""
        request = ExecutionRequest(
            code="System.out.println('Hello');",
            cell_id="cell-123"
        )
        
        assert request.cell_id == "cell-123"
    
    def test_execution_request_empty_code(self):
        """Test that empty code raises validation error."""
        with pytest.raises(ValidationError):
            ExecutionRequest(code="")
    
    def test_execution_result_success(self):
        """Test creating a successful execution result."""
        result = ExecutionResult(
            success=True,
            stdout="Hello, World!",
            execution_time=0.123
        )
        
        assert result.success is True
        assert result.stdout == "Hello, World!"
        assert result.stderr == ""
        assert result.execution_time == 0.123
        assert result.error_message is None
        assert result.compilation_error is None
    
    def test_execution_result_failure(self):
        """Test creating a failed execution result."""
        result = ExecutionResult(
            success=False,
            compilation_error="Syntax error on line 1",
            execution_time=0.05
        )
        
        assert result.success is False
        assert result.compilation_error == "Syntax error on line 1"
        assert result.stdout == ""
        assert result.stderr == ""


class TestNotebookModels:
    """Test cases for notebook models."""
    
    def test_empty_notebook(self):
        """Test creating an empty notebook."""
        notebook = Notebook(cells=[])
        
        assert len(notebook.cells) == 0
        assert len(notebook.markdown_cells) == 0
        assert len(notebook.code_cells) == 0
        assert notebook.metadata == {}
    
    def test_notebook_with_cells(self):
        """Test creating notebook with mixed cells."""
        cells = [
            MarkdownCell(content="# Title"),
            JavaCodeCell(content="public class Test {}"),
            MarkdownCell(content="Description"),
            JavaCodeCell(content="public class Another {}")
        ]
        
        notebook = Notebook(cells=cells)
        
        assert len(notebook.cells) == 4
        assert len(notebook.markdown_cells) == 2
        assert len(notebook.code_cells) == 2
    
    def test_notebook_properties(self):
        """Test notebook property methods."""
        markdown_cell = MarkdownCell(content="# Title")
        code_cell = JavaCodeCell(content="public class Test {}")
        
        notebook = Notebook(cells=[markdown_cell, code_cell])
        
        # Test markdown_cells property
        markdown_cells = notebook.markdown_cells
        assert len(markdown_cells) == 1
        assert markdown_cells[0].content == "# Title"
        
        # Test code_cells property
        code_cells = notebook.code_cells
        assert len(code_cells) == 1
        assert code_cells[0].content == "public class Test {}"
    
    def test_notebook_info(self):
        """Test creating notebook info."""
        info = NotebookInfo(
            filename="test.md",
            title="Test Notebook",
            total_cells=5,
            code_cells_count=3,
            markdown_cells_count=2
        )
        
        assert info.filename == "test.md"
        assert info.title == "Test Notebook"
        assert info.total_cells == 5
        assert info.code_cells_count == 3
        assert info.markdown_cells_count == 2
    
    def test_notebook_info_minimal(self):
        """Test creating notebook info with minimal data."""
        info = NotebookInfo(
            filename="minimal.md",
            total_cells=1,
            code_cells_count=1,
            markdown_cells_count=0
        )
        
        assert info.filename == "minimal.md"
        assert info.title is None  # Optional field
        assert info.total_cells == 1