"""API endpoints for Java Notebook."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any

from ..models import ExecutionRequest, ExecutionResult, NotebookInfo
from ..nb_models import (
    JupyterExecutionRequest, JupyterExecutionResult, JupyterNotebookInfo
)
from ..executor import JavaExecutor
from ..nb_executor import JupyterJavaExecutor
from ..parser import NotebookParser
from ..nb_parser import JupyterNotebookParser
from ..format_detector import FormatDetector, NotebookFormat
from ..exceptions import JavaNotebookError, JavaNotFoundError


router = APIRouter()

# AIDEV-NOTE: Global executor instances
executor = JavaExecutor()
jupyter_executor = JupyterJavaExecutor()


@router.post("/execute", response_model=ExecutionResult)
async def execute_java_code(request: ExecutionRequest):
    """Execute Java code and return results."""
    try:
        result = await executor.execute_java_code(request.code)
        return result
    except JavaNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except JavaNotebookError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


@router.get("/notebook/info", response_model=NotebookInfo)
async def get_notebook_info(notebook_path: str):
    """Get basic information about a notebook file."""
    try:
        parser = NotebookParser()
        notebook = parser.parse_file(notebook_path)
        
        return NotebookInfo(
            filename=notebook_path,
            total_cells=len(notebook.cells),
            code_cells_count=len(notebook.code_cells),
            markdown_cells_count=len(notebook.markdown_cells)
        )
    except JavaNotebookError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get notebook info: {str(e)}")


@router.post("/validate")
async def validate_java_code(request: ExecutionRequest) -> Dict[str, Any]:
    """Validate Java code structure without executing it."""
    try:
        parser = NotebookParser()
        
        # Extract class name
        try:
            class_name = parser.extract_class_name(request.code)
        except Exception:
            class_name = None
        
        # Check for main method
        has_main = parser.has_main_method(request.code)
        
        # Overall validation
        is_valid = parser.validate_java_code(request.code)
        
        return {
            "valid": is_valid,
            "class_name": class_name,
            "has_main_method": has_main,
            "errors": [] if is_valid else ["Java code must contain a public class with a main method"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("/health")
async def health_check():
    """API health check."""
    try:
        # AIDEV-NOTE: Verify Java is still available
        executor._verify_java_installation()
        return {"status": "healthy", "java_available": True}
    except JavaNotFoundError:
        return {"status": "degraded", "java_available": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


# AIDEV-NOTE: Jupyter notebook specific endpoints
@router.post("/jupyter/execute", response_model=JupyterExecutionResult)
async def execute_jupyter_code(request: JupyterExecutionRequest):
    """Execute Java code with Jupyter-compatible output format."""
    try:
        result = jupyter_executor.execute_code(request)
        return result
    except JavaNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except JavaNotebookError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


@router.get("/jupyter/notebook/info", response_model=JupyterNotebookInfo)
async def get_jupyter_notebook_info(notebook_path: str):
    """Get information about a Jupyter notebook file."""
    try:
        parser = JupyterNotebookParser()
        info = parser.get_notebook_info(notebook_path)
        return info
    except JavaNotebookError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get notebook info: {str(e)}")


@router.post("/jupyter/validate")
async def validate_jupyter_code(request: JupyterExecutionRequest) -> Dict[str, Any]:
    """Validate Java code for Jupyter notebook."""
    try:
        parser = JupyterNotebookParser()

        # Extract class name
        try:
            class_name = parser.extract_class_name(request.code)
        except Exception:
            class_name = None

        # Check for main method
        has_main = parser.has_main_method(request.code)

        # Overall validation
        is_valid = parser.validate_java_code(request.code)

        # Check if code can be auto-wrapped
        can_auto_wrap = False
        if not has_main and not class_name:
            can_auto_wrap = True

        return {
            "valid": is_valid,
            "class_name": class_name,
            "has_main_method": has_main,
            "can_auto_wrap": can_auto_wrap,
            "processed_code": parser.wrap_code_with_main(request.code) if can_auto_wrap else request.code,
            "errors": [] if is_valid else ["Invalid Java code structure"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.post("/jupyter/convert/md-to-ipynb")
async def convert_md_to_ipynb(md_content: str) -> Dict[str, Any]:
    """Convert markdown content to Jupyter notebook format."""
    try:
        parser = JupyterNotebookParser()
        notebook = parser.convert_from_markdown(md_content)

        return {
            "notebook": notebook.dict(),
            "cells_count": len(notebook.cells),
            "format": "ipynb"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


@router.post("/jupyter/convert/ipynb-to-md")
async def convert_ipynb_to_md(notebook_path: str) -> Dict[str, Any]:
    """Convert Jupyter notebook to markdown format."""
    try:
        parser = JupyterNotebookParser()
        notebook = parser.parse_file(notebook_path)
        md_content = parser.convert_to_markdown(notebook)

        return {
            "markdown": md_content,
            "cells_count": len(notebook.cells),
            "format": "md"
        }
    except JavaNotebookError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


@router.get("/jupyter/execution/reset")
async def reset_jupyter_execution():
    """Reset Jupyter execution count."""
    try:
        jupyter_executor.reset_execution_count()
        return {
            "status": "success",
            "execution_count": jupyter_executor.get_execution_count(),
            "message": "Execution count reset to 0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")


@router.get("/format/detect")
async def detect_notebook_format(file_path: str) -> Dict[str, Any]:
    """Detect notebook file format."""
    try:
        format_type = FormatDetector.detect_format(file_path)

        return {
            "file_path": file_path,
            "detected_format": format_type.value,
            "supported_formats": ["md", "ipynb"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Format detection failed: {str(e)}")