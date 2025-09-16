"""FastAPI application for Java Notebook."""

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
import os

from .routers import api
from .parser import NotebookParser
from .exceptions import ParseError


def create_app(notebook_path: str = None) -> FastAPI:
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
    
    # Store notebook path in app state
    app.state.notebook_path = notebook_path
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
            # AIDEV-NOTE: Parse notebook file and render template
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
                    "markdown_cells": len(notebook.markdown_cells)
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