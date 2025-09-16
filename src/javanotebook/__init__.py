"""Java Notebook - A Jupyter-style notebook for Java code execution."""

__version__ = "0.2.0"
__author__ = "Edward Kaper"
__email__ = "kaper.edward@gmail.com"

# AIDEV-NOTE: Package initialization for javanotebook
from .exceptions import JavaNotebookError, CompilationError, ExecutionError

__all__ = [
    "JavaNotebookError",
    "CompilationError", 
    "ExecutionError",
]