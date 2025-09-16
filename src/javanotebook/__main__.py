"""Command-line interface for Java Notebook."""

import argparse
import asyncio
import webbrowser
from pathlib import Path
import uvicorn

from .main import create_app


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Java Notebook - A Jupyter-style notebook for Java code execution"
    )
    
    parser.add_argument(
        "notebook",
        help="Path to the notebook file (.md)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the server on (default: 8000)"
    )
    
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind the server to (default: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't automatically open browser"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    args = parser.parse_args()
    
    # Validate notebook file
    notebook_path = Path(args.notebook)
    if not notebook_path.exists():
        print(f"Error: Notebook file not found: {args.notebook}")
        return 1
    
    if not notebook_path.suffix.lower() == ".md":
        print(f"Warning: Expected .md file, got {notebook_path.suffix}")
    
    # AIDEV-NOTE: Create FastAPI app with notebook file
    app = create_app(str(notebook_path.absolute()))
    
    # Open browser if requested
    if not args.no_browser:
        def open_browser():
            webbrowser.open(f"http://{args.host}:{args.port}")
        
        # Schedule browser opening after a short delay
        import threading
        threading.Timer(1.5, open_browser).start()
    
    print(f"Starting Java Notebook server...")
    print(f"Notebook: {notebook_path.name}")
    print(f"URL: http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop the server")
    
    # Run the server
    try:
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            log_level="info" if args.debug else "warning",
            access_log=args.debug
        )
    except KeyboardInterrupt:
        print("\nShutting down server...")
    
    return 0


if __name__ == "__main__":
    exit(main())