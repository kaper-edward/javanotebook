"""Jupyter notebook models using nbformat."""

import uuid
from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field, validator
import nbformat
from nbformat import NotebookNode


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