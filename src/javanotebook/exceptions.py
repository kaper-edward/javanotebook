"""Custom exceptions for Java Notebook."""


class JavaNotebookError(Exception):
    """Base exception for all Java Notebook errors."""
    
    def __init__(self, message: str, details: str = None):
        super().__init__(message)
        self.message = message
        self.details = details


class CompilationError(JavaNotebookError):
    """Raised when Java code compilation fails."""
    
    def __init__(self, message: str, stderr: str = None, line_number: int = None):
        super().__init__(message)
        self.stderr = stderr
        self.line_number = line_number


class ExecutionError(JavaNotebookError):
    """Raised when Java code execution fails."""
    
    def __init__(self, message: str, stderr: str = None, return_code: int = None):
        super().__init__(message)
        self.stderr = stderr
        self.return_code = return_code


class ParseError(JavaNotebookError):
    """Raised when notebook file parsing fails."""
    
    def __init__(self, message: str, line_number: int = None):
        super().__init__(message)
        self.line_number = line_number


class JavaNotFoundError(JavaNotebookError):
    """Raised when Java JDK is not found or not accessible."""
    
    def __init__(self, message: str = "Java JDK not found. Please ensure Java is installed and accessible in PATH."):
        super().__init__(message)