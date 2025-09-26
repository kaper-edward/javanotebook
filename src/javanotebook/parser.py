"""Markdown notebook parser for Java Notebook."""

import re
from typing import List
from pathlib import Path
import markdown
from markdown.extensions import codehilite, fenced_code, tables, toc
from pygments.formatters import HtmlFormatter

from .models import Notebook, Cell, MarkdownCell, JavaCodeCell
from .exceptions import ParseError


class NotebookParser:
    """Parser for markdown-based Java notebooks."""
    
    def __init__(self):
        # AIDEV-NOTE: Regex pattern to match Java code blocks
        self.java_code_pattern = re.compile(
            r'^```java\s*\n(.*?)\n```',
            re.MULTILINE | re.DOTALL
        )
        
        # AIDEV-NOTE: Configure markdown processor with extensions
        self.markdown_processor = markdown.Markdown(
            extensions=[
                'codehilite',
                'fenced_code',
                'tables',
                'toc',
                'nl2br'  # Convert newlines to <br> tags
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': True,
                    'pygments_style': 'default'
                }
            }
        )
    
    def parse_file(self, file_path: str) -> Notebook:
        """Parse a markdown file into a Notebook object."""
        try:
            content = Path(file_path).read_text(encoding='utf-8')
            return self.parse_content(content)
        except FileNotFoundError:
            raise ParseError(f"Notebook file not found: {file_path}")
        except UnicodeDecodeError:
            raise ParseError(f"Unable to decode file: {file_path}")
    
    def parse_content(self, content: str) -> Notebook:
        """Parse markdown content into a Notebook object."""
        cells = self._split_into_cells(content)
        return Notebook(cells=cells)
    
    def _split_into_cells(self, content: str) -> List[Cell]:
        """Split markdown content into cells."""
        cells = []
        cell_id_counter = 0
        
        # AIDEV-NOTE: Split content by Java code blocks
        parts = self.java_code_pattern.split(content)
        
        for i, part in enumerate(parts):
            if not part.strip():
                continue
                
            cell_id_counter += 1
            
            if i % 2 == 0:
                # Markdown content (even indices)
                if part.strip():
                    # AIDEV-NOTE: Render markdown to HTML server-side
                    rendered_html = self._render_markdown(part.strip())
                    cells.append(MarkdownCell(
                        content=rendered_html,
                        id=f"cell-{cell_id_counter}"
                    ))
            else:
                # Java code content (odd indices)
                cells.append(JavaCodeCell(
                    content=part.strip(),
                    id=f"cell-{cell_id_counter}"
                ))
        
        return cells
    
    def _render_markdown(self, markdown_content: str) -> str:
        """Render markdown content to HTML."""
        try:
            # AIDEV-NOTE: Reset markdown processor for each render
            self.markdown_processor.reset()
            html = self.markdown_processor.convert(markdown_content)
            return html
        except Exception as e:
            # AIDEV-NOTE: Fallback to raw content if rendering fails
            return f"<p>Markdown rendering error: {str(e)}</p><pre>{markdown_content}</pre>"
    
    def extract_class_name(self, java_code: str) -> str:
        """Extract the public class name from Java code."""
        # AIDEV-NOTE: Find public class declaration
        class_match = re.search(r'public\s+class\s+(\w+)', java_code)
        if class_match:
            return class_match.group(1)
        
        # AIDEV-NOTE: Fallback to any class declaration
        class_match = re.search(r'class\s+(\w+)', java_code)
        if class_match:
            return class_match.group(1)
        
        raise ParseError("No class declaration found in Java code")
    
    def has_main_method(self, java_code: str) -> bool:
        """Check if Java code contains a main method."""
        main_pattern = re.compile(
            r'public\s+static\s+void\s+main\s*\(\s*String\s*\[\s*\]\s*\w*\s*\)',
            re.IGNORECASE
        )
        return bool(main_pattern.search(java_code))
    
    def validate_java_code(self, java_code: str) -> bool:
        """Validate that Java code has the required structure."""
        try:
            self.extract_class_name(java_code)
            return self.has_main_method(java_code)
        except ParseError:
            return False

    def extract_package_name(self, java_code: str) -> str:
        """Extract package name from Java code."""
        # AIDEV-NOTE: Find package declaration at the start of the file
        package_match = re.search(r'^\s*package\s+([\w.]+)\s*;', java_code, re.MULTILINE)
        if package_match:
            return package_match.group(1)
        return ""  # Default package (no package declaration)

    def get_full_class_name(self, java_code: str) -> str:
        """Get full class name including package."""
        package_name = self.extract_package_name(java_code)
        class_name = self.extract_class_name(java_code)

        if package_name:
            return f"{package_name}.{class_name}"
        return class_name

    def get_package_path(self, package_name: str) -> str:
        """Convert package name to directory path."""
        if not package_name:
            return ""
        return package_name.replace('.', '/')

    def extract_imports(self, java_code: str) -> List[str]:
        """Extract all import statements from Java code."""
        # AIDEV-NOTE: Find all import declarations
        import_matches = re.findall(r'^\s*import\s+([\w.*]+)\s*;', java_code, re.MULTILINE)
        return import_matches

    def has_package_declaration(self, java_code: str) -> bool:
        """Check if Java code has a package declaration."""
        return bool(re.search(r'^\s*package\s+[\w.]+\s*;', java_code, re.MULTILINE))