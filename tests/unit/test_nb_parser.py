"""Tests for Jupyter notebook parser."""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch
import nbformat

from src.javanotebook.nb_parser import JupyterNotebookParser
from src.javanotebook.nb_models import JupyterNotebook, JupyterCodeCell, JupyterMarkdownCell
from src.javanotebook.exceptions import ParseError


class TestJupyterNotebookParser:
    """Test JupyterNotebookParser functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = JupyterNotebookParser()

    def test_parse_valid_notebook_file(self):
        """Test parsing a valid Jupyter notebook file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            notebook_file = Path(temp_dir) / "test.ipynb"

            # Create valid notebook content
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
                        "source": ["System.out.println(\"Hello\");"]
                    }
                ]
            }

            notebook_file.write_text(json.dumps(notebook_content))

            notebook = self.parser.parse_file(str(notebook_file))

            assert isinstance(notebook, JupyterNotebook)
            assert notebook.nbformat == 4
            assert notebook.nbformat_minor == 5
            assert len(notebook.cells) == 2
            assert len(notebook.markdown_cells) == 1
            assert len(notebook.code_cells) == 1

    def test_parse_file_not_found(self):
        """Test parsing non-existent file."""
        with pytest.raises(ParseError, match="Notebook file not found"):
            self.parser.parse_file("non_existent.ipynb")

    def test_parse_invalid_json(self):
        """Test parsing file with invalid JSON."""
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_file = Path(temp_dir) / "invalid.ipynb"
            invalid_file.write_text("{invalid json content")

            with pytest.raises(ParseError, match="Error parsing notebook"):
                self.parser.parse_file(str(invalid_file))

    def test_save_notebook(self):
        """Test saving notebook to file."""
        # Create a test notebook
        notebook = JupyterNotebook()
        notebook.cells = [
            JupyterMarkdownCell(id="md1", source="# Title"),
            JupyterCodeCell(id="code1", source="System.out.println(\"test\");")
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "output.ipynb"

            self.parser.save_notebook(notebook, str(output_file))

            # Verify file was created and is valid
            assert output_file.exists()

            # Parse it back to verify
            parsed_notebook = self.parser.parse_file(str(output_file))
            assert len(parsed_notebook.cells) == 2
            assert parsed_notebook.cells[0].id == "md1"
            assert parsed_notebook.cells[1].id == "code1"

    def test_create_empty_notebook(self):
        """Test creating empty notebook."""
        notebook = self.parser.create_empty_notebook()

        assert isinstance(notebook, JupyterNotebook)
        assert notebook.nbformat == 4
        assert len(notebook.cells) == 0
        assert "kernelspec" in notebook.metadata
        assert notebook.metadata["kernelspec"]["name"] == "java"

    def test_add_code_cell(self):
        """Test adding code cell to notebook."""
        notebook = self.parser.create_empty_notebook()
        java_code = "System.out.println(\"Hello, World!\");"

        cell = self.parser.add_code_cell(notebook, java_code, "test-cell")

        assert len(notebook.cells) == 1
        assert isinstance(cell, JupyterCodeCell)
        assert cell.id == "test-cell"
        assert cell.source == java_code
        assert cell.metadata.get("language") == "java"

    def test_add_markdown_cell(self):
        """Test adding markdown cell to notebook."""
        notebook = self.parser.create_empty_notebook()
        markdown_content = "# Test Title\n\nSome content."

        cell = self.parser.add_markdown_cell(notebook, markdown_content, "md-cell")

        assert len(notebook.cells) == 1
        assert isinstance(cell, JupyterMarkdownCell)
        assert cell.id == "md-cell"
        assert cell.source == markdown_content

    def test_extract_class_name_public_class(self):
        """Test extracting class name from Java code with public class."""
        java_code = """
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}
"""
        class_name = self.parser.extract_class_name(java_code)
        assert class_name == "HelloWorld"

    def test_extract_class_name_regular_class(self):
        """Test extracting class name from Java code with regular class."""
        java_code = """
class SimpleClass {
    void method() {
        // some code
    }
}
"""
        class_name = self.parser.extract_class_name(java_code)
        assert class_name == "SimpleClass"

    def test_extract_class_name_no_class(self):
        """Test extracting class name when no class is found."""
        java_code = "System.out.println(\"Hello\");"

        with pytest.raises(ParseError, match="No class declaration found"):
            self.parser.extract_class_name(java_code)

    def test_has_main_method_true(self):
        """Test detecting main method when present."""
        java_code = """
public class Test {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}
"""
        assert self.parser.has_main_method(java_code) is True

    def test_has_main_method_false(self):
        """Test detecting main method when absent."""
        java_code = """
public class Test {
    public void someMethod() {
        System.out.println("Hello");
    }
}
"""
        assert self.parser.has_main_method(java_code) is False

    def test_wrap_code_with_main(self):
        """Test wrapping simple code with main method."""
        simple_code = "System.out.println(\"Hello\");"

        wrapped_code = self.parser.wrap_code_with_main(simple_code)

        assert "public class Main" in wrapped_code
        assert "public static void main" in wrapped_code
        assert simple_code in wrapped_code

    def test_wrap_code_with_main_already_has_main(self):
        """Test wrapping code that already has main method."""
        code_with_main = """
public class Test {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}
"""
        wrapped_code = self.parser.wrap_code_with_main(code_with_main)
        assert wrapped_code == code_with_main

    def test_validate_java_code_valid_class(self):
        """Test validating valid Java code with class."""
        valid_code = """
public class Test {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}
"""
        assert self.parser.validate_java_code(valid_code) is True

    def test_validate_java_code_simple_statements(self):
        """Test validating simple Java statements."""
        simple_statements = "int x = 10;\nSystem.out.println(x);"
        assert self.parser.validate_java_code(simple_statements) is True

    def test_validate_java_code_invalid(self):
        """Test validating invalid Java code."""
        invalid_code = "interface TestInterface { }"  # Interface without class
        assert self.parser.validate_java_code(invalid_code) is False

    def test_get_notebook_info(self):
        """Test getting notebook information."""
        with tempfile.TemporaryDirectory() as temp_dir:
            notebook_file = Path(temp_dir) / "test_notebook.ipynb"

            notebook_content = {
                "nbformat": 4,
                "nbformat_minor": 5,
                "metadata": {
                    "kernelspec": {"name": "java"},
                    "language_info": {"name": "java"}
                },
                "cells": [
                    {
                        "cell_type": "markdown",
                        "id": "md1",
                        "metadata": {},
                        "source": ["# Test Notebook\n\nDescription here."]
                    },
                    {
                        "cell_type": "code",
                        "id": "code1",
                        "metadata": {},
                        "execution_count": None,
                        "outputs": [],
                        "source": ["System.out.println(\"test\");"]
                    },
                    {
                        "cell_type": "raw",
                        "id": "raw1",
                        "metadata": {},
                        "source": ["Raw content"]
                    }
                ]
            }

            notebook_file.write_text(json.dumps(notebook_content))

            info = self.parser.get_notebook_info(str(notebook_file))

            assert info.filename == "test_notebook.ipynb"
            assert info.title == "Test Notebook"
            assert info.total_cells == 3
            assert info.code_cells_count == 1
            assert info.markdown_cells_count == 1
            assert info.raw_cells_count == 1
            assert info.nbformat_version == "4.5"
            assert info.kernel_name == "java"
            assert info.language == "java"

    def test_convert_from_markdown(self):
        """Test converting markdown content to Jupyter notebook."""
        markdown_content = """# Java Examples

This is an introduction.

```java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

## Another Section

More explanations here.

```java
int x = 10;
int y = 20;
System.out.println(x + y);
```
"""

        notebook = self.parser.convert_from_markdown(markdown_content)

        assert isinstance(notebook, JupyterNotebook)
        assert len(notebook.cells) == 4  # 2 markdown + 2 code cells
        assert len(notebook.markdown_cells) == 2
        assert len(notebook.code_cells) == 2

        # Check first markdown cell
        first_md = notebook.markdown_cells[0]
        assert "# Java Examples" in first_md.source

        # Check first code cell
        first_code = notebook.code_cells[0]
        assert "HelloWorld" in first_code.source

    def test_convert_to_markdown(self):
        """Test converting Jupyter notebook to markdown."""
        notebook = JupyterNotebook()
        notebook.cells = [
            JupyterMarkdownCell(source="# Title\n\nIntroduction"),
            JupyterCodeCell(source="System.out.println(\"Hello\");"),
            JupyterMarkdownCell(source="## Section 2"),
            JupyterCodeCell(source="int x = 10;")
        ]

        markdown_content = self.parser.convert_to_markdown(notebook)

        assert "# Title" in markdown_content
        assert "```java\nSystem.out.println(\"Hello\");\n```" in markdown_content
        assert "## Section 2" in markdown_content
        assert "```java\nint x = 10;\n```" in markdown_content