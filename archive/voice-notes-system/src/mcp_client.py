import json
import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class MCPMessage:
    """Represents an MCP message."""
    role: str
    content: str
    timestamp: Optional[str] = None


class MCPClient:
    """Client for connecting to Model Context Protocol (MCP) servers."""

    def __init__(self, server_url: str, api_key: Optional[str] = None, timeout: int = 30):
        """Initialize MCP client.

        Args:
            server_url: URL of the MCP server
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
        """
        self.server_url = server_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()

    async def connect(self):
        """Establish connection to MCP server."""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)

    async def disconnect(self):
        """Close connection to MCP server."""
        if self.session:
            await self.session.close()
            self.session = None

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers including authentication."""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'

        return headers

    async def send_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send a message to the MCP server.

        Args:
            message: The message content to send
            conversation_id: Optional conversation identifier
            context: Optional context data

        Returns:
            Server response as dictionary

        Raises:
            aiohttp.ClientError: If request fails
            ValueError: If server returns error response
        """
        if not self.session:
            await self.connect()

        payload = {
            'message': message,
            'timestamp': str(asyncio.get_event_loop().time())
        }

        if conversation_id:
            payload['conversation_id'] = conversation_id

        if context:
            payload['context'] = context

        url = f"{self.server_url}/message"

        try:
            async with self.session.post(
                url,
                json=payload,
                headers=self._get_headers()
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise ValueError(f"MCP server error {response.status}: {error_text}")

        except aiohttp.ClientError as e:
            raise aiohttp.ClientError(f"Failed to connect to MCP server: {e}")

    async def start_conversation(
        self,
        initial_message: str,
        conversation_type: str = "voice_note",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Start a new conversation with the MCP server.

        Args:
            initial_message: The first message in the conversation
            conversation_type: Type of conversation (e.g., 'voice_note', 'analysis')
            metadata: Optional metadata about the conversation

        Returns:
            Conversation ID

        Raises:
            aiohttp.ClientError: If request fails
            ValueError: If server returns error response
        """
        if not self.session:
            await self.connect()

        payload = {
            'type': conversation_type,
            'initial_message': initial_message,
            'timestamp': str(asyncio.get_event_loop().time())
        }

        if metadata:
            payload['metadata'] = metadata

        url = f"{self.server_url}/conversation/start"

        try:
            async with self.session.post(
                url,
                json=payload,
                headers=self._get_headers()
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('conversation_id')
                else:
                    error_text = await response.text()
                    raise ValueError(f"MCP server error {response.status}: {error_text}")

        except aiohttp.ClientError as e:
            raise aiohttp.ClientError(f"Failed to start conversation: {e}")

    async def continue_conversation(
        self,
        conversation_id: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Continue an existing conversation.

        Args:
            conversation_id: ID of the conversation to continue
            message: The next message in the conversation
            context: Optional context data

        Returns:
            Server response including AI response

        Raises:
            aiohttp.ClientError: If request fails
            ValueError: If server returns error response
        """
        return await self.send_message(message, conversation_id, context)

    async def end_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """End a conversation and get summary.

        Args:
            conversation_id: ID of the conversation to end

        Returns:
            Conversation summary and metadata

        Raises:
            aiohttp.ClientError: If request fails
            ValueError: If server returns error response
        """
        if not self.session:
            await self.connect()

        url = f"{self.server_url}/conversation/{conversation_id}/end"

        try:
            async with self.session.post(
                url,
                headers=self._get_headers()
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise ValueError(f"MCP server error {response.status}: {error_text}")

        except aiohttp.ClientError as e:
            raise aiohttp.ClientError(f"Failed to end conversation: {e}")

    async def get_conversation_history(
        self,
        conversation_id: str
    ) -> List[MCPMessage]:
        """Get the full conversation history.

        Args:
            conversation_id: ID of the conversation

        Returns:
            List of conversation messages

        Raises:
            aiohttp.ClientError: If request fails
            ValueError: If server returns error response
        """
        if not self.session:
            await self.connect()

        url = f"{self.server_url}/conversation/{conversation_id}/history"

        try:
            async with self.session.get(
                url,
                headers=self._get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    messages = []
                    for msg_data in data.get('messages', []):
                        messages.append(MCPMessage(
                            role=msg_data['role'],
                            content=msg_data['content'],
                            timestamp=msg_data.get('timestamp')
                        ))
                    return messages
                else:
                    error_text = await response.text()
                    raise ValueError(f"MCP server error {response.status}: {error_text}")

        except aiohttp.ClientError as e:
            raise aiohttp.ClientError(f"Failed to get conversation history: {e}")

    async def health_check(self) -> bool:
        """Check if the MCP server is healthy and responsive.

        Returns:
            True if server is healthy, False otherwise
        """
        if not self.session:
            await self.connect()

        url = f"{self.server_url}/health"

        try:
            async with self.session.get(
                url,
                headers=self._get_headers()
            ) as response:
                return response.status == 200

        except Exception:
            return False

    async def get_server_info(self) -> Dict[str, Any]:
        """Get information about the MCP server.

        Returns:
            Server information dictionary

        Raises:
            aiohttp.ClientError: If request fails
            ValueError: If server returns error response
        """
        if not self.session:
            await self.connect()

        url = f"{self.server_url}/info"

        try:
            async with self.session.get(
                url,
                headers=self._get_headers()
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise ValueError(f"MCP server error {response.status}: {error_text}")

        except aiohttp.ClientError as e:
            raise aiohttp.ClientError(f"Failed to get server info: {e}")


class MockMCPClient(MCPClient):
    """Mock MCP client for testing and development when no real server is available."""

    def __init__(self, *args, **kwargs):
        """Initialize mock client."""
        super().__init__("http://localhost:8000", None, 30)
        self._conversations = {}
        self._message_count = 0

    async def connect(self):
        """Mock connection - always succeeds."""
        pass

    async def disconnect(self):
        """Mock disconnection."""
        pass

    async def send_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Mock message sending with simulated responses."""
        self._message_count += 1

        # Simple response simulation based on message content
        if "struggling" in message.lower() or "difficult" in message.lower():
            response = "I hear that this is challenging for you. What specifically feels most difficult about this situation?"
        elif "excited" in message.lower() or "great" in message.lower():
            response = "That sounds wonderful! What made this particularly meaningful for you?"
        elif "thinking" in message.lower() or "wondering" in message.lower():
            response = "Those are interesting thoughts. What sparked this particular line of thinking for you?"
        else:
            response = "Tell me more about what you're experiencing with this."

        return {
            'response': response,
            'conversation_id': conversation_id or f"mock_conv_{self._message_count}",
            'message_id': f"msg_{self._message_count}",
            'timestamp': str(asyncio.get_event_loop().time())
        }

    async def start_conversation(
        self,
        initial_message: str,
        conversation_type: str = "voice_note",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Mock conversation start."""
        conv_id = f"mock_conv_{len(self._conversations) + 1}"
        self._conversations[conv_id] = {
            'messages': [{'role': 'user', 'content': initial_message}],
            'type': conversation_type,
            'metadata': metadata or {}
        }
        return conv_id

    async def health_check(self) -> bool:
        """Mock health check - always returns True."""
        return True

    async def get_server_info(self) -> Dict[str, Any]:
        """Mock server info."""
        return {
            'name': 'Mock MCP Server',
            'version': '1.0.0',
            'status': 'running',
            'capabilities': ['conversations', 'analysis', 'voice_notes']
        }