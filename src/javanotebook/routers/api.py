"""API endpoints for Java Notebook."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any

from ..models import ExecutionRequest, ExecutionResult, NotebookInfo
from ..executor import JavaExecutor
from ..parser import NotebookParser
from ..exceptions import JavaNotebookError, JavaNotFoundError


router = APIRouter()

# AIDEV-NOTE: Global executor instance
executor = JavaExecutor()


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