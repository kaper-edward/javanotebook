"""Java code execution engine for Java Notebook."""

import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, Any

from .models import ExecutionResult
from .exceptions import CompilationError, ExecutionError, JavaNotFoundError
from .parser import NotebookParser


class JavaExecutor:
    """Handles compilation and execution of Java code."""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
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
            raise JavaNotFoundError()
    
    def wrap_code_with_main(self, java_code: str) -> str:
        """Wrap Java code with Main class and main method if needed."""
        # AIDEV-NOTE: Auto-wrap code without main method for quick testing
        
        # Check if code already has a main method
        if self.parser.has_main_method(java_code):
            return java_code
        
        # Check if code already has a class declaration
        import re
        if re.search(r'\bclass\s+\w+', java_code):
            # Code has a class but no main method - don't auto-wrap
            return java_code
        
        # Auto-wrap simple code with Main class and main method
        wrapped_code = f"""public class Main {{
    public static void main(String[] args) {{
        {java_code}
    }}
}}"""
        return wrapped_code

    async def execute_java_code(self, java_code: str) -> ExecutionResult:
        """Execute Java code and return results."""
        start_time = time.time()
        
        try:
            # AIDEV-NOTE: Auto-wrap code with main method if needed
            processed_code = self.wrap_code_with_main(java_code)
            
            # AIDEV-NOTE: Validate processed Java code structure
            if not self.parser.validate_java_code(processed_code):
                return ExecutionResult(
                    success=False,
                    error_message="Java code must contain a public class with a main method"
                )
            
            class_name = self.parser.extract_class_name(processed_code)
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # AIDEV-NOTE: Create temporary Java file
                java_file = Path(temp_dir) / f"{class_name}.java"
                java_file.write_text(processed_code, encoding='utf-8')
                
                # Compile Java code
                compile_result = await self._compile_java(java_file)
                if not compile_result["success"]:
                    return ExecutionResult(
                        success=False,
                        compilation_error=compile_result["stderr"],
                        execution_time=time.time() - start_time
                    )
                
                # Execute compiled Java code
                exec_result = await self._execute_java(temp_dir, class_name)
                
                return ExecutionResult(
                    success=exec_result["success"],
                    stdout=exec_result["stdout"],
                    stderr=exec_result["stderr"],
                    execution_time=time.time() - start_time,
                    error_message=exec_result.get("error_message")
                )
                
        except Exception as e:
            return ExecutionResult(
                success=False,
                error_message=f"Unexpected error: {str(e)}",
                execution_time=time.time() - start_time
            )
    
    async def _compile_java(self, java_file: Path) -> Dict[str, Any]:
        """Compile Java source file."""
        try:
            result = subprocess.run(
                ["javac", str(java_file)],
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
    
    async def _execute_java(self, class_dir: str, class_name: str) -> Dict[str, Any]:
        """Execute compiled Java class."""
        try:
            result = subprocess.run(
                ["java", "-cp", class_dir, class_name],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "error_message": result.stderr if result.returncode != 0 else None
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution timed out after {self.timeout} seconds",
                "returncode": -1,
                "error_message": f"Execution timed out after {self.timeout} seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution error: {str(e)}",
                "returncode": -1,
                "error_message": f"Execution error: {str(e)}"
            }