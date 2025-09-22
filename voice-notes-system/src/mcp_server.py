import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
from pathlib import Path
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / ".env")

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from mcp import ClientSession


logger = logging.getLogger(__name__)


class VoiceNotesServer:
    """MCP server for voice notes system integration with Claude Desktop."""

    def __init__(self, config_dir: str = None, output_dir: str = None):
        """Initialize the voice notes MCP server.

        Args:
            config_dir: Directory for configuration files
            output_dir: Directory where voice notes are saved
        """
        # Get the project root directory (parent of src)
        project_root = Path(__file__).parent.parent

        self.config_dir = Path(config_dir or os.getenv('VOICE_NOTES_CONFIG_DIR', project_root / 'config'))
        self.output_dir = Path(output_dir or os.getenv('VOICE_NOTES_OUTPUT_DIR', project_root / 'notes'))
        self.temp_audio_dir = Path(os.getenv('VOICE_NOTES_TEMP_AUDIO_DIR', project_root / 'temp_audio'))

        # Ensure directories exist
        self.output_dir.mkdir(exist_ok=True)
        self.temp_audio_dir.mkdir(exist_ok=True)

        # Voice notes storage
        self.voice_notes = {}
        self.active_recordings = {}

        self.server = Server("voice-notes")
        self._setup_handlers()

    def _setup_handlers(self):
        """Set up MCP server handlers."""

        # List available resources
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List available voice notes as resources."""
            resources = []

            # Add existing voice notes
            if self.output_dir.exists():
                for note_file in self.output_dir.glob("*.md"):
                    resources.append(Resource(
                        uri=f"voice-note://{note_file.stem}",
                        name=f"Voice Note: {note_file.stem}",
                        description=f"Voice note from {note_file.stem}",
                        mimeType="text/markdown"
                    ))

            # Add system status resource
            resources.append(Resource(
                uri="voice-notes://status",
                name="Voice Notes System Status",
                description="Current status of the voice notes system",
                mimeType="application/json"
            ))

            return resources

        # Read resource content
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read content of a voice note resource."""
            if uri.startswith("voice-note://"):
                note_id = uri.replace("voice-note://", "")
                note_file = self.output_dir / f"{note_id}.md"

                if note_file.exists():
                    return note_file.read_text()
                else:
                    return f"Voice note '{note_id}' not found."

            elif uri == "voice-notes://status":
                status = {
                    "system": "Voice Notes System",
                    "status": "active",
                    "output_directory": str(self.output_dir),
                    "total_notes": len(list(self.output_dir.glob("*.md"))),
                    "active_recordings": len(self.active_recordings),
                    "last_updated": datetime.now().isoformat()
                }
                return json.dumps(status, indent=2)

            else:
                return f"Unknown resource: {uri}"

        # List available tools
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available voice notes tools."""
            return [
                Tool(
                    name="start_voice_recording",
                    description="Start a new voice recording session",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_name": {
                                "type": "string",
                                "description": "Optional name for the recording session"
                            },
                            "conversation_type": {
                                "type": "string",
                                "description": "Type of conversation (e.g., 'brainstorm', 'meeting', 'journal')",
                                "default": "general"
                            }
                        }
                    }
                ),
                Tool(
                    name="stop_voice_recording",
                    description="Stop an active voice recording session",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "ID of the recording session to stop"
                            }
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="transcribe_audio",
                    description="Transcribe an audio file using Whisper",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "audio_file": {
                                "type": "string",
                                "description": "Path to the audio file to transcribe"
                            },
                            "language": {
                                "type": "string",
                                "description": "Language code for transcription (optional)"
                            }
                        },
                        "required": ["audio_file"]
                    }
                ),
                Tool(
                    name="create_voice_note",
                    description="Create a formatted voice note from transcription",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "transcription": {
                                "type": "string",
                                "description": "The transcribed text"
                            },
                            "title": {
                                "type": "string",
                                "description": "Title for the voice note"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Tags to associate with the note"
                            },
                            "conversation_type": {
                                "type": "string",
                                "description": "Type of conversation for formatting",
                                "default": "general"
                            }
                        },
                        "required": ["transcription"]
                    }
                ),
                Tool(
                    name="list_voice_notes",
                    description="List all existing voice notes with metadata",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filter": {
                                "type": "string",
                                "description": "Optional filter by tag or keyword"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of notes to return",
                                "default": 20
                            }
                        }
                    }
                ),
                Tool(
                    name="search_voice_notes",
                    description="Search through voice notes content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    }
                )
            ]

        # Handle tool calls
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls from Claude Desktop."""
            try:
                if name == "start_voice_recording":
                    return await self._start_voice_recording(**arguments)
                elif name == "stop_voice_recording":
                    return await self._stop_voice_recording(**arguments)
                elif name == "transcribe_audio":
                    return await self._transcribe_audio(**arguments)
                elif name == "create_voice_note":
                    return await self._create_voice_note(**arguments)
                elif name == "list_voice_notes":
                    return await self._list_voice_notes(**arguments)
                elif name == "search_voice_notes":
                    return await self._search_voice_notes(**arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]

            except Exception as e:
                logger.error(f"Error in tool call {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _start_voice_recording(self, session_name: Optional[str] = None,
                                   conversation_type: str = "general") -> List[TextContent]:
        """Start a new voice recording session."""
        # This would integrate with your audio_recorder.py
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.active_recordings[session_id] = {
            "name": session_name or f"Recording {session_id}",
            "type": conversation_type,
            "started": datetime.now().isoformat(),
            "status": "recording"
        }

        # Here you would start the actual audio recording
        # For now, return a mock response
        return [TextContent(
            type="text",
            text=f"Started voice recording session: {session_id}\n"
                 f"Session name: {session_name or 'Unnamed'}\n"
                 f"Type: {conversation_type}\n"
                 f"Use the stop_voice_recording tool with session_id '{session_id}' when finished."
        )]

    async def _stop_voice_recording(self, session_id: str) -> List[TextContent]:
        """Stop an active voice recording session."""
        if session_id not in self.active_recordings:
            return [TextContent(type="text", text=f"No active recording found for session: {session_id}")]

        session = self.active_recordings[session_id]
        session["status"] = "stopped"
        session["ended"] = datetime.now().isoformat()

        # Here you would stop the actual audio recording and save the file
        audio_file = self.temp_audio_dir / f"{session_id}.wav"

        return [TextContent(
            type="text",
            text=f"Stopped voice recording session: {session_id}\n"
                 f"Duration: Started at {session['started']}\n"
                 f"Audio saved to: {audio_file}\n"
                 f"Use the transcribe_audio tool to process the recording."
        )]

    async def _transcribe_audio(self, audio_file: str, language: Optional[str] = None) -> List[TextContent]:
        """Transcribe an audio file using Whisper."""
        # This would integrate with your transcription.py
        # For now, return a mock response
        return [TextContent(
            type="text",
            text=f"Transcription of {audio_file}:\n\n"
                 f"[Mock transcription - this would contain the actual Whisper output]\n"
                 f"Language detected: {language or 'auto-detected'}\n\n"
                 f"Use the create_voice_note tool to format this transcription into a note."
        )]

    async def _create_voice_note(self, transcription: str, title: Optional[str] = None,
                               tags: Optional[List[str]] = None,
                               conversation_type: str = "general") -> List[TextContent]:
        """Create a formatted voice note from transcription."""
        timestamp = datetime.now()
        note_id = timestamp.strftime("%Y%m%d_%H%M%S")
        note_title = title or f"Voice Note {note_id}"

        # Format the note in markdown
        note_content = f"# {note_title}\n\n"
        note_content += f"**Date:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        note_content += f"**Type:** {conversation_type}\n"

        if tags:
            note_content += f"**Tags:** {', '.join(tags)}\n"

        note_content += "\n---\n\n"
        note_content += transcription
        note_content += "\n\n---\n\n"
        note_content += "*Created by Voice Notes System*\n"

        # Save the note
        note_file = self.output_dir / f"{note_id}_{note_title.replace(' ', '_')}.md"
        note_file.write_text(note_content)

        return [TextContent(
            type="text",
            text=f"Created voice note: {note_title}\n"
                 f"File: {note_file}\n"
                 f"Type: {conversation_type}\n"
                 f"Tags: {', '.join(tags) if tags else 'None'}"
        )]

    async def _list_voice_notes(self, filter: Optional[str] = None,
                              limit: int = 20) -> List[TextContent]:
        """List all existing voice notes with metadata."""
        notes = []

        if self.output_dir.exists():
            for note_file in sorted(self.output_dir.glob("*.md"),
                                  key=lambda x: x.stat().st_mtime, reverse=True):
                if len(notes) >= limit:
                    break

                # Basic filtering
                if filter and filter.lower() not in note_file.name.lower():
                    continue

                stat = note_file.stat()
                notes.append({
                    "name": note_file.name,
                    "path": str(note_file),
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

        if not notes:
            return [TextContent(type="text", text="No voice notes found.")]

        result = "## Voice Notes\n\n"
        for note in notes:
            result += f"- **{note['name']}**\n"
            result += f"  - Modified: {note['modified']}\n"
            result += f"  - Size: {note['size']} bytes\n\n"

        return [TextContent(type="text", text=result)]

    async def _search_voice_notes(self, query: str, max_results: int = 10) -> List[TextContent]:
        """Search through voice notes content."""
        results = []

        if self.output_dir.exists():
            for note_file in self.output_dir.glob("*.md"):
                if len(results) >= max_results:
                    break

                try:
                    content = note_file.read_text()
                    if query.lower() in content.lower():
                        # Extract a snippet around the match
                        lines = content.split('\n')
                        matching_lines = []
                        for i, line in enumerate(lines):
                            if query.lower() in line.lower():
                                start = max(0, i-2)
                                end = min(len(lines), i+3)
                                snippet = '\n'.join(lines[start:end])
                                matching_lines.append(snippet)
                                break

                        results.append({
                            "file": note_file.name,
                            "snippet": matching_lines[0] if matching_lines else content[:200]
                        })

                except Exception as e:
                    logger.error(f"Error reading {note_file}: {e}")
                    continue

        if not results:
            return [TextContent(type="text", text=f"No results found for query: '{query}'")]

        result_text = f"## Search Results for '{query}'\n\n"
        for i, result in enumerate(results, 1):
            result_text += f"### {i}. {result['file']}\n"
            result_text += f"```\n{result['snippet']}\n```\n\n"

        return [TextContent(type="text", text=result_text)]


async def main():
    """Main entry point for the MCP server."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create and run the server
    voice_notes_server = VoiceNotesServer()

    # Run the server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await voice_notes_server.server.run(
            read_stream,
            write_stream,
            voice_notes_server.server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())