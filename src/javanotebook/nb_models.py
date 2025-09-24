"""Jupyter notebook models using nbformat."""

import uuid
from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field, validator
import nbformat
from nbformat import NotebookNode


# AIDEV-NOTE: JavaNotebook-specific metadata models for cell connections
class JavaNotebookMetadata(BaseModel):
    """Metadata schema for JavaNotebook-specific cell information."""

    project_group: Optional[str] = Field(None, description="ID of the project group this cell belongs to")
    execution_order: Optional[int] = Field(None, description="Order of execution within the group")
    is_main: bool = Field(False, description="Whether this cell contains the main class")
    package_name: Optional[str] = Field(None, description="Java package name extracted from the code")
    class_name: Optional[str] = Field(None, description="Main Java class name in this cell")


class CellConnectionRequest(BaseModel):
    """Request model for connecting two cells."""

    cell_id1: str = Field(..., description="ID of the first cell to connect")
    cell_id2: str = Field(..., description="ID of the second cell to connect")
    notebook_path: str = Field(..., description="Path to the notebook file")


class CellDisconnectionRequest(BaseModel):
    """Request model for disconnecting cells."""

    cell_id: str = Field(..., description="ID of the cell to disconnect from its group")
    notebook_path: str = Field(..., description="Path to the notebook file")


class ProjectGroupExecutionRequest(BaseModel):
    """Request model for executing a project group."""

    group_id: str = Field(..., description="ID of the project group to execute")
    notebook_path: str = Field(..., description="Path to the notebook file")


class ProjectGroupInfo(BaseModel):
    """Information about a project group."""

    group_id: str
    cell_ids: List[str]
    main_cell_id: Optional[str]
    execution_order: List[str]
    package_names: List[str]


class JupyterCell(BaseModel):
    """Base model for Jupyter notebook cells."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    cell_type: Literal["code", "markdown", "raw"]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source: Union[str, List[str]] = ""

    @validator('id')
    def validate_id(cls, v):
        """Validate cell ID according to Jupyter spec."""
        if not (1 <= len(v) <= 64):
            raise ValueError("Cell ID must be 1-64 characters long")
        if not all(c.isalnum() or c in '-_' for c in v):
            raise ValueError("Cell ID can only contain alphanumeric, -, and _ characters")
        return v

    @validator('source')
    def normalize_source(cls, v):
        """Normalize source to list of strings if needed."""
        if isinstance(v, str):
            return v.splitlines(True) if '\n' in v else [v]
        return v

    # AIDEV-NOTE: JavaNotebook-specific metadata helpers
    def get_javanotebook_metadata(self) -> Optional[JavaNotebookMetadata]:
        """Get JavaNotebook-specific metadata from cell metadata."""
        jn_metadata = self.metadata.get("javanotebook")
        if jn_metadata:
            try:
                return JavaNotebookMetadata(**jn_metadata)
            except Exception:
                return None
        return None

    def set_javanotebook_metadata(self, jn_metadata: JavaNotebookMetadata) -> None:
        """Set JavaNotebook-specific metadata in cell metadata."""
        self.metadata["javanotebook"] = jn_metadata.dict(exclude_none=True)

    def is_connected(self) -> bool:
        """Check if this cell is connected to a project group."""
        jn_meta = self.get_javanotebook_metadata()
        return jn_meta is not None and jn_meta.project_group is not None

    def get_project_group(self) -> Optional[str]:
        """Get the project group ID this cell belongs to."""
        jn_meta = self.get_javanotebook_metadata()
        return jn_meta.project_group if jn_meta else None


class JupyterMarkdownCell(JupyterCell):
    """Model for Jupyter markdown cells."""

    cell_type: Literal["markdown"] = "markdown"


class JupyterRawCell(JupyterCell):
    """Model for Jupyter raw cells."""

    cell_type: Literal["raw"] = "raw"


class JupyterOutput(BaseModel):
    """Base model for cell outputs."""

    output_type: Literal["execute_result", "display_data", "stream", "error"]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class JupyterExecuteResult(JupyterOutput):
    """Model for execution results."""

    output_type: Literal["execute_result"] = "execute_result"
    execution_count: Optional[int] = None
    data: Dict[str, Any] = Field(default_factory=dict)


class JupyterStream(JupyterOutput):
    """Model for stream outputs (stdout/stderr)."""

    output_type: Literal["stream"] = "stream"
    name: Literal["stdout", "stderr"] = "stdout"
    text: Union[str, List[str]] = ""


class JupyterError(JupyterOutput):
    """Model for error outputs."""

    output_type: Literal["error"] = "error"
    ename: str = ""
    evalue: str = ""
    traceback: List[str] = Field(default_factory=list)


class JupyterCodeCell(JupyterCell):
    """Model for Jupyter code cells."""

    cell_type: Literal["code"] = "code"
    execution_count: Optional[int] = None
    outputs: List[Union[JupyterExecuteResult, JupyterStream, JupyterError]] = Field(
        default_factory=list
    )


class JupyterNotebook(BaseModel):
    """Model representing a Jupyter notebook."""

    nbformat: int = 4
    nbformat_minor: int = 5
    metadata: Dict[str, Any] = Field(default_factory=dict)
    cells: List[Union[JupyterMarkdownCell, JupyterCodeCell, JupyterRawCell]] = Field(
        default_factory=list
    )

    def __init__(self, **data):
        """Initialize notebook with default metadata."""
        if 'metadata' not in data:
            data['metadata'] = self._default_metadata()
        super().__init__(**data)

    @staticmethod
    def _default_metadata() -> Dict[str, Any]:
        """Create default notebook metadata."""
        return {
            "kernelspec": {
                "display_name": "Java",
                "language": "java",
                "name": "java"
            },
            "language_info": {
                "name": "java",
                "version": "11",
                "mimetype": "text/x-java-source",
                "file_extension": ".java"
            }
        }

    @property
    def markdown_cells(self) -> List[JupyterMarkdownCell]:
        """Get all markdown cells."""
        return [cell for cell in self.cells if isinstance(cell, JupyterMarkdownCell)]

    @property
    def code_cells(self) -> List[JupyterCodeCell]:
        """Get all code cells."""
        return [cell for cell in self.cells if isinstance(cell, JupyterCodeCell)]

    @property
    def raw_cells(self) -> List[JupyterRawCell]:
        """Get all raw cells."""
        return [cell for cell in self.cells if isinstance(cell, JupyterRawCell)]

    # AIDEV-NOTE: Project group management methods
    def get_project_groups(self) -> Dict[str, ProjectGroupInfo]:
        """Get all project groups in this notebook."""
        groups: Dict[str, ProjectGroupInfo] = {}

        for cell in self.cells:
            if isinstance(cell, JupyterCodeCell) and cell.is_connected():
                group_id = cell.get_project_group()
                if group_id:
                    if group_id not in groups:
                        groups[group_id] = ProjectGroupInfo(
                            group_id=group_id,
                            cell_ids=[],
                            main_cell_id=None,
                            execution_order=[],
                            package_names=[]
                        )

                    groups[group_id].cell_ids.append(cell.id)
                    jn_meta = cell.get_javanotebook_metadata()
                    if jn_meta:
                        if jn_meta.is_main:
                            groups[group_id].main_cell_id = cell.id
                        if jn_meta.execution_order is not None:
                            groups[group_id].execution_order.append(cell.id)
                        if jn_meta.package_name:
                            groups[group_id].package_names.append(jn_meta.package_name)

        # Sort execution order by order value
        for group in groups.values():
            group.execution_order.sort(key=lambda cell_id: self._get_cell_execution_order(cell_id))

        return groups

    def _get_cell_execution_order(self, cell_id: str) -> int:
        """Get execution order for a cell."""
        for cell in self.cells:
            if cell.id == cell_id:
                jn_meta = cell.get_javanotebook_metadata()
                return jn_meta.execution_order if jn_meta and jn_meta.execution_order else 999
        return 999

    def get_cells_in_group(self, group_id: str) -> List[JupyterCodeCell]:
        """Get all code cells in a specific project group."""
        return [
            cell for cell in self.code_cells
            if cell.get_project_group() == group_id
        ]

    def find_cell_by_id(self, cell_id: str) -> Optional[JupyterCell]:
        """Find a cell by its ID."""
        for cell in self.cells:
            if cell.id == cell_id:
                return cell
        return None

    def to_notebook_node(self) -> NotebookNode:
        """Convert to nbformat NotebookNode."""
        # AIDEV-NOTE: Convert Pydantic models to nbformat structure
        nb_dict = {
            "nbformat": self.nbformat,
            "nbformat_minor": self.nbformat_minor,
            "metadata": self.metadata,
            "cells": []
        }

        for cell in self.cells:
            cell_dict = {
                "id": cell.id,
                "cell_type": cell.cell_type,
                "metadata": cell.metadata,
                "source": cell.source
            }

            if isinstance(cell, JupyterCodeCell):
                cell_dict["execution_count"] = cell.execution_count
                cell_dict["outputs"] = [
                    self._output_to_dict(output) for output in cell.outputs
                ]

            nb_dict["cells"].append(cell_dict)

        return nbformat.from_dict(nb_dict)

    @classmethod
    def from_notebook_node(cls, nb: NotebookNode) -> 'JupyterNotebook':
        """Create JupyterNotebook from nbformat NotebookNode."""
        # AIDEV-NOTE: Convert nbformat structure to Pydantic models
        cells = []
        used_ids = set()  # Track used cell IDs to prevent duplicates

        for cell_dict in nb.cells:
            # AIDEV-NOTE: Ensure unique cell ID
            original_id = cell_dict.get("id", str(uuid.uuid4())[:8])
            cell_id = original_id

            # If ID is already used, generate a new unique one
            while cell_id in used_ids:
                cell_id = str(uuid.uuid4())[:8]

            used_ids.add(cell_id)

            cell_data = {
                "id": cell_id,
                "metadata": cell_dict.get("metadata", {}),
                "source": cell_dict.get("source", "")
            }

            if cell_dict["cell_type"] == "markdown":
                cells.append(JupyterMarkdownCell(**cell_data))
            elif cell_dict["cell_type"] == "code":
                cell_data["execution_count"] = cell_dict.get("execution_count")
                cell_data["outputs"] = [
                    cls._dict_to_output(output_dict)
                    for output_dict in cell_dict.get("outputs", [])
                ]
                cells.append(JupyterCodeCell(**cell_data))
            elif cell_dict["cell_type"] == "raw":
                cells.append(JupyterRawCell(**cell_data))

        return cls(
            nbformat=nb.nbformat,
            nbformat_minor=nb.nbformat_minor,
            metadata=nb.metadata,
            cells=cells
        )

    @staticmethod
    def _output_to_dict(output: JupyterOutput) -> Dict[str, Any]:
        """Convert output model to dictionary."""
        output_dict = output.dict()
        return output_dict

    @staticmethod
    def _dict_to_output(output_dict: Dict[str, Any]) -> JupyterOutput:
        """Convert dictionary to output model."""
        output_type = output_dict["output_type"]

        if output_type == "execute_result":
            return JupyterExecuteResult(**output_dict)
        elif output_type == "stream":
            return JupyterStream(**output_dict)
        elif output_type == "error":
            return JupyterError(**output_dict)
        else:
            # Fallback for unknown output types
            return JupyterExecuteResult(**output_dict)


class JupyterExecutionRequest(BaseModel):
    """Request model for Jupyter code execution."""

    code: str = Field(..., description="Java code to execute")
    cell_id: Optional[str] = Field(None, description="ID of the cell being executed")
    execution_count: Optional[int] = Field(None, description="Execution count")


class JupyterExecutionResult(BaseModel):
    """Response model for Jupyter code execution results."""

    success: bool
    execution_count: int
    outputs: List[Union[JupyterExecuteResult, JupyterStream, JupyterError]] = Field(
        default_factory=list
    )
    execution_time: Optional[float] = None
    error_message: Optional[str] = None


class JupyterNotebookInfo(BaseModel):
    """Basic information about a Jupyter notebook."""

    filename: str
    title: Optional[str] = None
    total_cells: int
    code_cells_count: int
    markdown_cells_count: int
    raw_cells_count: int
    nbformat_version: str
    kernel_name: Optional[str] = None
    language: Optional[str] = None