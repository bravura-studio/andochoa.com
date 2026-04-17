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

# Import our voice notes components
try:
    from .audio_recorder import AudioRecorder
    from .transcription import TranscriptionService
    from .conversation_manager import ConversationManager
    from .config_manager import ConfigManager
except ImportError:
    from audio_recorder import AudioRecorder
    from transcription import TranscriptionService
    from conversation_manager import ConversationManager
    from config_manager import ConfigManager


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

        # Ensure directories exist with fallback for read-only systems
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            logger.error(f"Cannot create output directory {self.output_dir}: {e}")
            # Use a fallback directory
            import tempfile
            fallback_output = Path(tempfile.gettempdir()) / "voice_notes_output"
            fallback_output.mkdir(exist_ok=True)
            self.output_dir = fallback_output
            logger.warning(f"Using fallback output directory: {self.output_dir}")

        try:
            self.temp_audio_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            logger.error(f"Cannot create temp audio directory {self.temp_audio_dir}: {e}")
            # Use system temp directory
            import tempfile
            self.temp_audio_dir = Path(tempfile.gettempdir()) / "voice_notes_temp"
            self.temp_audio_dir.mkdir(exist_ok=True)
            logger.warning(f"Using fallback temp audio directory: {self.temp_audio_dir}")

        # Voice notes storage
        self.voice_notes = {}
        self.active_recordings = {}
        self.conversation_states = {}  # Store conversation states by session_id

        # Initialize voice notes components
        self.config_manager = ConfigManager()
        self.audio_recorder = AudioRecorder(self.config_manager)
        self.transcription_service = TranscriptionService(self.config_manager)
        self.conversation_manager = ConversationManager()

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
                            },
                            "enable_conversation": {
                                "type": "boolean",
                                "description": "Enable AI conversation for deeper insights",
                                "default": True
                            },
                            "processing_mode": {
                                "type": "string",
                                "description": "Processing mode (quick/standard/deep)",
                                "default": "standard"
                            }
                        },
                        "required": ["transcription"]
                    }
                ),
                Tool(
                    name="continue_conversation",
                    description="Continue an AI conversation about a voice note",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session ID of the conversation"
                            },
                            "user_response": {
                                "type": "string",
                                "description": "User's response to the AI prompt"
                            }
                        },
                        "required": ["session_id", "user_response"]
                    }
                ),
                Tool(
                    name="end_conversation",
                    description="End an AI conversation and get the final summary",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session ID of the conversation to end"
                            }
                        },
                        "required": ["session_id"]
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
                elif name == "continue_conversation":
                    return await self._continue_conversation(**arguments)
                elif name == "end_conversation":
                    return await self._end_conversation(**arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]

            except Exception as e:
                logger.error(f"Error in tool call {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _start_voice_recording(self, session_name: Optional[str] = None,
                                   conversation_type: str = "general") -> List[TextContent]:
        """Start a new voice recording session."""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        try:
            # Start actual audio recording
            success = self.audio_recorder.start_recording()

            if not success:
                return [TextContent(
                    type="text",
                    text=f"Failed to start audio recording. Please check your microphone settings."
                )]

            self.active_recordings[session_id] = {
                "name": session_name or f"Recording {session_id}",
                "type": conversation_type,
                "started": datetime.now().isoformat(),
                "status": "recording",
                "audio_recorder": self.audio_recorder
            }

            return [TextContent(
                type="text",
                text=f"🎤 Started voice recording session: {session_id}\n"
                     f"Session name: {session_name or 'Unnamed'}\n"
                     f"Type: {conversation_type}\n"
                     f"🛑 Use stop_voice_recording with session_id '{session_id}' when finished."
            )]

        except Exception as e:
            logger.error(f"Error starting recording: {e}")
            return [TextContent(
                type="text",
                text=f"Error starting recording: {str(e)}"
            )]

    async def _stop_voice_recording(self, session_id: str) -> List[TextContent]:
        """Stop an active voice recording session."""
        if session_id not in self.active_recordings:
            return [TextContent(type="text", text=f"No active recording found for session: {session_id}")]

        session = self.active_recordings[session_id]

        try:
            # Stop the actual audio recording
            if "audio_recorder" in session:
                audio_recorder = session["audio_recorder"]
                success = audio_recorder.stop_recording()

                if not success:
                    return [TextContent(
                        type="text",
                        text=f"Failed to stop recording for session: {session_id}"
                    )]

                # Save the audio file
                audio_file = self.temp_audio_dir / f"{session_id}.wav"
                saved_path = audio_recorder.save_audio(str(audio_file))
                duration = audio_recorder.get_recording_duration()

                session["status"] = "stopped"
                session["ended"] = datetime.now().isoformat()
                session["audio_file"] = saved_path
                session["duration"] = duration

                return [TextContent(
                    type="text",
                    text=f"🛑 Stopped voice recording session: {session_id}\n"
                         f"Duration: {duration:.1f} seconds\n"
                         f"Audio saved to: {saved_path}\n"
                         f"📝 Use transcribe_audio tool with file path '{saved_path}' to process the recording."
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"No audio recorder found for session: {session_id}"
                )]

        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            return [TextContent(
                type="text",
                text=f"Error stopping recording: {str(e)}"
            )]

    async def _transcribe_audio(self, audio_file: str, language: Optional[str] = None) -> List[TextContent]:
        """Transcribe an audio file using Whisper."""
        try:
            # Use the actual transcription service
            result = self.transcription_service.transcribe_audio(audio_file, use_cache=True)

            if not result or not result.text:
                return [TextContent(
                    type="text",
                    text=f"❌ Failed to transcribe audio file: {audio_file}\n"
                         f"The transcription returned empty or failed."
                )]

            # Format the response with metadata
            response_text = f"✅ Transcription completed for: {Path(audio_file).name}\n\n"
            response_text += f"**Text:**\n{result.text}\n\n"
            response_text += f"**Details:**\n"
            response_text += f"- Duration: {result.duration:.1f} minutes\n"
            response_text += f"- Language: {result.language or 'auto-detected'}\n"
            response_text += f"- Word count: {result.word_count}\n"
            response_text += f"- Cost: ${result.cost_estimate:.4f}\n"
            response_text += f"- API used: {result.api_used}\n\n"
            response_text += f"💡 Use create_voice_note tool with this transcription to create a structured note with AI conversation."

            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            # Try fallback transcription
            try:
                result = self.transcription_service.fallback_transcription(audio_file)
                response_text = f"⚠️ Used fallback transcription for: {Path(audio_file).name}\n\n"
                response_text += f"**Text:**\n{result.text}\n\n"
                response_text += f"**Note:** This is a lower-quality fallback transcription.\n"
                response_text += f"Duration: {result.duration:.1f} minutes | API: {result.api_used}\n\n"
                response_text += f"💡 Use create_voice_note tool with this transcription to create a structured note."
                return [TextContent(type="text", text=response_text)]
            except Exception as fallback_error:
                logger.error(f"Fallback transcription failed: {fallback_error}")
                return [TextContent(
                    type="text",
                    text=f"❌ Transcription failed: {str(e)}\n"
                         f"Fallback also failed: {str(fallback_error)}\n\n"
                         f"Please check your OpenAI API key and internet connection."
                )]

    async def _create_voice_note(self, transcription: str, title: Optional[str] = None,
                               tags: Optional[List[str]] = None,
                               conversation_type: str = "general",
                               enable_conversation: bool = True,
                               processing_mode: str = "standard") -> List[TextContent]:
        """Create a formatted voice note from transcription with optional AI conversation."""
        timestamp = datetime.now()
        note_id = timestamp.strftime("%Y%m%d_%H%M%S")
        note_title = title or f"Voice Note {note_id}"

        try:
            # Start AI conversation if enabled
            conversation_session_id = None
            initial_prompt = None
            conversation_state = None

            if enable_conversation:
                # Create conversation state and get initial prompt
                initial_prompt, conversation_state = self.conversation_manager.generate_initial_prompt(
                    transcription, processing_mode
                )

                conversation_session_id = f"conv_{note_id}"
                self.conversation_states[conversation_session_id] = conversation_state

            # Format the note in markdown with YAML frontmatter
            note_content = f"---\n"
            note_content += f"title: \"{note_title}\"\n"
            note_content += f"date: \"{timestamp.strftime('%Y-%m-%d %H:%M:%S')}\"\n"
            note_content += f"type: \"{conversation_type}\"\n"
            note_content += f"processing_mode: \"{processing_mode}\"\n"

            if tags:
                note_content += f"tags: [{', '.join(f'\"{tag}\"' for tag in tags)}]\n"

            if conversation_session_id:
                note_content += f"conversation_session_id: \"{conversation_session_id}\"\n"
                note_content += f"topic_type: \"{conversation_state.topic_type.value}\"\n"
                note_content += f"conversation_depth: \"{conversation_state.depth_level.value}\"\n"

            note_content += f"source: \"voice_recording\"\n"
            note_content += f"---\n\n"

            # Add the main content
            note_content += f"# {note_title}\n\n"
            note_content += f"## Original Transcription\n\n"
            note_content += transcription

            if enable_conversation and initial_prompt:
                note_content += f"\n\n## AI Conversation\n\n"
                note_content += f"**Initial AI Prompt:** {initial_prompt}\n\n"
                note_content += f"*Use `continue_conversation` with session ID `{conversation_session_id}` to respond and continue the conversation.*\n\n"

            note_content += f"\n\n---\n\n"
            note_content += f"*Created by Voice Notes System at {timestamp.strftime('%Y-%m-%d %H:%M:%S')}*\n"

            # Save the note
            note_file = self.output_dir / f"{note_id}_{note_title.replace(' ', '_').replace('/', '_')}.md"
            note_file.write_text(note_content)

            # Prepare response
            response_text = f"📝 Created voice note: {note_title}\n"
            response_text += f"📁 File: {note_file}\n"
            response_text += f"📊 Type: {conversation_type}\n"
            response_text += f"🏷️ Tags: {', '.join(tags) if tags else 'None'}\n"

            if enable_conversation and initial_prompt:
                response_text += f"\n🤖 **AI Conversation Started**\n"
                response_text += f"Session ID: `{conversation_session_id}`\n"
                response_text += f"Topic: {conversation_state.topic_type.value}\n"
                response_text += f"Depth: {conversation_state.depth_level.value}\n\n"
                response_text += f"**AI asks:** {initial_prompt}\n\n"
                response_text += f"💬 Use `continue_conversation` with session ID `{conversation_session_id}` and your response to continue."
            else:
                response_text += f"\n✅ Voice note created without AI conversation."

            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            logger.error(f"Error creating voice note: {e}")
            return [TextContent(
                type="text",
                text=f"❌ Error creating voice note: {str(e)}"
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

    async def _continue_conversation(self, session_id: str, user_response: str) -> List[TextContent]:
        """Continue an AI conversation about a voice note."""
        if session_id not in self.conversation_states:
            return [TextContent(
                type="text",
                text=f"❌ No active conversation found for session: {session_id}\n"
                     f"Available sessions: {list(self.conversation_states.keys())}"
            )]

        try:
            conversation_state = self.conversation_states[session_id]

            # Check if conversation is already complete
            if conversation_state.is_complete:
                return [TextContent(
                    type="text",
                    text=f"✅ This conversation has already been completed.\n"
                         f"Use `end_conversation` with session ID `{session_id}` to get the final summary."
                )]

            # Generate follow-up prompt based on user response
            next_prompt = self.conversation_manager.generate_followup(conversation_state)

            if next_prompt is None:
                # Conversation is complete
                conversation_state.is_complete = True
                insights = self.conversation_manager.extract_insights(conversation_state)

                return [TextContent(
                    type="text",
                    text=f"✅ Conversation completed naturally!\n\n"
                         f"**Summary:**\n"
                         f"- Topic: {insights['topic_type']}\n"
                         f"- Total exchanges: {insights['total_exchanges']}\n"
                         f"- Completion reason: {insights['completion_reason']}\n\n"
                         f"💾 Use `end_conversation` with session ID `{session_id}` to update your voice note with the conversation insights."
                )]

            # Update conversation context with the user response
            last_prompt = "[Previous AI prompt]"  # We could track this better
            self.conversation_manager.update_conversation_context(
                conversation_state, user_response, last_prompt
            )

            # Check if we should continue
            if not self.conversation_manager.should_continue(conversation_state, user_response):
                conversation_state.is_complete = True
                insights = self.conversation_manager.extract_insights(conversation_state)

                return [TextContent(
                    type="text",
                    text=f"✅ Conversation completed!\n\n"
                         f"**Final Summary:**\n"
                         f"- Topic: {insights['topic_type']}\n"
                         f"- Total exchanges: {insights['total_exchanges']}\n"
                         f"- Completion reason: {insights['completion_reason']}\n\n"
                         f"💾 Use `end_conversation` with session ID `{session_id}` to update your voice note."
                )]

            # Continue the conversation
            response_text = f"🤖 **AI Response** (Exchange {conversation_state.follow_up_count + 1})\n\n"
            response_text += f"{next_prompt}\n\n"
            response_text += f"**Session:** `{session_id}`\n"
            response_text += f"**Topic:** {conversation_state.topic_type.value}\n"
            response_text += f"**Engagement:** {conversation_state.user_engagement_score:.1f}/1.0\n\n"
            response_text += f"💬 Use `continue_conversation` with your response to continue, or `end_conversation` to finish."

            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            logger.error(f"Error continuing conversation: {e}")
            return [TextContent(
                type="text",
                text=f"❌ Error continuing conversation: {str(e)}"
            )]

    async def _end_conversation(self, session_id: str) -> List[TextContent]:
        """End an AI conversation and get the final summary."""
        if session_id not in self.conversation_states:
            return [TextContent(
                type="text",
                text=f"❌ No conversation found for session: {session_id}\n"
                     f"Available sessions: {list(self.conversation_states.keys())}"
            )]

        try:
            conversation_state = self.conversation_states[session_id]

            # Finalize the conversation
            insights = self.conversation_manager.finalize_conversation(conversation_state)

            # Find and update the original voice note file
            note_id = session_id.replace('conv_', '')
            matching_files = list(self.output_dir.glob(f"{note_id}_*.md"))

            if matching_files:
                note_file = matching_files[0]

                # Read existing content
                existing_content = note_file.read_text()

                # Add conversation summary to the note
                conversation_summary = f"\n## Conversation Summary\n\n"
                conversation_summary += f"**Topic Analysis:** {insights['topic_type']} ({insights['depth_level']} depth)\n"
                conversation_summary += f"**Total Exchanges:** {insights['total_exchanges']}\n"
                conversation_summary += f"**Completion Reason:** {insights['completion_reason']}\n\n"

                if insights.get('conversation_history'):
                    conversation_summary += f"**Full Conversation:**\n"
                    for i, exchange in enumerate(insights['conversation_history'], 1):
                        conversation_summary += f"\n{i}. {exchange}\n"

                conversation_summary += f"\n\n*Conversation completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

                # Update the note file
                updated_content = existing_content.replace(
                    "*Created by Voice Notes System",
                    f"{conversation_summary}\n---\n\n*Created by Voice Notes System"
                )

                note_file.write_text(updated_content)

                # Clean up conversation state
                del self.conversation_states[session_id]

                response_text = f"✅ **Conversation Completed & Note Updated**\n\n"
                response_text += f"**Summary:**\n"
                response_text += f"- Topic: {insights['topic_type']}\n"
                response_text += f"- Depth: {insights['depth_level']}\n"
                response_text += f"- Exchanges: {insights['total_exchanges']}\n"
                response_text += f"- Reason: {insights['completion_reason']}\n\n"
                response_text += f"📝 **Updated file:** {note_file}\n\n"
                response_text += f"🎯 The conversation insights have been added to your original voice note."

                return [TextContent(type="text", text=response_text)]
            else:
                return [TextContent(
                    type="text",
                    text=f"⚠️ Conversation ended but could not find original note file for ID: {note_id}\n\n"
                         f"**Conversation Summary:**\n"
                         f"- Topic: {insights['topic_type']}\n"
                         f"- Exchanges: {insights['total_exchanges']}\n"
                         f"- Reason: {insights['completion_reason']}"
                )]

        except Exception as e:
            logger.error(f"Error ending conversation: {e}")
            return [TextContent(
                type="text",
                text=f"❌ Error ending conversation: {str(e)}"
            )]


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