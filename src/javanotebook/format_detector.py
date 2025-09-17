"""File format detection for notebook files."""

import json
from pathlib import Path
from typing import Literal, Optional
from enum import Enum

from .exceptions import ParseError


class NotebookFormat(str, Enum):
    """Supported notebook formats."""

    MARKDOWN = "md"
    JUPYTER = "ipynb"
    AUTO = "auto"


class FormatDetector:
    """Detector for notebook file formats."""

    @staticmethod
    def detect_format(file_path: str) -> NotebookFormat:
        """
        Detect notebook format based on file extension and content.

        Args:
            file_path: Path to the notebook file

        Returns:
            Detected format (MARKDOWN or JUPYTER)

        Raises:
            ParseError: If format cannot be determined
        """
        path = Path(file_path)

        if not path.exists():
            raise ParseError(f"File not found: {file_path}")

        # AIDEV-NOTE: Check file extension first
        extension = path.suffix.lower()

        if extension == ".md":
            return NotebookFormat.MARKDOWN
        elif extension == ".ipynb":
            return NotebookFormat.JUPYTER

        # AIDEV-NOTE: If extension is ambiguous, check content
        return FormatDetector._detect_by_content(file_path)

    @staticmethod
    def _detect_by_content(file_path: str) -> NotebookFormat:
        """
        Detect format by analyzing file content.

        Args:
            file_path: Path to the notebook file

        Returns:
            Detected format based on content analysis

        Raises:
            ParseError: If content cannot be parsed or format is unclear
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
        except (IOError, UnicodeDecodeError) as e:
            raise ParseError(f"Cannot read file {file_path}: {str(e)}")

        if not content:
            raise ParseError(f"Empty file: {file_path}")

        # AIDEV-NOTE: Try to parse as JSON (Jupyter notebook)
        if content.startswith('{'):
            try:
                data = json.loads(content)
                if FormatDetector._is_jupyter_notebook(data):
                    return NotebookFormat.JUPYTER
            except json.JSONDecodeError:
                pass

        # AIDEV-NOTE: Check for markdown patterns
        if FormatDetector._is_markdown_notebook(content):
            return NotebookFormat.MARKDOWN

        raise ParseError(f"Cannot determine format of file: {file_path}")

    @staticmethod
    def _is_jupyter_notebook(data: dict) -> bool:
        """
        Check if JSON data represents a Jupyter notebook.

        Args:
            data: Parsed JSON data

        Returns:
            True if data looks like a Jupyter notebook
        """
        required_fields = ['nbformat', 'cells']

        # AIDEV-NOTE: Check for required Jupyter notebook fields
        if not all(field in data for field in required_fields):
            return False

        # AIDEV-NOTE: Check nbformat version
        if not isinstance(data.get('nbformat'), int):
            return False

        # AIDEV-NOTE: Check cells structure
        cells = data.get('cells', [])
        if not isinstance(cells, list):
            return False

        # AIDEV-NOTE: Validate at least one cell has proper structure
        for cell in cells:
            if not isinstance(cell, dict):
                continue
            if 'cell_type' not in cell:
                continue
            if cell['cell_type'] in ['code', 'markdown', 'raw']:
                return True

        return len(cells) == 0  # Empty notebook is still valid

    @staticmethod
    def _is_markdown_notebook(content: str) -> bool:
        """
        Check if content looks like a markdown notebook.

        Args:
            content: File content as string

        Returns:
            True if content looks like markdown with Java code blocks
        """
        # AIDEV-NOTE: Look for Java code blocks in markdown
        java_patterns = [
            '```java',
            '```Java',
            '```JAVA'
        ]

        # AIDEV-NOTE: Check for markdown headers
        has_markdown_headers = any(
            line.strip().startswith('#')
            for line in content.splitlines()
        )

        # AIDEV-NOTE: Check for Java code blocks
        has_java_blocks = any(
            pattern in content
            for pattern in java_patterns
        )

        # AIDEV-NOTE: If it has Java blocks, it's likely our markdown format
        if has_java_blocks:
            return True

        # AIDEV-NOTE: If it has markdown headers but no Java, might still be markdown
        if has_markdown_headers:
            return True

        return False

    @staticmethod
    def get_appropriate_parser(file_path: str, format_hint: Optional[str] = None):
        """
        Get appropriate parser for the given file.

        Args:
            file_path: Path to the notebook file
            format_hint: Optional format hint ('md', 'ipynb', or 'auto')

        Returns:
            Tuple of (parser_class, format) where parser_class is the appropriate
            parser class and format is the detected/specified format

        Raises:
            ParseError: If format cannot be determined or is unsupported
        """
        from .parser import NotebookParser
        from .nb_parser import JupyterNotebookParser

        # AIDEV-NOTE: Handle explicit format specification
        if format_hint and format_hint != "auto":
            if format_hint == "md":
                return NotebookParser, NotebookFormat.MARKDOWN
            elif format_hint == "ipynb":
                return JupyterNotebookParser, NotebookFormat.JUPYTER
            else:
                raise ParseError(f"Unsupported format hint: {format_hint}")

        # AIDEV-NOTE: Auto-detect format
        detected_format = FormatDetector.detect_format(file_path)

        if detected_format == NotebookFormat.MARKDOWN:
            return NotebookParser, detected_format
        elif detected_format == NotebookFormat.JUPYTER:
            return JupyterNotebookParser, detected_format
        else:
            raise ParseError(f"Unsupported format: {detected_format}")

    @staticmethod
    def validate_format_consistency(file_path: str, expected_format: NotebookFormat) -> bool:
        """
        Validate that file format matches expectation.

        Args:
            file_path: Path to the notebook file
            expected_format: Expected format

        Returns:
            True if format matches expectation
        """
        try:
            detected_format = FormatDetector.detect_format(file_path)
            return detected_format == expected_format
        except ParseError:
            return False

    @staticmethod
    def suggest_output_format(input_format: NotebookFormat,
                             output_path: Optional[str] = None) -> NotebookFormat:
        """
        Suggest appropriate output format.

        Args:
            input_format: Input notebook format
            output_path: Optional output file path

        Returns:
            Suggested output format
        """
        # AIDEV-NOTE: If output path is specified, use its extension
        if output_path:
            try:
                path = Path(output_path)
                extension = path.suffix.lower()
                if extension == ".md":
                    return NotebookFormat.MARKDOWN
                elif extension == ".ipynb":
                    return NotebookFormat.JUPYTER
            except Exception:
                pass

        # AIDEV-NOTE: Default to same format as input
        return input_format