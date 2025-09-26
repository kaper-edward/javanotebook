"""Package management utilities for Java Notebook."""

import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass

from .parser import NotebookParser
from .exceptions import CompilationError, ParseError


@dataclass
class JavaClass:
    """Represents a Java class with package information."""
    code: str
    class_name: str
    package_name: str
    full_class_name: str
    file_path: str
    imports: List[str]
    has_main: bool


class PackageManager:
    """Manages Java packages and multi-class compilation."""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.parser = NotebookParser()

    def analyze_java_classes(self, java_codes: List[str]) -> List[JavaClass]:
        """Analyze Java code strings and extract class information."""
        classes = []

        for code in java_codes:
            if not code.strip():
                continue

            try:
                # AIDEV-NOTE: Extract all class information using parser
                class_name = self.parser.extract_class_name(code)
                package_name = self.parser.extract_package_name(code)
                full_class_name = self.parser.get_full_class_name(code)
                imports = self.parser.extract_imports(code)
                has_main = self.parser.has_main_method(code)

                # AIDEV-NOTE: Generate file path based on package structure
                package_path = self.parser.get_package_path(package_name)
                file_path = f"{package_path}/{class_name}.java" if package_path else f"{class_name}.java"

                classes.append(JavaClass(
                    code=code,
                    class_name=class_name,
                    package_name=package_name,
                    full_class_name=full_class_name,
                    file_path=file_path,
                    imports=imports,
                    has_main=has_main
                ))

            except ParseError as e:
                # AIDEV-NOTE: Skip invalid Java code with error logging
                print(f"Warning: Skipping invalid Java code: {str(e)}")
                continue

        return classes

    def create_package_structure(self, classes: List[JavaClass], base_dir: Path) -> None:
        """Create package directory structure and write Java files."""
        for java_class in classes:
            file_path = base_dir / java_class.file_path

            # AIDEV-NOTE: Create package directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # AIDEV-NOTE: Write Java source file
            file_path.write_text(java_class.code, encoding='utf-8')

    def compile_all_classes(self, base_dir: Path, classes: List[JavaClass]) -> Dict[str, any]:
        """Compile all Java classes with proper package support."""
        try:
            # AIDEV-NOTE: Get all Java files for compilation
            java_files = [str(base_dir / java_class.file_path) for java_class in classes]

            if not java_files:
                return {
                    "success": False,
                    "error": "No Java files to compile",
                    "stdout": "",
                    "stderr": ""
                }

            # AIDEV-NOTE: Compile all Java files with package support
            compile_cmd = [
                "javac",
                "-d", str(base_dir),           # Output directory (creates package structure)
                "-cp", str(base_dir),          # Classpath includes compiled classes
                "-sourcepath", str(base_dir)   # Source path for dependency resolution
            ] + java_files

            result = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Compilation timed out after {self.timeout} seconds",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Compilation error: {str(e)}",
                "returncode": -1
            }

    def find_main_class(self, classes: List[JavaClass]) -> Optional[JavaClass]:
        """Find the class with main method."""
        main_classes = [cls for cls in classes if cls.has_main]

        if not main_classes:
            return None
        elif len(main_classes) == 1:
            return main_classes[0]
        else:
            # AIDEV-NOTE: If multiple main methods, prefer the last one (most recent cell)
            return main_classes[-1]

    def execute_main_class(self, base_dir: Path, main_class: JavaClass) -> Dict[str, any]:
        """Execute the main class with proper package support."""
        try:
            # AIDEV-NOTE: Execute with full class name including package
            execute_cmd = [
                "java",
                "-cp", str(base_dir),
                main_class.full_class_name
            ]

            result = subprocess.run(
                execute_cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "executed_class": main_class.full_class_name
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution timed out after {self.timeout} seconds",
                "returncode": -1,
                "executed_class": main_class.full_class_name
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution error: {str(e)}",
                "returncode": -1,
                "executed_class": main_class.full_class_name
            }

    def validate_dependencies(self, classes: List[JavaClass]) -> List[str]:
        """Validate that all imported classes are available."""
        available_classes = {cls.full_class_name for cls in classes}
        missing_dependencies = []

        for java_class in classes:
            for import_stmt in java_class.imports:
                # AIDEV-NOTE: Skip standard Java library imports
                if (import_stmt.startswith('java.') or
                    import_stmt.startswith('javax.') or
                    import_stmt.endswith('.*')):
                    continue

                # AIDEV-NOTE: Check if imported class is available
                if import_stmt not in available_classes:
                    missing_dependencies.append(
                        f"Class '{java_class.full_class_name}' imports '{import_stmt}' but it's not available"
                    )

        return missing_dependencies

    def process_multi_class_execution(self, java_codes: List[str]) -> Dict[str, any]:
        """Process multiple Java classes and execute the one with main method."""
        # AIDEV-NOTE: Analyze all Java classes
        classes = self.analyze_java_classes(java_codes)

        if not classes:
            return {
                "success": False,
                "error": "No valid Java classes found",
                "stdout": "",
                "stderr": ""
            }

        # AIDEV-NOTE: Validate dependencies
        missing_deps = self.validate_dependencies(classes)
        if missing_deps:
            return {
                "success": False,
                "error": "Missing dependencies: " + "; ".join(missing_deps),
                "stdout": "",
                "stderr": ""
            }

        # AIDEV-NOTE: Find main class
        main_class = self.find_main_class(classes)
        if not main_class:
            return {
                "success": False,
                "error": "No main method found in any class",
                "stdout": "",
                "stderr": ""
            }

        # AIDEV-NOTE: Create temporary directory and compile
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)

            # Create package structure
            self.create_package_structure(classes, base_dir)

            # Compile all classes
            compile_result = self.compile_all_classes(base_dir, classes)
            if not compile_result["success"]:
                return {
                    "success": False,
                    "error": "Compilation failed",
                    "compilation_error": compile_result["stderr"],
                    "stdout": compile_result["stdout"],
                    "stderr": compile_result["stderr"]
                }

            # Execute main class
            exec_result = self.execute_main_class(base_dir, main_class)

            return {
                "success": exec_result["success"],
                "stdout": exec_result["stdout"],
                "stderr": exec_result["stderr"],
                "executed_class": exec_result["executed_class"],
                "compiled_classes": [cls.full_class_name for cls in classes]
            }