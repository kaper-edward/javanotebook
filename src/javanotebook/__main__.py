"""Command-line interface for Java Notebook."""

import argparse
import asyncio
import webbrowser
from pathlib import Path
import uvicorn

from .main import create_app
from .format_detector import FormatDetector, NotebookFormat


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Java Notebook - A Jupyter-style notebook for Java code execution"
    )
    
    parser.add_argument(
        "notebook",
        help="Path to the notebook file (.md or .ipynb)"
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

    parser.add_argument(
        "--format",
        choices=["md", "ipynb", "auto"],
        default="auto",
        help="Notebook format (default: auto-detect)"
    )

    parser.add_argument(
        "--output-format",
        choices=["md", "ipynb"],
        help="Output format for conversions (optional)"
    )
    
    args = parser.parse_args()
    
    # Validate notebook file
    notebook_path = Path(args.notebook)
    if not notebook_path.exists():
        print(f"Error: Notebook file not found: {args.notebook}")
        return 1

    # AIDEV-NOTE: Detect and validate notebook format
    try:
        if args.format == "auto":
            detected_format = FormatDetector.detect_format(str(notebook_path))
            print(f"Detected format: {detected_format.value}")
        else:
            detected_format = NotebookFormat(args.format)
            # Validate format consistency
            if not FormatDetector.validate_format_consistency(str(notebook_path), detected_format):
                print(f"Warning: File content may not match specified format ({args.format})")

        # AIDEV-NOTE: Create FastAPI app with notebook file and format info
        app = create_app(str(notebook_path.absolute()), detected_format)

    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    # Open browser if requested
    if not args.no_browser:
        def open_browser():
            webbrowser.open(f"http://{args.host}:{args.port}")
        
        # Schedule browser opening after a short delay
        import threading
        threading.Timer(1.5, open_browser).start()
    
    print(f"Starting Java Notebook server...")
    print(f"Notebook: {notebook_path.name} ({detected_format.value})")
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