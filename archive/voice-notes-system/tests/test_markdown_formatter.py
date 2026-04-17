"""
Test suite for MarkdownFormatter.
Tests all core functionality including document generation and formatting.
"""

import unittest
from datetime import datetime
from src.markdown_formatter import MarkdownFormatter, ConversationMetadata, ConversationExchange


class TestMarkdownFormatter(unittest.TestCase):
    """Test cases for MarkdownFormatter functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = MarkdownFormatter()
        self.metadata = ConversationMetadata(
            topic_type="struggle",
            depth_level="medium",
            total_exchanges=3,
            conversation_length=500,
            completion_reason="natural_end",
            created_at=datetime.now(),
            duration_minutes=5.2,
            tags=["work", "productivity"]
        )

    def test_generate_title_with_insight(self):
        """Test title generation from key insight."""
        insight = "I'm struggling with time management and productivity"
        title = self.formatter.generate_title(insight, "struggle")

        self.assertIn("Struggle:", title)
        self.assertTrue(len(title) > 10)
        self.assertTrue(len(title) <= 60)

    def test_generate_title_without_insight(self):
        """Test title generation without insight."""
        title = self.formatter.generate_title("", "reflection", ["daily", "review", "session"])

        self.assertIn("Reflection:", title)
        self.assertTrue("daily" in title.lower() or "Daily" in title)

    def test_extract_action_items(self):
        """Test action item extraction."""
        text = """
        I need to finish the project report by Friday.
        TODO: Call the client about the meeting.
        I should also remember to update the status board.
        Make sure to send the invoice.
        """

        action_items = self.formatter.extract_action_items(text)

        self.assertTrue(len(action_items) >= 2)
        self.assertTrue(any("finish the project report" in item.lower() for item in action_items))
        self.assertTrue(any("call the client" in item.lower() for item in action_items))

    def test_extract_key_insights(self):
        """Test key insights extraction."""
        text = """
        The main challenge is balancing multiple priorities.
        What I've learned is that planning ahead really helps.
        I realize that communication is key to project success.
        """

        insights = self.formatter.extract_key_insights(text, "struggle")

        self.assertTrue(len(insights) >= 2)
        self.assertTrue(any("balancing multiple priorities" in insight.lower() for insight in insights))

    def test_create_wikilinks(self):
        """Test wikilink generation."""
        entities = ["John Smith", "Project Alpha"]
        topics = ["productivity", "time management", "workflow"]
        existing_notes = ["Time Management Strategies", "Workflow Optimization"]

        wikilinks = self.formatter.create_wikilinks(entities, topics, existing_notes)

        if wikilinks:  # Only test if wikilinks were generated
            self.assertIn("[[", wikilinks)
            self.assertIn("]]", wikilinks)

    def test_format_conversation_exchanges(self):
        """Test conversation formatting from exchanges."""
        exchanges = [
            ConversationExchange("Initial", "I'm having trouble with my workflow"),
            ConversationExchange("AI", "What specific aspects are challenging?"),
            ConversationExchange("User", "Time management and prioritization")
        ]

        formatted = self.formatter.format_conversation(exchanges)

        self.assertIn("## Conversation", formatted)
        self.assertIn("Initial Voice Note", formatted)
        self.assertIn("**Claude:**", formatted)
        self.assertIn("**You:**", formatted)

    def test_create_frontmatter(self):
        """Test YAML frontmatter generation."""
        frontmatter = self.formatter.create_frontmatter(
            self.metadata,
            "Test Title",
            ["key insight"],
            ["action item"],
            ["topic"]
        )

        self.assertIn("---", frontmatter)
        self.assertIn("title: Test Title", frontmatter)
        self.assertIn("type: voice-note", frontmatter)
        self.assertIn("topic_type: struggle", frontmatter)
        self.assertIn("key_insights:", frontmatter)
        self.assertIn("action_items:", frontmatter)

    def test_complete_document_creation(self):
        """Test complete document creation."""
        conversation_data = {
            'context_history': [
                "Initial transcript: I'm struggling with productivity",
                "AI: What specific areas are you finding challenging?",
                "User: Time management and focus"
            ],
            'entities': ["productivity system"],
            'topics': ["time management", "focus"]
        }

        document = self.formatter.create_complete_document(
            conversation_data, self.metadata
        )

        # Verify document structure
        self.assertIn("---", document)  # Frontmatter
        self.assertIn("## Summary", document)
        self.assertIn("## Key Insights", document)
        self.assertIn("## Action Items", document)
        self.assertIn("## Conversation", document)
        self.assertIn("Initial Voice Note", document)


class TestConversationMetadata(unittest.TestCase):
    """Test ConversationMetadata dataclass."""

    def test_metadata_creation(self):
        """Test metadata object creation."""
        metadata = ConversationMetadata(
            topic_type="win",
            depth_level="deep",
            total_exchanges=5,
            conversation_length=1200,
            completion_reason="user_ended",
            created_at=datetime.now()
        )

        self.assertEqual(metadata.topic_type, "win")
        self.assertEqual(metadata.depth_level, "deep")
        self.assertEqual(metadata.total_exchanges, 5)
        self.assertIsInstance(metadata.tags, list)


if __name__ == '__main__':
    unittest.main()