"""
Server startup script for RAG Agent FastAPI application

Run this script to start the web service. Supports custom host/port
configuration and automatic reloading for development.
"""

import sys
import argparse
import logging
import uvicorn


# =============================================================================
# ARGUMENT PARSING
# =============================================================================

def parse_arguments():
    """
    Parse command-line arguments for server startup.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="RAG Agent FastAPI Web Service",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )

    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on file changes (development mode)"
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)"
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["critical", "error", "warning", "info", "debug"],
        help="Logging level (default: info)"
    )

    return parser.parse_args()


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """
    Main function to start the FastAPI server.
    """
    args = parse_arguments()

    # Setup logging
    log_level = getattr(logging, args.log_level.upper())
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Import app here (after logging setup)
    from api.app import app

    # Display startup banner
    print("=" * 60)
    print("RAG Agent FastAPI Web Service")
    print("=" * 60)
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Workers: {args.workers}")
    print(f"Log Level: {args.log_level}")
    print(f"Reload: {args.reload}")
    print("=" * 60)
    print(f"API Documentation: http://{args.host}:{args.port}/docs")
    print(f"ReDoc: http://{args.host}:{args.port}/redoc")
    print(f"Health Check: http://{args.host}:{args.port}/health")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the server\n")

    # Run uvicorn server
    try:
        uvicorn.run(
            "api.app:app",
            host=args.host,
            port=args.port,
            workers=args.workers,
            reload=args.reload,
            log_level=args.log_level
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Server startup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
