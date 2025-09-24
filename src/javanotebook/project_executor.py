"""Project-based Java execution engine for connected cells."""

import subprocess
import tempfile
import time
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import nbformat

from .nb_models import JupyterExecutionResult, JupyterStream, JupyterError
from .exceptions import CompilationError, ExecutionError, JavaNotFoundError


class ProjectExecutor:
    """Handles compilation and execution of connected Java code cells as a project."""

    def __init__(self, timeout: int = 30):
        """
        Initialize the project executor.

        Args:
            timeout: Maximum execution time in seconds
        """
        self.timeout = timeout
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

    def execute_project_group(self, notebook_path: str, group_id: str) -> JupyterExecutionResult:
        """
        Execute all cells in a project group together.

        Args:
            notebook_path: Path to the notebook file
            group_id: ID of the project group to execute

        Returns:
            JupyterExecutionResult with combined outputs
        """
        start_time = time.time()

        try:
            # Read notebook
            with open(notebook_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)

            # Collect cells in the group
            group_cells = []
            for cell in nb.cells:
                if (cell.get('cell_type') == 'code' and
                    cell.get('metadata', {}).get('javanotebook', {}).get('project_group') == group_id):
                    group_cells.append(cell)

            if not group_cells:
                return JupyterExecutionResult(
                    success=False,
                    execution_count=0,
                    outputs=[self._create_error_output(
                        "ProjectError",
                        f"No cells found in project group: {group_id}",
                        []
                    )],
                    execution_time=time.time() - start_time,
                    error_message=f"Project group {group_id} not found"
                )

            # Sort cells by execution order
            group_cells.sort(key=lambda c: c.get('metadata', {}).get('javanotebook', {}).get('execution_order', 999))

            # AIDEV-NOTE: Execute project in temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                compilation_result = self._compile_project_in_dir(group_cells, temp_dir)
                if not compilation_result["success"]:
                    return JupyterExecutionResult(
                        success=False,
                        execution_count=0,
                        outputs=[self._create_error_output(
                            "CompilationError",
                            compilation_result["error"],
                            compilation_result.get("traceback", [])
                        )],
                        execution_time=time.time() - start_time,
                        error_message=compilation_result["error"]
                    )

                # Execute the main class
                execution_result = self._execute_main_class(
                    compilation_result["main_class"],
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
                execution_count=0,  # Project execution doesn't have execution count
                outputs=outputs,
                execution_time=time.time() - start_time
            )

        except Exception as e:
            return JupyterExecutionResult(
                success=False,
                execution_count=0,
                outputs=[self._create_error_output(
                    type(e).__name__,
                    str(e),
                    []
                )],
                execution_time=time.time() - start_time,
                error_message=str(e)
            )

    def _compile_project_in_dir(self, cells: List[Dict], temp_dir: str) -> Dict[str, Any]:
        """
        Compile all Java cells in the project directory with proper package structure.

        Args:
            cells: List of code cells in the project
            temp_dir: Directory to compile in

        Returns:
            Dictionary with compilation results
        """
        try:
            java_files = []
            main_class = None

            # AIDEV-NOTE: Create Java files with proper package directory structure
            for cell in cells:
                source = ''.join(cell.get('source', []))
                if not source.strip():
                    continue

                # Extract package and class information
                package_match = re.search(r'package\s+([a-zA-Z0-9_.]+)\s*;', source)
                class_match = re.search(r'public\s+class\s+(\w+)', source)
                main_match = re.search(r'public\s+static\s+void\s+main\s*\(\s*String\s*\[\s*\]\s*\w*\s*\)', source)

                if not class_match:
                    continue  # Skip cells without a proper class declaration

                class_name = class_match.group(1)
                package_name = package_match.group(1) if package_match else None

                # Determine the main class
                if main_match:
                    if package_name:
                        main_class = f"{package_name}.{class_name}"
                    else:
                        main_class = class_name

                # Create package directory structure
                if package_name:
                    package_dir = Path(temp_dir) / Path(*package_name.split('.'))
                    package_dir.mkdir(parents=True, exist_ok=True)
                    java_file = package_dir / f"{class_name}.java"
                else:
                    java_file = Path(temp_dir) / f"{class_name}.java"

                # Write Java source file
                java_file.write_text(source, encoding='utf-8')
                java_files.append(str(java_file))

            if not java_files:
                return {
                    "success": False,
                    "error": "No valid Java classes found in project group",
                    "traceback": []
                }

            if not main_class:
                return {
                    "success": False,
                    "error": "No main class found in project group",
                    "traceback": []
                }

            # AIDEV-NOTE: Compile all Java files together with sourcepath for package dependencies
            compile_result = subprocess.run(
                ["javac", "-d", temp_dir, "-cp", temp_dir, "-sourcepath", temp_dir] + java_files,
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
                "main_class": main_class,
                "java_files": java_files
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

    def _execute_main_class(self, main_class: str, temp_dir: str) -> Dict[str, Any]:
        """
        Execute the main class.

        Args:
            main_class: Fully qualified name of the main class
            temp_dir: Directory containing compiled .class files

        Returns:
            Dictionary with execution results
        """
        try:
            # AIDEV-NOTE: Execute Java class with proper classpath
            run_result = subprocess.run(
                ["java", "-cp", temp_dir, main_class],
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
        Parse compilation error output into user-friendly traceback lines.

        Args:
            error_output: Compiler error output

        Returns:
            List of user-friendly error messages
        """
        if not error_output:
            return []

        lines = error_output.strip().split('\n')
        user_friendly_errors = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # AIDEV-NOTE: Convert technical errors to user-friendly messages
            if 'cannot find symbol' in line.lower():
                if 'class' in line.lower():
                    user_friendly_errors.append("❌ 클래스를 찾을 수 없습니다. import 문이나 패키지 선언을 확인하세요.")
                elif 'method' in line.lower():
                    user_friendly_errors.append("❌ 메서드를 찾을 수 없습니다. 메서드 이름과 매개변수를 확인하세요.")
                else:
                    user_friendly_errors.append("❌ 변수나 식별자를 찾을 수 없습니다. 철자와 선언을 확인하세요.")

            elif 'package does not exist' in line.lower():
                user_friendly_errors.append("📦 패키지가 존재하지 않습니다. package 선언과 폴더 구조를 확인하세요.")

            elif 'duplicate class' in line.lower():
                user_friendly_errors.append("🔄 동일한 이름의 클래스가 중복됩니다. 클래스 이름을 변경하세요.")

            elif 'illegal start of expression' in line.lower():
                user_friendly_errors.append("⚠️ 잘못된 문법입니다. 중괄호 { } 나 세미콜론 ; 을 확인하세요.")

            elif 'incompatible types' in line.lower():
                user_friendly_errors.append("🔧 타입이 맞지 않습니다. 변수 타입과 값의 타입을 확인하세요.")

            elif 'unreachable statement' in line.lower():
                user_friendly_errors.append("🚫 도달할 수 없는 코드입니다. return 문 이후의 코드를 확인하세요.")

            else:
                # AIDEV-NOTE: For unrecognized errors, clean up but keep original message
                cleaned_line = line
                if cleaned_line.startswith('error:'):
                    cleaned_line = cleaned_line[6:].strip()
                user_friendly_errors.append(f"⚡ {cleaned_line}")

        return user_friendly_errors if user_friendly_errors else ["❓ 컴파일 중 알 수 없는 오류가 발생했습니다."]

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