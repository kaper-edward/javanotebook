"""FastAPI application for Java Notebook."""

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
import os
import json

from .routers import api
from .parser import NotebookParser
from .nb_parser import JupyterNotebookParser
from .format_detector import FormatDetector, NotebookFormat
from .exceptions import ParseError


def create_app(notebook_path: str = None, notebook_format: NotebookFormat = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="Java Notebook",
        description="A Jupyter-style notebook for Java code execution",
        version="0.1.0"
    )
    
    # AIDEV-NOTE: Get package directory for static files and templates
    package_dir = Path(__file__).parent
    static_dir = package_dir / "static"
    templates_dir = package_dir / "templates"
    
    # Mount static files
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # Setup templates
    templates = None
    if templates_dir.exists():
        templates = Jinja2Templates(directory=str(templates_dir))
    
    # Store notebook path and format in app state
    app.state.notebook_path = notebook_path
    app.state.notebook_format = notebook_format
    app.state.templates = templates
    
    # Include API router
    app.include_router(api.router, prefix="/api/v1")
    
    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        """Render the main notebook interface."""
        if not templates:
            return HTMLResponse("Templates not configured")
        
        if not app.state.notebook_path:
            return HTMLResponse("No notebook file specified")
        
        try:
            # AIDEV-NOTE: Parse notebook file using appropriate parser based on format
            notebook_format = app.state.notebook_format or FormatDetector.detect_format(app.state.notebook_path)

            if notebook_format == NotebookFormat.JUPYTER:
                parser = JupyterNotebookParser()
                notebook = parser.parse_file(app.state.notebook_path)

                # AIDEV-NOTE: Debug logging for notebook parsing
                print(f"[DEBUG] Parsed Jupyter notebook: {app.state.notebook_path}")
                print(f"[DEBUG] Total cells: {len(notebook.cells)}")

                # Check for duplicate cell IDs
                cell_ids = [cell.id for cell in notebook.cells]
                if len(cell_ids) != len(set(cell_ids)):
                    duplicates = [id for id in set(cell_ids) if cell_ids.count(id) > 1]
                    print(f"[WARNING] Duplicate cell IDs found: {duplicates}")
                else:
                    print(f"[DEBUG] All cell IDs are unique")

                # Get detailed statistics
                code_cells_count = len([cell for cell in notebook.cells if cell.cell_type == "code"])
                markdown_cells_count = len([cell for cell in notebook.cells if cell.cell_type == "markdown"])
                raw_cells_count = len([cell for cell in notebook.cells if cell.cell_type == "raw"])

                print(f"[DEBUG] Cell breakdown - Code: {code_cells_count}, Markdown: {markdown_cells_count}, Raw: {raw_cells_count}")
                print(f"[DEBUG] First 5 cell IDs: {[cell.id for cell in notebook.cells[:5]]}")

                # AIDEV-NOTE: Prepare JavaScript cell data separately to avoid template double-loop
                cell_data_for_js = []
                for cell in notebook.cells:
                    source_text = cell.source if isinstance(cell.source, str) else ''.join(cell.source)
                    # Escape quotes and newlines properly for JSON
                    cell_data_for_js.append({
                        "id": cell.id,
                        "type": cell.cell_type,
                        "index": len(cell_data_for_js),
                        "source": source_text,
                        "executionCount": cell.execution_count if cell.cell_type == "code" and hasattr(cell, 'execution_count') else None,
                        "metadata": cell.metadata if hasattr(cell, 'metadata') else {}
                    })

                return templates.TemplateResponse(
                    "jupyter_notebook.html",
                    {
                        "request": request,
                        "notebook": notebook,
                        "notebook_filename": Path(app.state.notebook_path).name,
                        "total_cells": len(notebook.cells),
                        "code_cells": len(notebook.code_cells),
                        "markdown_cells": len(notebook.markdown_cells),
                        "raw_cells": len(notebook.raw_cells),
                        "format": "ipynb",
                        "nbformat_version": f"{notebook.nbformat}.{notebook.nbformat_minor}",
                        "cell_data_json": json.dumps(cell_data_for_js)
                    }
                )
            else:
                # Default to markdown format
                parser = NotebookParser()
                notebook = parser.parse_file(app.state.notebook_path)

                return templates.TemplateResponse(
                    "notebook.html",
                    {
                        "request": request,
                        "notebook": notebook,
                        "notebook_filename": Path(app.state.notebook_path).name,
                        "total_cells": len(notebook.cells),
                        "code_cells": len(notebook.code_cells),
                        "markdown_cells": len(notebook.markdown_cells),
                        "raw_cells": 0,
                        "format": "md",
                        "nbformat_version": "N/A"
                    }
                )
        except ParseError as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse notebook: {e.message}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "Java Notebook"}
    
    return app


# AIDEV-NOTE: Create default app instance for uvicorn
app = create_app()