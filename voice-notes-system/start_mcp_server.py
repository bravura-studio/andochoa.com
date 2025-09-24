#!/usr/bin/env python3
"""
Start the Voice Notes MCP server for Claude Desktop integration.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from src.mcp_server import main as run_mcp_server


def setup_logging():
    """Set up logging for the MCP server."""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "mcp_server.log"),
            logging.StreamHandler(sys.stderr)
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Starting Voice Notes MCP Server with log level: {log_level}")
    return logger


def main():
    """Main entry point for the MCP server."""
    try:
        # Set up logging
        logger = setup_logging()

        # Ensure required directories exist
        output_dir = Path(os.getenv('VOICE_NOTES_OUTPUT_DIR',
                                  os.path.expanduser("~/Documents/Build in public/Content Bank/1-raw-ideas")))
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            logger.warning(f"Cannot create output directory {output_dir}: {e}")
            # Directory creation will be handled in VoiceNotesServer with fallback

        temp_audio_dir = project_root / "temp_audio"
        try:
            temp_audio_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            logger.warning(f"Cannot create temp directory {temp_audio_dir}: {e}")
            # Directory creation will be handled in VoiceNotesServer with fallback

        logger.info(f"Output directory: {output_dir}")
        logger.info(f"Temp audio directory: {temp_audio_dir}")

        # Run the MCP server
        asyncio.run(run_mcp_server())

    except KeyboardInterrupt:
        logger.info("MCP server stopped by user")
    except Exception as e:
        logger.error(f"Error starting MCP server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()