"""API endpoints for Java Notebook."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any

from ..models import ExecutionRequest, ExecutionResult, NotebookInfo
from ..nb_models import (
    JupyterExecutionRequest, JupyterExecutionResult, JupyterNotebookInfo,
    CellConnectionRequest, CellDisconnectionRequest, ProjectGroupExecutionRequest,
    JavaNotebookMetadata, ProjectGroupInfo, JupyterNotebookSaveRequest, JupyterNotebookSaveResult,
    CompleteCellData
)
from ..executor import JavaExecutor
from ..nb_executor import JupyterJavaExecutor
from ..project_executor import ProjectExecutor
from ..parser import NotebookParser
from ..nb_parser import JupyterNotebookParser
from ..format_detector import FormatDetector, NotebookFormat
from ..exceptions import JavaNotebookError, JavaNotFoundError
import nbformat
import uuid
import re
import shutil
import tempfile
from pathlib import Path


router = APIRouter()

# AIDEV-NOTE: Global executor instances
executor = JavaExecutor()
jupyter_executor = JupyterJavaExecutor()
project_executor = ProjectExecutor()


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


# AIDEV-NOTE: Cell connection management endpoints
@router.post("/jupyter/cells/connect")
async def connect_cells(request: CellConnectionRequest) -> Dict[str, Any]:
    """Connect two cells into a project group."""
    try:
        notebook_path = Path(request.notebook_path)
        if not notebook_path.exists():
            raise HTTPException(status_code=404, detail="Notebook file not found")

        # Read notebook using nbformat
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)

        # Find the cells to connect
        cell1 = None
        cell2 = None
        for cell in nb.cells:
            if cell.get('id') == request.cell_id1:
                cell1 = cell
            elif cell.get('id') == request.cell_id2:
                cell2 = cell

        if not cell1 or not cell2:
            raise HTTPException(status_code=404, detail="One or both cells not found")

        # Only connect code cells
        if cell1.get('cell_type') != 'code' or cell2.get('cell_type') != 'code':
            raise HTTPException(status_code=400, detail="Only code cells can be connected")

        # Generate or use existing project group ID
        group_id = None

        # Check if either cell is already connected
        existing_group1 = cell1.get('metadata', {}).get('javanotebook', {}).get('project_group')
        existing_group2 = cell2.get('metadata', {}).get('javanotebook', {}).get('project_group')

        if existing_group1:
            group_id = existing_group1
        elif existing_group2:
            group_id = existing_group2
        else:
            group_id = str(uuid.uuid4())

        # Extract Java package and class information
        def extract_java_info(cell):
            source = ''.join(cell.get('source', []))
            package_match = re.search(r'package\s+([a-zA-Z0-9_.]+)\s*;', source)
            class_match = re.search(r'public\s+class\s+(\w+)', source)
            main_match = re.search(r'public\s+static\s+void\s+main\s*\(\s*String\s*\[\s*\]\s*\w*\s*\)', source)

            return {
                'package_name': package_match.group(1) if package_match else None,
                'class_name': class_match.group(1) if class_match else None,
                'is_main': bool(main_match)
            }

        # Set metadata for both cells
        for i, cell in enumerate([cell1, cell2]):
            if 'metadata' not in cell:
                cell['metadata'] = {}
            if 'javanotebook' not in cell['metadata']:
                cell['metadata']['javanotebook'] = {}

            java_info = extract_java_info(cell)
            cell['metadata']['javanotebook'].update({
                'project_group': group_id,
                'execution_order': i,
                'is_main': java_info['is_main'],
                'package_name': java_info['package_name'],
                'class_name': java_info['class_name']
            })

        # Save notebook
        with open(notebook_path, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)

        return {
            "success": True,
            "group_id": group_id,
            "connected_cells": [request.cell_id1, request.cell_id2],
            "message": "Cells connected successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection failed: {str(e)}")


@router.post("/jupyter/cells/disconnect")
async def disconnect_cell(request: CellDisconnectionRequest) -> Dict[str, Any]:
    """Disconnect a cell from its project group."""
    try:
        notebook_path = Path(request.notebook_path)
        if not notebook_path.exists():
            raise HTTPException(status_code=404, detail="Notebook file not found")

        # Read notebook using nbformat
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)

        # Find the cell to disconnect
        target_cell = None
        for cell in nb.cells:
            if cell.get('id') == request.cell_id:
                target_cell = cell
                break

        if not target_cell:
            raise HTTPException(status_code=404, detail="Cell not found")

        # Get the current group ID
        old_group_id = target_cell.get('metadata', {}).get('javanotebook', {}).get('project_group')

        if not old_group_id:
            return {
                "success": True,
                "message": "Cell was not connected to any group"
            }

        # Remove JavaNotebook metadata
        if 'metadata' in target_cell and 'javanotebook' in target_cell['metadata']:
            del target_cell['metadata']['javanotebook']
            # Clean up empty metadata
            if not target_cell['metadata']:
                del target_cell['metadata']

        # Check if this was the last cell in the group
        remaining_cells = []
        for cell in nb.cells:
            if (cell.get('metadata', {}).get('javanotebook', {}).get('project_group') == old_group_id
                and cell.get('id') != request.cell_id):
                remaining_cells.append(cell.get('id'))

        # If only one cell remains, disconnect it too
        if len(remaining_cells) == 1:
            for cell in nb.cells:
                if cell.get('id') == remaining_cells[0]:
                    if 'metadata' in cell and 'javanotebook' in cell['metadata']:
                        del cell['metadata']['javanotebook']
                        if not cell['metadata']:
                            del cell['metadata']
                    break

        # Save notebook
        with open(notebook_path, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)

        return {
            "success": True,
            "disconnected_cell": request.cell_id,
            "old_group_id": old_group_id,
            "remaining_cells_in_group": remaining_cells if len(remaining_cells) > 1 else [],
            "message": "Cell disconnected successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Disconnection failed: {str(e)}")


@router.get("/jupyter/groups/{notebook_path:path}")
async def get_project_groups(notebook_path: str) -> Dict[str, Any]:
    """Get all project groups in a notebook."""
    try:
        notebook_file = Path(notebook_path)
        if not notebook_file.exists():
            raise HTTPException(status_code=404, detail="Notebook file not found")

        parser = JupyterNotebookParser()
        notebook = parser.parse_file(str(notebook_file))
        groups = notebook.get_project_groups()

        return {
            "notebook_path": notebook_path,
            "groups": {group_id: group.dict() for group_id, group in groups.items()},
            "total_groups": len(groups)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project groups: {str(e)}")


@router.post("/jupyter/groups/execute", response_model=JupyterExecutionResult)
async def execute_project_group(request: ProjectGroupExecutionRequest):
    """Execute all cells in a project group together."""
    try:
        result = project_executor.execute_project_group(request.notebook_path, request.group_id)
        return result
    except JavaNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except JavaNotebookError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Project execution failed: {str(e)}")


@router.post("/jupyter/save", response_model=JupyterNotebookSaveResult)
async def save_jupyter_notebook(request: JupyterNotebookSaveRequest):
    """Save Jupyter notebook with complete cell data reconstruction."""
    backup_path = None
    try:
        notebook_path = Path(request.notebook_path)

        # Check if notebook file exists
        if not notebook_path.exists():
            raise HTTPException(status_code=404, detail="Notebook file not found")

        # AIDEV-NOTE: Create backup for atomic save
        backup_path = Path(tempfile.mktemp(suffix='.ipynb.backup'))
        shutil.copy2(notebook_path, backup_path)

        # AIDEV-NOTE: Load existing notebook to preserve metadata
        parser = JupyterNotebookParser()
        original_notebook = parser.parse_file(str(notebook_path))

        # AIDEV-NOTE: Create completely new notebook from frontend data
        from ..nb_models import (
            JupyterNotebook, JupyterCodeCell, JupyterMarkdownCell, JupyterRawCell,
            JupyterStream, JupyterError, JupyterExecuteResult
        )

        new_notebook = JupyterNotebook()

        # Preserve original notebook metadata if requested
        if request.preserve_metadata:
            new_notebook.metadata = original_notebook.metadata
            new_notebook.nbformat = original_notebook.nbformat
            new_notebook.nbformat_minor = original_notebook.nbformat_minor

        # AIDEV-NOTE: Rebuild all cells from frontend data
        created_cells_count = 0

        for cell_data in request.cells_data:
            try:
                # Normalize source
                source = cell_data.source
                if isinstance(source, str):
                    source = source.splitlines(True) if '\n' in source else [source]

                # Create appropriate cell type
                if cell_data.cell_type == "code":
                    new_cell = JupyterCodeCell(
                        id=cell_data.id,
                        source=source,
                        metadata=cell_data.metadata,
                        execution_count=cell_data.execution_count
                    )

                    # AIDEV-NOTE: Reconstruct outputs from frontend data
                    for output_data in cell_data.outputs:
                        output_type = output_data.get("output_type")
                        if output_type == "stream":
                            output = JupyterStream(**output_data)
                        elif output_type == "error":
                            output = JupyterError(**output_data)
                        elif output_type == "execute_result":
                            output = JupyterExecuteResult(**output_data)
                        else:
                            continue
                        new_cell.outputs.append(output)

                elif cell_data.cell_type == "markdown":
                    new_cell = JupyterMarkdownCell(
                        id=cell_data.id,
                        source=source,
                        metadata=cell_data.metadata
                    )

                elif cell_data.cell_type == "raw":
                    new_cell = JupyterRawCell(
                        id=cell_data.id,
                        source=source,
                        metadata=cell_data.metadata
                    )

                else:
                    raise ValueError(f"Unknown cell type: {cell_data.cell_type}")

                new_notebook.cells.append(new_cell)
                created_cells_count += 1

            except Exception as e:
                raise ValueError(f"Failed to create cell {cell_data.id}: {str(e)}")

        # AIDEV-NOTE: Validate the reconstructed notebook
        try:
            nb_node = new_notebook.to_notebook_node()
            nbformat.validate(nb_node)
        except Exception as e:
            raise ValueError(f"Notebook validation failed: {str(e)}")

        # AIDEV-NOTE: Atomic save - write to temp file first
        temp_path = Path(tempfile.mktemp(suffix='.ipynb.tmp'))
        try:
            parser.save_notebook(new_notebook, str(temp_path))

            # Verify the saved file
            test_notebook = parser.parse_file(str(temp_path))
            if len(test_notebook.cells) != created_cells_count:
                raise ValueError(f"Save verification failed: expected {created_cells_count} cells, got {len(test_notebook.cells)}")

            # Move temp file to actual location
            shutil.move(temp_path, notebook_path)

            # Clean up backup
            if backup_path and backup_path.exists():
                backup_path.unlink()

            return JupyterNotebookSaveResult(
                success=True,
                message=f"노트북이 성공적으로 재구성되어 저장되었습니다. {created_cells_count}개 셀이 처리되었습니다.",
                saved_cells_count=created_cells_count,
                file_path=str(notebook_path)
            )

        except Exception as e:
            # Clean up temp file
            if temp_path.exists():
                temp_path.unlink()
            raise e

    except Exception as e:
        # AIDEV-NOTE: Restore backup on any failure
        if backup_path and backup_path.exists():
            try:
                shutil.move(backup_path, notebook_path)
            except Exception as restore_error:
                raise HTTPException(
                    status_code=500,
                    detail=f"Save failed and backup restore failed: {str(e)} | Restore error: {str(restore_error)}"
                )

        # Handle specific error types
        if isinstance(e, ValueError):
            raise HTTPException(status_code=400, detail=f"Data validation error: {str(e)}")
        elif isinstance(e, FileNotFoundError):
            raise HTTPException(status_code=404, detail="Notebook file not found")
        elif isinstance(e, PermissionError):
            raise HTTPException(status_code=403, detail="Permission denied: Cannot write to notebook file")
        else:
            raise HTTPException(status_code=500, detail=f"Save failed: {str(e)}")

    finally:
        # Clean up backup file
        if backup_path and backup_path.exists():
            try:
                backup_path.unlink()
            except:
                pass