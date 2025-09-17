"""Tests for format detector."""

import pytest
import tempfile
import json
from pathlib import Path

from src.javanotebook.format_detector import FormatDetector, NotebookFormat
from src.javanotebook.exceptions import ParseError


class TestFormatDetector:
    """Test FormatDetector functionality."""

    def test_detect_format_by_extension(self):
        """Test format detection by file extension."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test .md file
            md_file = Path(temp_dir) / "test.md"
            md_file.write_text("# Test markdown\n\n```java\nSystem.out.println(\"test\");\n```")

            assert FormatDetector.detect_format(str(md_file)) == NotebookFormat.MARKDOWN

            # Test .ipynb file
            ipynb_file = Path(temp_dir) / "test.ipynb"
            notebook_content = {
                "nbformat": 4,
                "nbformat_minor": 5,
                "metadata": {},
                "cells": []
            }
            ipynb_file.write_text(json.dumps(notebook_content))

            assert FormatDetector.detect_format(str(ipynb_file)) == NotebookFormat.JUPYTER

    def test_detect_format_by_content_jupyter(self):
        """Test Jupyter format detection by content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Valid Jupyter notebook content
            notebook_file = Path(temp_dir) / "notebook.json"
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
                        "id": "test",
                        "metadata": {},
                        "source": ["# Test"]
                    }
                ]
            }
            notebook_file.write_text(json.dumps(notebook_content, indent=2))

            assert FormatDetector.detect_format(str(notebook_file)) == NotebookFormat.JUPYTER

    def test_detect_format_by_content_markdown(self):
        """Test markdown format detection by content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Valid markdown content
            md_file = Path(temp_dir) / "document.txt"
            md_content = """# Java Programming Examples

This is a markdown document with Java code blocks.

```java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

## Another section

More content here.

```java
int x = 10;
int y = 20;
System.out.println(x + y);
```
"""
            md_file.write_text(md_content)

            assert FormatDetector.detect_format(str(md_file)) == NotebookFormat.MARKDOWN

    def test_detect_format_file_not_found(self):
        """Test format detection with non-existent file."""
        with pytest.raises(ParseError, match="File not found"):
            FormatDetector.detect_format("non_existent_file.md")

    def test_detect_format_empty_file(self):
        """Test format detection with empty file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            empty_file = Path(temp_dir) / "empty.txt"
            empty_file.write_text("")

            with pytest.raises(ParseError, match="Empty file"):
                FormatDetector.detect_format(str(empty_file))

    def test_detect_format_ambiguous_content(self):
        """Test format detection with ambiguous content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            ambiguous_file = Path(temp_dir) / "ambiguous.txt"
            ambiguous_file.write_text("This is just plain text without clear format indicators.")

            with pytest.raises(ParseError, match="Cannot determine format"):
                FormatDetector.detect_format(str(ambiguous_file))

    def test_is_jupyter_notebook_valid(self):
        """Test Jupyter notebook validation."""
        # Valid notebook
        valid_notebook = {
            "nbformat": 4,
            "nbformat_minor": 5,
            "cells": [
                {"cell_type": "markdown", "source": "test"}
            ]
        }
        assert FormatDetector._is_jupyter_notebook(valid_notebook) is True

        # Empty notebook (still valid)
        empty_notebook = {
            "nbformat": 4,
            "cells": []
        }
        assert FormatDetector._is_jupyter_notebook(empty_notebook) is True

    def test_is_jupyter_notebook_invalid(self):
        """Test invalid Jupyter notebook detection."""
        # Missing required fields
        invalid_notebook = {
            "nbformat": 4
            # Missing cells
        }
        assert FormatDetector._is_jupyter_notebook(invalid_notebook) is False

        # Invalid nbformat
        invalid_format = {
            "nbformat": "4",  # Should be int
            "cells": []
        }
        assert FormatDetector._is_jupyter_notebook(invalid_format) is False

        # Invalid cells structure
        invalid_cells = {
            "nbformat": 4,
            "cells": "not a list"
        }
        assert FormatDetector._is_jupyter_notebook(invalid_cells) is False

    def test_is_markdown_notebook(self):
        """Test markdown notebook detection."""
        # Content with Java code blocks
        java_markdown = """# Title

```java
System.out.println("test");
```

More content.
"""
        assert FormatDetector._is_markdown_notebook(java_markdown) is True

        # Content with markdown headers
        header_markdown = """# Main Title

## Subtitle

Regular content here.
"""
        assert FormatDetector._is_markdown_notebook(header_markdown) is True

        # Plain text without markdown indicators
        plain_text = "This is just plain text without any markdown features."
        assert FormatDetector._is_markdown_notebook(plain_text) is False

    def test_get_appropriate_parser(self):
        """Test getting appropriate parser for file format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            md_file = Path(temp_dir) / "test.md"
            md_file.write_text("# Test\n\n```java\nSystem.out.println(\"test\");\n```")

            ipynb_file = Path(temp_dir) / "test.ipynb"
            notebook_content = {"nbformat": 4, "cells": []}
            ipynb_file.write_text(json.dumps(notebook_content))

            # Test auto-detection
            from src.javanotebook.parser import NotebookParser
            from src.javanotebook.nb_parser import JupyterNotebookParser

            parser_class, format_type = FormatDetector.get_appropriate_parser(str(md_file))
            assert parser_class == NotebookParser
            assert format_type == NotebookFormat.MARKDOWN

            parser_class, format_type = FormatDetector.get_appropriate_parser(str(ipynb_file))
            assert parser_class == JupyterNotebookParser
            assert format_type == NotebookFormat.JUPYTER

            # Test explicit format hints
            parser_class, format_type = FormatDetector.get_appropriate_parser(str(md_file), "md")
            assert parser_class == NotebookParser
            assert format_type == NotebookFormat.MARKDOWN

            parser_class, format_type = FormatDetector.get_appropriate_parser(str(ipynb_file), "ipynb")
            assert parser_class == JupyterNotebookParser
            assert format_type == NotebookFormat.JUPYTER

    def test_get_appropriate_parser_invalid_hint(self):
        """Test getting parser with invalid format hint."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.md"
            test_file.write_text("# Test")

            with pytest.raises(ParseError, match="Unsupported format hint"):
                FormatDetector.get_appropriate_parser(str(test_file), "invalid")

    def test_validate_format_consistency(self):
        """Test format consistency validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create markdown file
            md_file = Path(temp_dir) / "test.md"
            md_file.write_text("# Test\n\n```java\ncode\n```")

            # Should match markdown format
            assert FormatDetector.validate_format_consistency(
                str(md_file), NotebookFormat.MARKDOWN
            ) is True

            # Should not match Jupyter format
            assert FormatDetector.validate_format_consistency(
                str(md_file), NotebookFormat.JUPYTER
            ) is False

    def test_suggest_output_format(self):
        """Test output format suggestion."""
        # Based on output path extension
        assert FormatDetector.suggest_output_format(
            NotebookFormat.MARKDOWN, "output.ipynb"
        ) == NotebookFormat.JUPYTER

        assert FormatDetector.suggest_output_format(
            NotebookFormat.JUPYTER, "output.md"
        ) == NotebookFormat.MARKDOWN

        # Default to input format when no output path
        assert FormatDetector.suggest_output_format(
            NotebookFormat.MARKDOWN, None
        ) == NotebookFormat.MARKDOWN

        # Invalid output path, default to input format
        assert FormatDetector.suggest_output_format(
            NotebookFormat.JUPYTER, "invalid_extension.xyz"
        ) == NotebookFormat.JUPYTER