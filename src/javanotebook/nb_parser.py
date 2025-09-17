"""Jupyter notebook parser using nbformat."""

import re
from typing import List, Optional
from pathlib import Path
import nbformat
from nbformat import NotebookNode
from nbformat.validator import ValidationError

from .nb_models import (
    JupyterNotebook, JupyterCodeCell, JupyterMarkdownCell, JupyterRawCell,
    JupyterNotebookInfo
)
from .exceptions import ParseError


class JupyterNotebookParser:
    """Parser for Jupyter notebook files (.ipynb)."""

    def __init__(self):
        """Initialize the Jupyter notebook parser."""
        # AIDEV-NOTE: Regex pattern to extract class name from Java code
        self.java_class_pattern = re.compile(
            r'(?:public\s+)?class\s+(\w+)',
            re.MULTILINE
        )

        # AIDEV-NOTE: Pattern to detect main method
        self.main_method_pattern = re.compile(
            r'public\s+static\s+void\s+main\s*\(\s*String\s*\[\s*\]\s*\w*\s*\)',
            re.IGNORECASE | re.MULTILINE
        )

    def parse_file(self, file_path: str) -> JupyterNotebook:
        """
        Parse a Jupyter notebook file.

        Args:
            file_path: Path to the .ipynb file

        Returns:
            JupyterNotebook object

        Raises:
            ParseError: If file cannot be parsed
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise ParseError(f"Notebook file not found: {file_path}")

            # AIDEV-NOTE: Read and validate notebook using nbformat
            with open(file_path, 'r', encoding='utf-8') as f:
                nb_node = nbformat.read(f, as_version=4)

            return self.parse_notebook_node(nb_node)

        except (IOError, UnicodeDecodeError) as e:
            raise ParseError(f"Cannot read notebook file {file_path}: {str(e)}")
        except ValidationError as e:
            raise ParseError(f"Invalid notebook format in {file_path}: {str(e)}")
        except Exception as e:
            raise ParseError(f"Error parsing notebook {file_path}: {str(e)}")

    def parse_notebook_node(self, nb_node: NotebookNode) -> JupyterNotebook:
        """
        Parse a NotebookNode into JupyterNotebook.

        Args:
            nb_node: nbformat NotebookNode

        Returns:
            JupyterNotebook object
        """
        try:
            # AIDEV-NOTE: Validate notebook structure
            nbformat.validate(nb_node)
            return JupyterNotebook.from_notebook_node(nb_node)
        except ValidationError as e:
            raise ParseError(f"Notebook validation failed: {str(e)}")

    def save_notebook(self, notebook: JupyterNotebook, file_path: str) -> None:
        """
        Save notebook to file.

        Args:
            notebook: JupyterNotebook to save
            file_path: Output file path

        Raises:
            ParseError: If notebook cannot be saved
        """
        try:
            # AIDEV-NOTE: Convert to NotebookNode and save
            nb_node = notebook.to_notebook_node()

            # AIDEV-NOTE: Validate before saving
            nbformat.validate(nb_node)

            with open(file_path, 'w', encoding='utf-8') as f:
                nbformat.write(nb_node, f)

        except ValidationError as e:
            raise ParseError(f"Notebook validation failed before saving: {str(e)}")
        except (IOError, UnicodeEncodeError) as e:
            raise ParseError(f"Cannot save notebook to {file_path}: {str(e)}")

    def create_empty_notebook(self) -> JupyterNotebook:
        """
        Create a new empty Jupyter notebook.

        Returns:
            Empty JupyterNotebook with default metadata
        """
        return JupyterNotebook()

    def add_code_cell(self, notebook: JupyterNotebook, java_code: str,
                     cell_id: Optional[str] = None) -> JupyterCodeCell:
        """
        Add a Java code cell to the notebook.

        Args:
            notebook: Target notebook
            java_code: Java source code
            cell_id: Optional cell ID

        Returns:
            Created code cell
        """
        # AIDEV-NOTE: Create new code cell with Java metadata
        cell = JupyterCodeCell(
            id=cell_id,
            source=java_code,
            metadata={
                "language": "java",
                "java_executable": self.has_main_method(java_code)
            }
        )

        notebook.cells.append(cell)
        return cell

    def add_markdown_cell(self, notebook: JupyterNotebook, markdown_content: str,
                         cell_id: Optional[str] = None) -> JupyterMarkdownCell:
        """
        Add a markdown cell to the notebook.

        Args:
            notebook: Target notebook
            markdown_content: Markdown content
            cell_id: Optional cell ID

        Returns:
            Created markdown cell
        """
        cell = JupyterMarkdownCell(
            id=cell_id,
            source=markdown_content
        )

        notebook.cells.append(cell)
        return cell

    def extract_class_name(self, java_code: str) -> str:
        """
        Extract the public class name from Java code.

        Args:
            java_code: Java source code

        Returns:
            Class name

        Raises:
            ParseError: If no class found
        """
        # AIDEV-NOTE: Find public class declaration first
        public_class_match = re.search(r'public\s+class\s+(\w+)', java_code)
        if public_class_match:
            return public_class_match.group(1)

        # AIDEV-NOTE: Fallback to any class declaration
        class_match = self.java_class_pattern.search(java_code)
        if class_match:
            return class_match.group(1)

        raise ParseError("No class declaration found in Java code")

    def has_main_method(self, java_code: str) -> bool:
        """
        Check if Java code contains a main method.

        Args:
            java_code: Java source code

        Returns:
            True if main method is found
        """
        return bool(self.main_method_pattern.search(java_code))

    def wrap_code_with_main(self, java_code: str) -> str:
        """
        Wrap simple Java statements with a Main class and main method.

        Args:
            java_code: Simple Java statements

        Returns:
            Complete Java class with main method
        """
        if self.has_main_method(java_code):
            return java_code

        # AIDEV-NOTE: Check if code already has a class declaration
        if "class " in java_code:
            return java_code

        # AIDEV-NOTE: Wrap with Main class
        wrapped_code = f"""public class Main {{
    public static void main(String[] args) {{
        {java_code}
    }}
}}"""
        return wrapped_code

    def validate_java_code(self, java_code: str) -> bool:
        """
        Validate that Java code has the required structure.

        Args:
            java_code: Java source code

        Returns:
            True if code is valid (has class and optionally main method)
        """
        try:
            self.extract_class_name(java_code)
            return True
        except ParseError:
            # AIDEV-NOTE: If no class found, check if it's simple statements
            # that can be auto-wrapped
            if java_code.strip() and not any(
                keyword in java_code for keyword in ['class ', 'interface ', 'enum ']
            ):
                return True  # Can be auto-wrapped
            return False

    def get_notebook_info(self, file_path: str) -> JupyterNotebookInfo:
        """
        Get basic information about a notebook file.

        Args:
            file_path: Path to the notebook file

        Returns:
            JupyterNotebookInfo with basic statistics
        """
        notebook = self.parse_file(file_path)

        # AIDEV-NOTE: Extract title from first markdown cell or filename
        title = None
        if notebook.markdown_cells:
            first_md = notebook.markdown_cells[0]
            source = first_md.source
            if isinstance(source, list):
                source = ''.join(source)
            # Extract title from first heading
            lines = source.split('\n')
            for line in lines:
                if line.strip().startswith('#'):
                    title = line.strip().lstrip('#').strip()
                    break

        if not title:
            title = Path(file_path).stem

        # AIDEV-NOTE: Get kernel information
        kernel_name = None
        language = None
        if 'kernelspec' in notebook.metadata:
            kernel_name = notebook.metadata['kernelspec'].get('name')
        if 'language_info' in notebook.metadata:
            language = notebook.metadata['language_info'].get('name')

        return JupyterNotebookInfo(
            filename=Path(file_path).name,
            title=title,
            total_cells=len(notebook.cells),
            code_cells_count=len(notebook.code_cells),
            markdown_cells_count=len(notebook.markdown_cells),
            raw_cells_count=len(notebook.raw_cells),
            nbformat_version=f"{notebook.nbformat}.{notebook.nbformat_minor}",
            kernel_name=kernel_name,
            language=language
        )

    def convert_from_markdown(self, md_content: str) -> JupyterNotebook:
        """
        Convert markdown content to Jupyter notebook format.

        Args:
            md_content: Markdown content with Java code blocks

        Returns:
            JupyterNotebook object
        """
        notebook = self.create_empty_notebook()

        # AIDEV-NOTE: Split content by Java code blocks
        java_code_pattern = re.compile(
            r'^```java\s*\n(.*?)\n```',
            re.MULTILINE | re.DOTALL
        )

        parts = java_code_pattern.split(md_content)

        for i, part in enumerate(parts):
            if not part.strip():
                continue

            if i % 2 == 0:
                # Markdown content (even indices)
                if part.strip():
                    self.add_markdown_cell(notebook, part.strip())
            else:
                # Java code content (odd indices)
                self.add_code_cell(notebook, part.strip())

        return notebook

    def convert_to_markdown(self, notebook: JupyterNotebook) -> str:
        """
        Convert Jupyter notebook to markdown format.

        Args:
            notebook: JupyterNotebook to convert

        Returns:
            Markdown content string
        """
        md_parts = []

        for cell in notebook.cells:
            if isinstance(cell, JupyterMarkdownCell):
                source = cell.source
                if isinstance(source, list):
                    source = ''.join(source)
                md_parts.append(source)
            elif isinstance(cell, JupyterCodeCell):
                source = cell.source
                if isinstance(source, list):
                    source = ''.join(source)
                md_parts.append(f"```java\n{source}\n```")
            elif isinstance(cell, JupyterRawCell):
                source = cell.source
                if isinstance(source, list):
                    source = ''.join(source)
                md_parts.append(source)

        return '\n\n'.join(md_parts)