"""Jupyter-compatible Java code execution engine."""

import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import re

from .nb_models import (
    JupyterExecutionResult, JupyterExecutionRequest,
    JupyterStream, JupyterError, JupyterExecuteResult
)
from .exceptions import CompilationError, ExecutionError, JavaNotFoundError
from .package_manager import PackageManager
from .parser import NotebookParser


class JupyterJavaExecutor:
    """Handles compilation and execution of Java code with Jupyter-compatible output."""

    def __init__(self, timeout: int = 30):
        """
        Initialize the executor.

        Args:
            timeout: Maximum execution time in seconds
        """
        self.timeout = timeout
        self.execution_count = 0
        self.package_manager = PackageManager(timeout)
        self.parser = NotebookParser()
        self._verify_java_installation()

    def _verify_java_installation(self) -> None:
        """Verify that Java JDK is installed and accessible."""
        try:
            # AIDEV-NOTE: Check if javac is available
            subprocess.run(
                ["javac", "-version"],
                capture_output=True,
                check=True,
                timeout=5
            )
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            raise JavaNotFoundError("Java JDK not found. Please install JDK and ensure javac is in PATH.")

    def execute_code(self, request: JupyterExecutionRequest) -> JupyterExecutionResult:
        """
        Execute Java code and return Jupyter-compatible results.

        Args:
            request: Execution request with Java code

        Returns:
            JupyterExecutionResult with outputs in Jupyter format
        """
        start_time = time.time()

        # AIDEV-NOTE: Increment execution count for this session
        if request.execution_count is not None:
            self.execution_count = request.execution_count
        else:
            self.execution_count += 1

        try:
            # AIDEV-NOTE: Prepare code (auto-wrap if needed)
            processed_code = self._prepare_code(request.code)

            # AIDEV-NOTE: Check if code has package declaration
            has_package = self.parser.has_package_declaration(processed_code)

            if has_package:
                # AIDEV-NOTE: Use PackageManager for code with packages
                return self._execute_with_package_support([processed_code], start_time)
            else:
                # AIDEV-NOTE: Use legacy method for simple code without packages
                return self._execute_single_class_jupyter(processed_code, start_time)

        except Exception as e:
            return JupyterExecutionResult(
                success=False,
                execution_count=self.execution_count,
                outputs=[self._create_error_output(
                    type(e).__name__,
                    str(e),
                    []
                )],
                execution_time=time.time() - start_time,
                error_message=str(e)
            )

    def execute_multiple_codes(self, java_codes: list[str]) -> JupyterExecutionResult:
        """Execute multiple Java code cells with package support."""
        start_time = time.time()

        # AIDEV-NOTE: Increment execution count for this session
        self.execution_count += 1

        try:
            # AIDEV-NOTE: Prepare each code (auto-wrap if needed)
            processed_codes = [self._prepare_code(code) for code in java_codes if code.strip()]

            if not processed_codes:
                return JupyterExecutionResult(
                    success=False,
                    execution_count=self.execution_count,
                    outputs=[self._create_error_output(
                        "ValueError",
                        "No valid Java code provided",
                        []
                    )],
                    execution_time=time.time() - start_time,
                    error_message="No valid Java code provided"
                )

            # AIDEV-NOTE: Use PackageManager for multiple classes
            return self._execute_with_package_support(processed_codes, start_time)

        except Exception as e:
            return JupyterExecutionResult(
                success=False,
                execution_count=self.execution_count,
                outputs=[self._create_error_output(
                    type(e).__name__,
                    str(e),
                    []
                )],
                execution_time=time.time() - start_time,
                error_message=str(e)
            )

    def _execute_with_package_support(self, java_codes: list[str], start_time: float) -> JupyterExecutionResult:
        """Execute Java code using PackageManager for package support."""
        try:
            # AIDEV-NOTE: Use PackageManager for multi-class and package support
            result = self.package_manager.process_multi_class_execution(java_codes)

            outputs = []
            success = result["success"]

            # AIDEV-NOTE: Add stdout output if present
            if result.get("stdout"):
                outputs.append(JupyterStream(
                    name="stdout",
                    text=result["stdout"]
                ))

            # AIDEV-NOTE: Add stderr output if present
            if result.get("stderr"):
                outputs.append(JupyterStream(
                    name="stderr",
                    text=result["stderr"]
                ))

            # AIDEV-NOTE: Add error output for failures
            if not success:
                error_message = result.get("error", "Unknown error")
                outputs.append(self._create_error_output(
                    "ExecutionError",
                    error_message,
                    result.get("compilation_error", "").splitlines() if result.get("compilation_error") else []
                ))

            return JupyterExecutionResult(
                success=success,
                execution_count=self.execution_count,
                outputs=outputs,
                execution_time=time.time() - start_time,
                error_message=result.get("error") if not success else None
            )

        except Exception as e:
            return JupyterExecutionResult(
                success=False,
                execution_count=self.execution_count,
                outputs=[self._create_error_output(
                    type(e).__name__,
                    f"Package execution error: {str(e)}",
                    []
                )],
                execution_time=time.time() - start_time,
                error_message=f"Package execution error: {str(e)}"
            )

    def _execute_single_class_jupyter(self, processed_code: str, start_time: float) -> JupyterExecutionResult:
        """Execute single Java class using legacy method (no packages)."""
        try:
            # AIDEV-NOTE: Compile and run Java code in single temp directory context
            with tempfile.TemporaryDirectory() as temp_dir:
                compilation_result = self._compile_java_code_in_dir(processed_code, temp_dir)
                if not compilation_result["success"]:
                    return JupyterExecutionResult(
                        success=False,
                        execution_count=self.execution_count,
                        outputs=[self._create_error_output(
                            "CompilationError",
                            compilation_result["error"],
                            compilation_result.get("traceback", [])
                        )],
                        execution_time=time.time() - start_time,
                        error_message=compilation_result["error"]
                    )

                # AIDEV-NOTE: Execute compiled code in same temp directory
                execution_result = self._execute_java_code(
                    compilation_result["class_name"],
                    temp_dir
                )

            outputs = []
            success = execution_result["returncode"] == 0

            # AIDEV-NOTE: Add stdout output if present
            if execution_result["stdout"]:
                outputs.append(JupyterStream(
                    name="stdout",
                    text=execution_result["stdout"]
                ))

            # AIDEV-NOTE: Add stderr output if present
            if execution_result["stderr"]:
                outputs.append(JupyterStream(
                    name="stderr",
                    text=execution_result["stderr"]
                ))

            # AIDEV-NOTE: Add error output for non-zero exit codes
            if not success:
                outputs.append(self._create_error_output(
                    "RuntimeError",
                    f"Process exited with code {execution_result['returncode']}",
                    execution_result["stderr"].splitlines() if execution_result["stderr"] else []
                ))

            return JupyterExecutionResult(
                success=success,
                execution_count=self.execution_count,
                outputs=outputs,
                execution_time=time.time() - start_time
            )

        except Exception as e:
            return JupyterExecutionResult(
                success=False,
                execution_count=self.execution_count,
                outputs=[self._create_error_output(
                    type(e).__name__,
                    f"Single class execution error: {str(e)}",
                    []
                )],
                execution_time=time.time() - start_time,
                error_message=f"Single class execution error: {str(e)}"
            )

    def _prepare_code(self, java_code: str) -> str:
        """
        Prepare Java code for execution (auto-wrap if needed).

        Args:
            java_code: Original Java code

        Returns:
            Processed Java code ready for compilation
        """
        # AIDEV-NOTE: Check if code already has a main method
        if self._has_main_method(java_code):
            return java_code

        # AIDEV-NOTE: Check if code already has a class declaration
        if re.search(r'\bclass\s+\w+', java_code):
            return java_code

        # AIDEV-NOTE: Auto-wrap simple statements with Main class
        return self._wrap_code_with_main(java_code)

    def _has_main_method(self, java_code: str) -> bool:
        """Check if Java code contains a main method."""
        main_pattern = re.compile(
            r'public\s+static\s+void\s+main\s*\(\s*String\s*\[\s*\]\s*\w*\s*\)',
            re.IGNORECASE
        )
        return bool(main_pattern.search(java_code))

    def _wrap_code_with_main(self, java_code: str) -> str:
        """Wrap simple Java statements with a Main class and main method."""
        # AIDEV-NOTE: Indent the original code properly
        indented_code = '\n'.join(f"        {line}" for line in java_code.splitlines())

        wrapped_code = f"""public class Main {{
    public static void main(String[] args) {{
{indented_code}
    }}
}}"""
        return wrapped_code

    def _extract_class_name(self, java_code: str) -> str:
        """
        Extract the public class name from Java code.

        Args:
            java_code: Java source code

        Returns:
            Class name

        Raises:
            CompilationError: If no class found
        """
        # AIDEV-NOTE: Find public class declaration first
        public_class_match = re.search(r'public\s+class\s+(\w+)', java_code)
        if public_class_match:
            return public_class_match.group(1)

        # AIDEV-NOTE: Fallback to any class declaration
        class_match = re.search(r'class\s+(\w+)', java_code)
        if class_match:
            return class_match.group(1)

        raise CompilationError("No class declaration found in Java code")

    def _compile_java_code_in_dir(self, java_code: str, temp_dir: str) -> Dict[str, Any]:
        """
        Compile Java code in the specified directory.

        Args:
            java_code: Java source code to compile
            temp_dir: Directory to compile in

        Returns:
            Dictionary with compilation results
        """
        try:
            class_name = self._extract_class_name(java_code)
        except CompilationError as e:
            return {
                "success": False,
                "error": str(e),
                "traceback": []
            }

        java_file = Path(temp_dir) / f"{class_name}.java"

        try:
            # AIDEV-NOTE: Write Java source to temporary file
            java_file.write_text(java_code, encoding='utf-8')

            # AIDEV-NOTE: Compile Java source
            compile_result = subprocess.run(
                ["javac", str(java_file)],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            if compile_result.returncode != 0:
                return {
                    "success": False,
                    "error": compile_result.stderr,
                    "traceback": self._parse_compilation_error(compile_result.stderr)
                }

            return {
                "success": True,
                "class_name": class_name,
                "java_file": str(java_file)
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Compilation timed out after {self.timeout} seconds",
                "traceback": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Compilation error: {str(e)}",
                "traceback": []
            }

    def _execute_java_code(self, class_name: str, temp_dir: str) -> Dict[str, Any]:
        """
        Execute compiled Java code.

        Args:
            class_name: Name of the Java class to execute
            temp_dir: Directory containing compiled .class files

        Returns:
            Dictionary with execution results
        """
        try:
            # AIDEV-NOTE: Execute Java class
            run_result = subprocess.run(
                ["java", "-cp", temp_dir, class_name],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            return {
                "returncode": run_result.returncode,
                "stdout": run_result.stdout,
                "stderr": run_result.stderr
            }

        except subprocess.TimeoutExpired:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": f"Execution timed out after {self.timeout} seconds"
            }
        except Exception as e:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": f"Execution error: {str(e)}"
            }

    def _parse_compilation_error(self, error_output: str) -> List[str]:
        """
        Parse compilation error output into traceback lines.

        Args:
            error_output: Compiler error output

        Returns:
            List of formatted error lines
        """
        if not error_output:
            return []

        lines = error_output.strip().split('\n')
        traceback = []

        for line in lines:
            if line.strip():
                # AIDEV-NOTE: Clean up error messages
                cleaned_line = line.strip()
                if cleaned_line.startswith('error:'):
                    cleaned_line = cleaned_line[6:].strip()
                traceback.append(cleaned_line)

        return traceback

    def _create_error_output(self, error_name: str, error_message: str,
                           traceback: List[str]) -> JupyterError:
        """
        Create a Jupyter-compatible error output.

        Args:
            error_name: Name of the error type
            error_message: Error message
            traceback: List of traceback lines

        Returns:
            JupyterError output
        """
        return JupyterError(
            ename=error_name,
            evalue=error_message,
            traceback=traceback
        )

    def reset_execution_count(self) -> None:
        """Reset the execution count to 0."""
        self.execution_count = 0

    def get_execution_count(self) -> int:
        """Get current execution count."""
        return self.execution_count

    def validate_java_code(self, java_code: str) -> bool:
        """
        Validate that Java code can be compiled.

        Args:
            java_code: Java source code

        Returns:
            True if code appears valid
        """
        try:
            processed_code = self._prepare_code(java_code)
            self._extract_class_name(processed_code)
            return True
        except Exception:
            return False