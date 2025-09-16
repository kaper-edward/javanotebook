"""Pydantic models for Java Notebook."""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class Cell(BaseModel):
    """Base model for notebook cells."""
    
    cell_type: Literal["markdown", "code"]
    content: str
    id: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class MarkdownCell(Cell):
    """Model for markdown cells."""
    
    cell_type: Literal["markdown"] = "markdown"


class JavaCodeCell(Cell):
    """Model for Java code cells."""
    
    cell_type: Literal["code"] = "code"
    language: Literal["java"] = "java"


class ExecutionRequest(BaseModel):
    """Request model for code execution."""
    
    code: str = Field(..., description="Java code to execute")
    cell_id: Optional[str] = Field(None, description="ID of the cell being executed")


class ExecutionResult(BaseModel):
    """Response model for code execution results."""
    
    success: bool
    stdout: str = ""
    stderr: str = ""
    execution_time: Optional[float] = None
    error_message: Optional[str] = None
    compilation_error: Optional[str] = None


class Notebook(BaseModel):
    """Model representing a complete notebook."""
    
    cells: List[Cell]
    metadata: dict = Field(default_factory=dict)
    
    @property
    def markdown_cells(self) -> List[MarkdownCell]:
        """Get all markdown cells."""
        return [cell for cell in self.cells if cell.cell_type == "markdown"]
    
    @property
    def code_cells(self) -> List[JavaCodeCell]:
        """Get all code cells."""
        return [cell for cell in self.cells if cell.cell_type == "code"]


class NotebookInfo(BaseModel):
    """Basic information about a notebook."""
    
    filename: str
    title: Optional[str] = None
    total_cells: int
    code_cells_count: int
    markdown_cells_count: int