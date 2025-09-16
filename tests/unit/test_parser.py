"""Unit tests for the notebook parser."""

import pytest
from javanotebook.parser import NotebookParser
from javanotebook.models import Notebook, MarkdownCell, JavaCodeCell
from javanotebook.exceptions import ParseError


class TestNotebookParser:
    """Test cases for NotebookParser."""
    
    def test_parse_simple_notebook(self, notebook_parser, sample_notebook_content):
        """Test parsing a simple notebook with markdown and code cells."""
        notebook = notebook_parser.parse_content(sample_notebook_content)
        
        assert isinstance(notebook, Notebook)
        assert len(notebook.cells) == 4  # 2 markdown + 2 code cells
        
        # Check cell types
        assert isinstance(notebook.cells[0], MarkdownCell)
        assert isinstance(notebook.cells[1], JavaCodeCell)
        assert isinstance(notebook.cells[2], MarkdownCell)
        assert isinstance(notebook.cells[3], JavaCodeCell)
    
    def test_parse_file(self, notebook_parser, temp_notebook_file):
        """Test parsing a notebook from a file."""
        notebook = notebook_parser.parse_file(temp_notebook_file)
        
        assert isinstance(notebook, Notebook)
        assert len(notebook.cells) > 0
    
    def test_parse_nonexistent_file(self, notebook_parser):
        """Test parsing a non-existent file raises ParseError."""
        with pytest.raises(ParseError, match="Notebook file not found"):
            notebook_parser.parse_file("nonexistent.md")
    
    def test_extract_class_name_simple(self, notebook_parser):
        """Test extracting class name from simple Java code."""
        java_code = """public class TestClass {
    public static void main(String[] args) {
        System.out.println("Test");
    }
}"""
        class_name = notebook_parser.extract_class_name(java_code)
        assert class_name == "TestClass"
    
    def test_extract_class_name_with_spaces(self, notebook_parser):
        """Test extracting class name with various spacing."""
        java_code = "public   class   MyClass   {"
        class_name = notebook_parser.extract_class_name(java_code)
        assert class_name == "MyClass"
    
    def test_extract_class_name_no_public(self, notebook_parser):
        """Test extracting class name without public modifier."""
        java_code = "class SimpleClass {"
        class_name = notebook_parser.extract_class_name(java_code)
        assert class_name == "SimpleClass"
    
    def test_extract_class_name_not_found(self, notebook_parser):
        """Test extracting class name when no class is found."""
        java_code = "// Just a comment, no class"
        with pytest.raises(ParseError, match="No class declaration found"):
            notebook_parser.extract_class_name(java_code)
    
    def test_has_main_method_valid(self, notebook_parser):
        """Test detecting valid main method."""
        java_code = """public class Test {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}"""
        assert notebook_parser.has_main_method(java_code) is True
    
    def test_has_main_method_with_different_param_name(self, notebook_parser):
        """Test detecting main method with different parameter name."""
        java_code = """public class Test {
    public static void main(String[] arguments) {
        System.out.println("Hello");
    }
}"""
        assert notebook_parser.has_main_method(java_code) is True
    
    def test_has_main_method_missing(self, notebook_parser):
        """Test detecting missing main method."""
        java_code = """public class Test {
    public void someMethod() {
        System.out.println("Hello");
    }
}"""
        assert notebook_parser.has_main_method(java_code) is False
    
    def test_validate_java_code_valid(self, notebook_parser, valid_java_code):
        """Test validating valid Java code."""
        assert notebook_parser.validate_java_code(valid_java_code) is True
    
    def test_validate_java_code_invalid(self, notebook_parser, invalid_java_code):
        """Test validating invalid Java code."""
        assert notebook_parser.validate_java_code(invalid_java_code) is False
    
    def test_parse_empty_content(self, notebook_parser):
        """Test parsing empty content."""
        notebook = notebook_parser.parse_content("")
        assert len(notebook.cells) == 0
    
    def test_parse_only_markdown(self, notebook_parser):
        """Test parsing content with only markdown."""
        content = "# Title\n\nSome text here."
        notebook = notebook_parser.parse_content(content)
        
        assert len(notebook.cells) == 1
        assert isinstance(notebook.cells[0], MarkdownCell)
        assert "Title" in notebook.cells[0].content
    
    def test_parse_only_java_code(self, notebook_parser):
        """Test parsing content with only Java code."""
        content = """```java
public class OnlyCode {
    public static void main(String[] args) {
        System.out.println("Only code");
    }
}
```"""
        notebook = notebook_parser.parse_content(content)
        
        assert len(notebook.cells) == 1
        assert isinstance(notebook.cells[0], JavaCodeCell)
        assert "OnlyCode" in notebook.cells[0].content