"""Tests for Jupyter Java executor."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import subprocess
import tempfile
from pathlib import Path

from src.javanotebook.nb_executor import JupyterJavaExecutor
from src.javanotebook.nb_models import (
    JupyterExecutionRequest, JupyterExecutionResult,
    JupyterStream, JupyterError
)
from src.javanotebook.exceptions import JavaNotFoundError


class TestJupyterJavaExecutor:
    """Test JupyterJavaExecutor functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch('subprocess.run') as mock_run:
            # Mock successful Java verification
            mock_run.return_value = Mock(returncode=0)
            self.executor = JupyterJavaExecutor(timeout=10)

    def test_initialization(self):
        """Test executor initialization."""
        assert self.executor.timeout == 10
        assert self.executor.execution_count == 0

    @patch('subprocess.run')
    def test_java_not_found(self, mock_run):
        """Test behavior when Java is not found."""
        mock_run.side_effect = FileNotFoundError()

        with pytest.raises(JavaNotFoundError):
            JupyterJavaExecutor()

    def test_execution_count_management(self):
        """Test execution count management."""
        assert self.executor.get_execution_count() == 0

        self.executor.execution_count = 5
        assert self.executor.get_execution_count() == 5

        self.executor.reset_execution_count()
        assert self.executor.get_execution_count() == 0

    def test_has_main_method_true(self):
        """Test detecting main method when present."""
        code_with_main = """
public class Test {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}
"""
        assert self.executor._has_main_method(code_with_main) is True

    def test_has_main_method_false(self):
        """Test detecting main method when absent."""
        code_without_main = """
public class Test {
    public void someMethod() {
        System.out.println("Hello");
    }
}
"""
        assert self.executor._has_main_method(code_without_main) is False

    def test_wrap_code_with_main(self):
        """Test wrapping simple code with main method."""
        simple_code = "System.out.println(\"Hello\");"

        wrapped = self.executor._wrap_code_with_main(simple_code)

        assert "public class Main" in wrapped
        assert "public static void main" in wrapped
        assert "System.out.println(\"Hello\");" in wrapped

    def test_prepare_code_already_has_main(self):
        """Test preparing code that already has main method."""
        code_with_main = """
public class Test {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}
"""
        prepared = self.executor._prepare_code(code_with_main)
        assert prepared == code_with_main

    def test_prepare_code_simple_statements(self):
        """Test preparing simple Java statements."""
        simple_code = "int x = 10;\nSystem.out.println(x);"

        prepared = self.executor._prepare_code(simple_code)

        assert "public class Main" in prepared
        assert "public static void main" in prepared
        assert simple_code in prepared

    def test_extract_class_name_success(self):
        """Test successful class name extraction."""
        java_code = """
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}
"""
        class_name = self.executor._extract_class_name(java_code)
        assert class_name == "HelloWorld"

    def test_extract_class_name_failure(self):
        """Test class name extraction failure."""
        invalid_code = "System.out.println(\"Hello\");"

        with pytest.raises(Exception):  # Should raise CompilationError
            self.executor._extract_class_name(invalid_code)

    @patch('tempfile.TemporaryDirectory')
    @patch('subprocess.run')
    def test_compile_java_code_success(self, mock_run, mock_tempdir):
        """Test successful Java compilation."""
        # Mock temporary directory
        mock_tempdir.return_value.__enter__.return_value = "/tmp/test"

        # Mock successful compilation
        mock_run.return_value = Mock(returncode=0, stderr="")

        java_code = """
public class Test {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}
"""

        with patch.object(Path, 'write_text'):
            result = self.executor._compile_java_code(java_code)

        assert result["success"] is True
        assert result["class_name"] == "Test"

    @patch('tempfile.TemporaryDirectory')
    @patch('subprocess.run')
    def test_compile_java_code_failure(self, mock_run, mock_tempdir):
        """Test Java compilation failure."""
        # Mock temporary directory
        mock_tempdir.return_value.__enter__.return_value = "/tmp/test"

        # Mock compilation failure
        mock_run.return_value = Mock(
            returncode=1,
            stderr="Error: ';' expected"
        )

        java_code = """
public class Test {
    public static void main(String[] args) {
        System.out.println("Hello")  // Missing semicolon
    }
}
"""

        with patch.object(Path, 'write_text'):
            result = self.executor._compile_java_code(java_code)

        assert result["success"] is False
        assert "';' expected" in result["error"]

    @patch('subprocess.run')
    def test_execute_java_code_success(self, mock_run):
        """Test successful Java code execution."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Hello, World!\n",
            stderr=""
        )

        result = self.executor._execute_java_code("Test", "/tmp/test")

        assert result["returncode"] == 0
        assert result["stdout"] == "Hello, World!\n"
        assert result["stderr"] == ""

    @patch('subprocess.run')
    def test_execute_java_code_runtime_error(self, mock_run):
        """Test Java code execution with runtime error."""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="Exception in thread \"main\" java.lang.RuntimeException"
        )

        result = self.executor._execute_java_code("Test", "/tmp/test")

        assert result["returncode"] == 1
        assert "RuntimeException" in result["stderr"]

    @patch('subprocess.run')
    def test_execute_java_code_timeout(self, mock_run):
        """Test Java code execution timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("java", 10)

        result = self.executor._execute_java_code("Test", "/tmp/test")

        assert result["returncode"] == -1
        assert "timed out" in result["stderr"]

    @patch.object(JupyterJavaExecutor, '_compile_java_code')
    @patch.object(JupyterJavaExecutor, '_execute_java_code')
    def test_execute_code_success(self, mock_execute, mock_compile):
        """Test complete code execution success."""
        # Mock successful compilation
        mock_compile.return_value = {
            "success": True,
            "class_name": "Test",
            "temp_dir": "/tmp/test"
        }

        # Mock successful execution
        mock_execute.return_value = {
            "returncode": 0,
            "stdout": "Hello, World!\n",
            "stderr": ""
        }

        request = JupyterExecutionRequest(code="System.out.println(\"Hello, World!\");")
        result = self.executor.execute_code(request)

        assert isinstance(result, JupyterExecutionResult)
        assert result.success is True
        assert result.execution_count == 1
        assert len(result.outputs) == 1
        assert isinstance(result.outputs[0], JupyterStream)
        assert result.outputs[0].text == "Hello, World!\n"

    @patch.object(JupyterJavaExecutor, '_compile_java_code')
    def test_execute_code_compilation_error(self, mock_compile):
        """Test code execution with compilation error."""
        # Mock compilation failure
        mock_compile.return_value = {
            "success": False,
            "error": "';' expected",
            "traceback": ["Error at line 1", "';' expected"]
        }

        request = JupyterExecutionRequest(code="invalid java code")
        result = self.executor.execute_code(request)

        assert result.success is False
        assert len(result.outputs) == 1
        assert isinstance(result.outputs[0], JupyterError)
        assert result.outputs[0].ename == "CompilationError"

    @patch.object(JupyterJavaExecutor, '_compile_java_code')
    @patch.object(JupyterJavaExecutor, '_execute_java_code')
    def test_execute_code_with_stderr(self, mock_execute, mock_compile):
        """Test code execution with stderr output."""
        # Mock successful compilation
        mock_compile.return_value = {
            "success": True,
            "class_name": "Test",
            "temp_dir": "/tmp/test"
        }

        # Mock execution with stderr
        mock_execute.return_value = {
            "returncode": 0,
            "stdout": "Output\n",
            "stderr": "Warning: something\n"
        }

        request = JupyterExecutionRequest(code="test code")
        result = self.executor.execute_code(request)

        assert result.success is True
        assert len(result.outputs) == 2

        # Check stdout
        stdout_output = next(o for o in result.outputs if o.name == "stdout")
        assert stdout_output.text == "Output\n"

        # Check stderr
        stderr_output = next(o for o in result.outputs if o.name == "stderr")
        assert stderr_output.text == "Warning: something\n"

    def test_parse_compilation_error(self):
        """Test parsing compilation error output."""
        error_output = """Test.java:5: error: ';' expected
        System.out.println("Hello")
                                   ^
1 error"""

        traceback = self.executor._parse_compilation_error(error_output)

        assert len(traceback) > 0
        assert any("';' expected" in line for line in traceback)

    def test_validate_java_code_valid(self):
        """Test validating valid Java code."""
        valid_code = """
public class Test {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}
"""
        assert self.executor.validate_java_code(valid_code) is True

    def test_validate_java_code_invalid(self):
        """Test validating invalid Java code."""
        # This will fail in _extract_class_name
        invalid_code = "This is not Java code at all"
        assert self.executor.validate_java_code(invalid_code) is False

    def test_execution_request_with_execution_count(self):
        """Test execution request with specific execution count."""
        with patch.object(self.executor, '_compile_java_code') as mock_compile, \
             patch.object(self.executor, '_execute_java_code') as mock_execute:

            mock_compile.return_value = {
                "success": True,
                "class_name": "Test",
                "temp_dir": "/tmp/test"
            }
            mock_execute.return_value = {
                "returncode": 0,
                "stdout": "Output\n",
                "stderr": ""
            }

            request = JupyterExecutionRequest(
                code="test code",
                execution_count=10
            )
            result = self.executor.execute_code(request)

            assert result.execution_count == 10
            assert self.executor.get_execution_count() == 10