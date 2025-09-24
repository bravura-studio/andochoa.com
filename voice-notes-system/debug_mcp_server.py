#!/usr/bin/env python3
"""
Debug version of MCP server to help diagnose Claude Desktop connection issues.
"""

import asyncio
import json
import logging
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


class DebugVoiceNotesServer:
    """Simplified debug version of Voice Notes MCP server."""

    def __init__(self):
        print("🚀 Initializing Debug Voice Notes MCP Server...", file=sys.stderr)
        self.server = Server("voice-notes")
        self._setup_handlers()
        print("✅ Debug server initialized successfully", file=sys.stderr)

    def _setup_handlers(self):
        """Set up MCP protocol handlers."""
        print("📋 Setting up MCP handlers...", file=sys.stderr)

        @self.server.list_tools()
        async def list_tools():
            """List available tools."""
            print("📝 Tools requested by Claude Desktop", file=sys.stderr)
            tools = [
                Tool(
                    name="test_tool",
                    description="Simple test tool to verify MCP connection",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Test message to echo back"
                            }
                        },
                        "required": ["message"]
                    }
                ),
                Tool(
                    name="start_voice_recording",
                    description="Start a new voice recording session",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_name": {
                                "type": "string",
                                "description": "Optional name for the recording session"
                            }
                        }
                    }
                )
            ]
            print(f"📤 Returning {len(tools)} tools to Claude Desktop", file=sys.stderr)
            return tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            """Handle tool calls."""
            print(f"🔧 Tool called: {name} with args: {arguments}", file=sys.stderr)

            if name == "test_tool":
                message = arguments.get("message", "No message provided")
                response = f"✅ Debug MCP Server received: {message}"
                print(f"📤 Responding with: {response}", file=sys.stderr)
                return [TextContent(type="text", text=response)]

            elif name == "start_voice_recording":
                session_name = arguments.get("session_name", "Debug Session")
                response = f"🎤 Debug: Started voice recording session '{session_name}'"
                print(f"📤 Responding with: {response}", file=sys.stderr)
                return [TextContent(type="text", text=response)]

            else:
                response = f"❌ Unknown tool: {name}"
                print(f"📤 Responding with error: {response}", file=sys.stderr)
                return [TextContent(type="text", text=response)]


async def main():
    """Main entry point for debug MCP server."""
    print("🎯 Starting Debug Voice Notes MCP Server", file=sys.stderr)

    # Set up logging to stderr so it appears in Claude Desktop logs
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )

    try:
        # Create debug server
        debug_server = DebugVoiceNotesServer()
        print("🌟 Debug server created successfully", file=sys.stderr)

        # Run the server
        print("🔗 Connecting to Claude Desktop via stdio...", file=sys.stderr)
        async with stdio_server() as (read_stream, write_stream):
            print("📡 Connected! Running server...", file=sys.stderr)
            await debug_server.server.run(
                read_stream,
                write_stream,
                debug_server.server.create_initialization_options()
            )

    except Exception as e:
        print(f"💥 Debug server failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise


if __name__ == "__main__":
    asyncio.run(main())