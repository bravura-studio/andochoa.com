"""
Markdown Formatter for Voice Notes.
Formats conversation data into structured markdown with YAML frontmatter.
"""

import yaml
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ConversationExchange:
    """Represents a single conversation exchange."""
    speaker: str  # "User" or "AI"
    content: str
    timestamp: Optional[datetime] = None


@dataclass
class ConversationMetadata:
    """Metadata for conversation formatting."""
    topic_type: str
    depth_level: str
    total_exchanges: int
    conversation_length: int
    completion_reason: str
    created_at: datetime
    duration_minutes: Optional[float] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class MarkdownFormatter:
    """
    Formats voice note conversations into structured markdown documents.
    Creates proper YAML frontmatter and organized content sections.
    """

    def __init__(self):
        """Initialize the markdown formatter."""
        self.action_item_patterns = [
            r'\b(?:I need to|I should|I will|I must|I have to|I\'ll|I plan to)\s+([^.!?]+)',
            r'\b(?:TODO|Action item|Next step|Follow up):\s*([^.!?\n]+)',
            r'\b(?:Remember to|Don\'t forget to|Make sure to)\s+([^.!?]+)',
            r'\b(?:Schedule|Book|Call|Email|Contact|Send|Write|Create|Build|Fix|Update)\s+([^.!?]+)',
        ]

    def create_frontmatter(self, metadata: ConversationMetadata, title: str,
                          key_insights: List[str] = None, action_items: List[str] = None,
                          related_topics: List[str] = None) -> str:
        """
        Generate proper YAML frontmatter for the markdown document.

        Args:
            metadata: Conversation metadata
            title: Generated title for the conversation
            key_insights: List of key insights
            action_items: List of extracted action items
            related_topics: List of related topics/entities

        Returns:
            YAML frontmatter as string
        """
        if key_insights is None:
            key_insights = []
        if action_items is None:
            action_items = []
        if related_topics is None:
            related_topics = []

        # Create comprehensive frontmatter
        frontmatter_data = {
            'title': title,
            'created': metadata.created_at.isoformat(),
            'type': 'voice-note',
            'status': 'processed',
            'topic_type': metadata.topic_type,
            'conversation_depth': metadata.depth_level,
            'tags': self._generate_tags(metadata, related_topics),
            'metadata': {
                'total_exchanges': metadata.total_exchanges,
                'conversation_length_chars': metadata.conversation_length,
                'completion_reason': metadata.completion_reason,
                'processing_date': datetime.now().isoformat()
            }
        }

        # Add duration if available
        if metadata.duration_minutes:
            frontmatter_data['metadata']['duration_minutes'] = round(metadata.duration_minutes, 1)

        # Add key insights if available
        if key_insights:
            frontmatter_data['key_insights'] = key_insights

        # Add action items if available
        if action_items:
            frontmatter_data['action_items'] = action_items

        # Add related topics if available
        if related_topics:
            frontmatter_data['related_topics'] = related_topics

        # Format as YAML frontmatter
        yaml_content = yaml.dump(frontmatter_data, default_flow_style=False, sort_keys=False)
        return f"---\n{yaml_content}---\n"

    def _generate_tags(self, metadata: ConversationMetadata, related_topics: List[str]) -> List[str]:
        """Generate comprehensive tags for the conversation."""
        tags = set(metadata.tags) if metadata.tags else set()

        # Add topic type tag
        tags.add(metadata.topic_type)

        # Add depth level tag
        tags.add(f"depth-{metadata.depth_level}")

        # Add date-based tags
        date_tag = metadata.created_at.strftime("%Y-%m")
        tags.add(date_tag)

        # Add related topic tags (first 5 to avoid clutter)
        for topic in related_topics[:5]:
            # Clean topic for tag format
            clean_topic = re.sub(r'[^\w\s-]', '', topic.lower())
            clean_topic = re.sub(r'\s+', '-', clean_topic.strip())
            if clean_topic:
                tags.add(clean_topic)

        return sorted(list(tags))

    def format_conversation(self, exchanges: List[ConversationExchange],
                          include_timestamps: bool = False) -> str:
        """
        Format conversation exchanges into clear markdown structure.

        Args:
            exchanges: List of conversation exchanges
            include_timestamps: Whether to include timestamps in output

        Returns:
            Formatted conversation as markdown string
        """
        if not exchanges:
            return "## Conversation\n\n*No conversation exchanges recorded.*\n"

        conversation_lines = ["## Conversation\n"]

        for i, exchange in enumerate(exchanges):
            # Determine if this is the initial transcript or a conversation exchange
            if i == 0 and exchange.speaker == "Initial":
                conversation_lines.append("### Initial Voice Note\n")
                conversation_lines.append(f"{exchange.content}\n")
                conversation_lines.append("")
                continue

            # Format regular exchanges
            speaker_label = "**You:**" if exchange.speaker == "User" else "**Claude:**"

            # Add timestamp if requested and available
            timestamp_str = ""
            if include_timestamps and exchange.timestamp:
                timestamp_str = f" *({exchange.timestamp.strftime('%H:%M:%S')})*"

            conversation_lines.append(f"{speaker_label}{timestamp_str}")
            conversation_lines.append(f"{exchange.content}\n")

        return "\n".join(conversation_lines)

    def format_conversation_from_history(self, context_history: List[str],
                                       include_timestamps: bool = False) -> str:
        """
        Format conversation from context history strings.

        Args:
            context_history: List of context history strings from ConversationState
            include_timestamps: Whether to include timestamps

        Returns:
            Formatted conversation as markdown string
        """
        exchanges = []

        for i, history_item in enumerate(context_history):
            if i == 0 and history_item.startswith("Initial transcript:"):
                # Extract initial transcript
                transcript = history_item.replace("Initial transcript: ", "")
                exchanges.append(ConversationExchange("Initial", transcript))
            else:
                # Parse AI/User exchanges
                lines = history_item.strip().split('\n')
                current_speaker = None
                current_content = []

                for line in lines:
                    if line.startswith("AI: "):
                        if current_speaker and current_content:
                            exchanges.append(ConversationExchange(
                                current_speaker,
                                '\n'.join(current_content).strip()
                            ))
                        current_speaker = "AI"
                        current_content = [line[4:]]  # Remove "AI: " prefix
                    elif line.startswith("User: "):
                        if current_speaker and current_content:
                            exchanges.append(ConversationExchange(
                                current_speaker,
                                '\n'.join(current_content).strip()
                            ))
                        current_speaker = "User"
                        current_content = [line[6:]]  # Remove "User: " prefix
                    else:
                        if current_content:
                            current_content.append(line)

                # Add the last exchange
                if current_speaker and current_content:
                    exchanges.append(ConversationExchange(
                        current_speaker,
                        '\n'.join(current_content).strip()
                    ))

        return self.format_conversation(exchanges, include_timestamps)

    def create_summary_section(self, conversation_text: str, metadata: ConversationMetadata) -> str:
        """
        Create a summary section with conversation overview.

        Args:
            conversation_text: The full conversation text
            metadata: Conversation metadata

        Returns:
            Formatted summary section
        """
        summary_lines = ["## Summary\n"]

        # Add basic stats
        word_count = len(conversation_text.split())
        summary_lines.append(f"**Topic Type:** {metadata.topic_type.title()}")
        summary_lines.append(f"**Conversation Depth:** {metadata.depth_level.title()}")
        summary_lines.append(f"**Exchanges:** {metadata.total_exchanges}")
        summary_lines.append(f"**Word Count:** {word_count}")

        if metadata.duration_minutes:
            summary_lines.append(f"**Duration:** {metadata.duration_minutes:.1f} minutes")

        summary_lines.append(f"**Completion Reason:** {metadata.completion_reason}")
        summary_lines.append("")

        return "\n".join(summary_lines)

    def extract_action_items(self, text: str) -> List[str]:
        """
        Extract and list action items from conversation text.

        Args:
            text: Full conversation text to analyze

        Returns:
            List of extracted action items
        """
        action_items = []
        seen_items = set()  # To avoid duplicates

        # Split text into sentences for better analysis
        sentences = re.split(r'[.!?]+', text)

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Check each pattern
            for pattern in self.action_item_patterns:
                matches = re.finditer(pattern, sentence, re.IGNORECASE)
                for match in matches:
                    action_text = match.group(1).strip()

                    # Clean up the action text
                    action_text = self._clean_action_item(action_text)

                    # Skip if too short or already seen
                    if len(action_text) < 10 or action_text.lower() in seen_items:
                        continue

                    seen_items.add(action_text.lower())
                    action_items.append(action_text)

        # Also look for explicit bullet points or numbered lists that might be actions
        explicit_actions = self._extract_explicit_action_lists(text)
        for action in explicit_actions:
            clean_action = self._clean_action_item(action)
            if len(clean_action) >= 10 and clean_action.lower() not in seen_items:
                seen_items.add(clean_action.lower())
                action_items.append(clean_action)

        return action_items[:10]  # Limit to 10 most relevant action items

    def _clean_action_item(self, action_text: str) -> str:
        """Clean and normalize action item text."""
        # Remove common prefixes/suffixes
        action_text = re.sub(r'^(to\s+|that\s+|the\s+)', '', action_text, flags=re.IGNORECASE)
        action_text = re.sub(r'\s*(tomorrow|today|next week|soon)\s*$', '', action_text, flags=re.IGNORECASE)

        # Capitalize first letter
        action_text = action_text.strip()
        if action_text:
            action_text = action_text[0].upper() + action_text[1:]

        return action_text

    def _extract_explicit_action_lists(self, text: str) -> List[str]:
        """Extract action items from explicit lists in the text."""
        action_items = []

        # Look for patterns like "Action items:" or "TODO:" followed by lists
        list_patterns = [
            r'(?:Action items?|TODO|To do|Next steps?):\s*\n?((?:\s*[-*•]\s*[^\n]+\n?)+)',
            r'(?:I need to|I should|I will):\s*\n?((?:\s*[-*•]\s*[^\n]+\n?)+)',
        ]

        for pattern in list_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                list_content = match.group(1)
                items = re.findall(r'[-*•]\s*([^\n]+)', list_content)
                action_items.extend(items)

        return action_items

    def format_action_items_section(self, action_items: List[str]) -> str:
        """
        Format action items into a markdown section.

        Args:
            action_items: List of action items

        Returns:
            Formatted action items section
        """
        if not action_items:
            return "## Action Items\n\n*No specific action items identified.*\n"

        lines = ["## Action Items\n"]
        for item in action_items:
            lines.append(f"- [ ] {item}")
        lines.append("")

        return "\n".join(lines)

    def extract_key_insights(self, conversation_text: str, topic_type: str) -> List[str]:
        """
        Extract key insights from conversation based on topic type.

        Args:
            conversation_text: Full conversation text
            topic_type: The topic type to guide insight extraction

        Returns:
            List of key insights
        """
        insights = []
        text_lower = conversation_text.lower()

        # Topic-specific insight patterns
        insight_patterns = {
            'struggle': [
                r'(?:the main|primary|biggest|key) (?:challenge|problem|issue|difficulty) (?:is|was|seems to be) ([^.!?]+)',
                r'(?:i\'m struggling with|i\'m having trouble with|the hardest part is) ([^.!?]+)',
                r'(?:what\'s difficult|what\'s hard|what\'s challenging) (?:is|about this) ([^.!?]+)',
                r'(?:i realize|i\'ve learned|i understand) (?:that|how) ([^.!?]+)'
            ],
            'win': [
                r'(?:the key to|what made this work|the secret was|what helped) ([^.!?]+)',
                r'(?:i\'m proud of|i\'m excited about|what went well) ([^.!?]+)',
                r'(?:the breakthrough|the turning point|what changed) (?:was|came when) ([^.!?]+)',
                r'(?:i learned|i discovered|i realized) (?:that|how) ([^.!?]+)'
            ],
            'reflection': [
                r'(?:i think|i believe|i feel|it seems) (?:that|like) ([^.!?]+)',
                r'(?:what this means|what i\'ve learned|what i understand) (?:is|now is) ([^.!?]+)',
                r'(?:this makes me think|this suggests|this shows) (?:that|about) ([^.!?]+)',
                r'(?:the insight|the realization|what struck me) (?:is|was) ([^.!?]+)'
            ],
            'planning': [
                r'(?:the strategy|the approach|the plan) (?:is|will be) (?:to|that) ([^.!?]+)',
                r'(?:what i need to focus on|the priority|what\'s important) (?:is|right now is) ([^.!?]+)',
                r'(?:the goal|the objective|what i want to achieve) (?:is|here is) ([^.!?]+)',
                r'(?:this will help|this should|the benefit) (?:me|us|with) ([^.!?]+)'
            ],
            'idea': [
                r'(?:the concept|the idea|what if we) ([^.!?]+)',
                r'(?:this could|this might|we could) ([^.!?]+)',
                r'(?:the innovation|what\'s new|what\'s different) (?:is|about this is) ([^.!?]+)',
                r'(?:the potential|the opportunity|the possibility) (?:is|here is) ([^.!?]+)'
            ],
            'update': [
                r'(?:what happened|what changed|the update) (?:is|was) ([^.!?]+)',
                r'(?:the status|where we are|the current situation) (?:is|now is) ([^.!?]+)',
                r'(?:what\'s new|what\'s different|what\'s changed) (?:is|since) ([^.!?]+)',
                r'(?:the progress|what we\'ve accomplished|what we\'ve done) ([^.!?]+)'
            ]
        }

        # Get patterns for the specific topic type, with fallback to general patterns
        patterns = insight_patterns.get(topic_type, insight_patterns.get('reflection', []))

        # Add general insight patterns that work for any topic
        general_patterns = [
            r'(?:the main point|the key thing|what\'s important) (?:is|here is) ([^.!?]+)',
            r'(?:what i\'ve learned|what i understand|what i realize) (?:is|now is) ([^.!?]+)',
            r'(?:this tells me|this shows me|this means) ([^.!?]+)',
            r'(?:the bottom line|in summary|essentially) ([^.!?]+)'
        ]
        patterns.extend(general_patterns)

        seen_insights = set()

        # Extract insights using patterns
        for pattern in patterns:
            matches = re.finditer(pattern, conversation_text, re.IGNORECASE)
            for match in matches:
                insight_text = match.group(1).strip()
                insight_text = self._clean_insight(insight_text)

                if len(insight_text) >= 15 and insight_text.lower() not in seen_insights:
                    seen_insights.add(insight_text.lower())
                    insights.append(insight_text)

        # If we don't have enough insights, extract from emphatic statements
        if len(insights) < 3:
            emphatic_insights = self._extract_emphatic_insights(conversation_text)
            for insight in emphatic_insights:
                clean_insight = self._clean_insight(insight)
                if len(clean_insight) >= 15 and clean_insight.lower() not in seen_insights:
                    seen_insights.add(clean_insight.lower())
                    insights.append(clean_insight)

        return insights[:5]  # Return top 5 insights

    def _clean_insight(self, insight_text: str) -> str:
        """Clean and normalize insight text."""
        # Remove common prefixes/suffixes
        insight_text = re.sub(r'^(that\s+|the\s+|how\s+)', '', insight_text, flags=re.IGNORECASE)
        insight_text = re.sub(r'\s*(right now|today|currently)\s*$', '', insight_text, flags=re.IGNORECASE)

        # Capitalize first letter
        insight_text = insight_text.strip()
        if insight_text:
            insight_text = insight_text[0].upper() + insight_text[1:]

        return insight_text

    def _extract_emphatic_insights(self, text: str) -> List[str]:
        """Extract insights from emphatic statements and strong language."""
        emphatic_patterns = [
            r'(?:really|truly|definitely|certainly|absolutely) ([^.!?]{15,})',
            r'(?:it\'s clear|it\'s obvious|it\'s important) (?:that|to) ([^.!?]+)',
            r'(?:what matters|what counts|what\'s crucial) (?:is|most is) ([^.!?]+)',
            r'(?:i\'m convinced|i\'m certain|i believe strongly) (?:that|in) ([^.!?]+)'
        ]

        insights = []
        for pattern in emphatic_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                insights.append(match.group(1).strip())

        return insights

    def format_key_insights_section(self, key_insights: List[str]) -> str:
        """
        Format key insights into a markdown section.

        Args:
            key_insights: List of key insights

        Returns:
            Formatted key insights section
        """
        if not key_insights:
            return "## Key Insights\n\n*No specific insights identified.*\n"

        lines = ["## Key Insights\n"]
        for i, insight in enumerate(key_insights, 1):
            lines.append(f"{i}. {insight}")
        lines.append("")

        return "\n".join(lines)

    def format_complete_note(self, metadata: Dict[str, Any]) -> str:
        """
        Format a complete note with YAML frontmatter and all content sections.

        Args:
            metadata: Dictionary containing all note metadata including transcript and conversation

        Returns:
            Complete formatted markdown note
        """
        # Build YAML frontmatter
        yaml_lines = ["---"]
        yaml_lines.append(f"title: \"{metadata.get('title', 'Voice Note')}\"")
        yaml_lines.append(f"created: {metadata.get('created', '')}")
        yaml_lines.append(f"duration: {metadata.get('duration', 0)}")
        yaml_lines.append(f"topic: {metadata.get('topic', 'general')}")
        yaml_lines.append(f"source: voice_recording")
        if metadata.get('degraded_mode'):
            yaml_lines.append(f"degraded_mode: true")
            yaml_lines.append(f"unavailable_services: {metadata.get('unavailable_services', [])}")
        yaml_lines.append("---")
        yaml_lines.append("")

        # Add main content
        content_lines = []

        # Add transcript
        content_lines.append("## Original Transcript")
        content_lines.append("")
        content_lines.append(metadata.get('transcript', 'No transcript available.'))
        content_lines.append("")

        # Add conversation if available
        if metadata.get('conversation_result'):
            conversation_lines = self.format_conversation(
                metadata['conversation_result'].get('exchanges', [])
            )
            content_lines.append(conversation_lines)

        # Combine all parts
        return "\n".join(yaml_lines + content_lines)

    def generate_title(self, key_insight: str, topic_type: str = None,
                      fallback_words: List[str] = None) -> str:
        """
        Auto-generate meaningful title from key insight or conversation content.

        Args:
            key_insight: Primary insight or first few words of conversation
            topic_type: Type of conversation for context
            fallback_words: Fallback words if insight is too short

        Returns:
            Generated title for the conversation
        """
        if not key_insight:
            # Use fallback or generic title
            if fallback_words:
                title_base = " ".join(fallback_words[:6])
            else:
                title_base = "Voice Note"

            if topic_type:
                return f"{topic_type.title()}: {title_base}"
            else:
                return title_base

        # Clean and prepare the insight for title generation
        clean_insight = re.sub(r'^[^\w]+|[^\w]+$', '', key_insight)
        clean_insight = re.sub(r'\s+', ' ', clean_insight).strip()

        # Extract the most meaningful part for the title
        title_words = clean_insight.split()

        # Remove common filler words from the beginning
        filler_words = {'the', 'a', 'an', 'that', 'this', 'what', 'how', 'why', 'when', 'where'}
        while title_words and title_words[0].lower() in filler_words:
            title_words.pop(0)

        # Limit title length (aim for 6-8 words max)
        if len(title_words) > 8:
            title_words = title_words[:8]
        elif len(title_words) < 3 and fallback_words:
            # If insight is too short, supplement with fallback words
            additional_words = fallback_words[:5-len(title_words)]
            title_words.extend(additional_words)

        # Create title with proper capitalization
        if not title_words:
            title = "Voice Note Session"
        else:
            title = " ".join(title_words)
            # Capitalize first letter and important words
            title = self._capitalize_title(title)

        # Add topic type prefix if available and not already included
        if topic_type and topic_type.lower() not in title.lower():
            title = f"{topic_type.title()}: {title}"

        # Ensure title is not too long
        if len(title) > 60:
            title = title[:57] + "..."

        return title

    def _capitalize_title(self, title: str) -> str:
        """Capitalize title following title case rules."""
        # Words that should not be capitalized (unless first or last word)
        articles_prepositions = {
            'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at',
            'to', 'from', 'by', 'of', 'in', 'with', 'without'
        }

        words = title.split()
        if not words:
            return title

        # Always capitalize first and last word
        capitalized_words = []
        for i, word in enumerate(words):
            if i == 0 or i == len(words) - 1:
                capitalized_words.append(word.capitalize())
            elif word.lower() in articles_prepositions:
                capitalized_words.append(word.lower())
            else:
                capitalized_words.append(word.capitalize())

        return " ".join(capitalized_words)

    def create_wikilinks(self, entities: List[str], topics: List[str],
                        existing_notes: List[str] = None) -> str:
        """
        Auto-generate wikilinks to related notes and concepts.

        Args:
            entities: List of entities/people mentioned in conversation
            topics: List of topics/concepts discussed
            existing_notes: List of existing note titles to link to

        Returns:
            Formatted wikilinks section as markdown string
        """
        if existing_notes is None:
            existing_notes = []

        all_linkable_items = []

        # Process entities (people, places, organizations)
        if entities:
            for entity in entities:
                clean_entity = self._clean_wikilink_text(entity)
                if clean_entity and len(clean_entity) > 2:
                    # Check if we have an existing note that matches
                    matching_note = self._find_matching_note(clean_entity, existing_notes)
                    if matching_note:
                        all_linkable_items.append(f"[[{matching_note}]]")
                    else:
                        all_linkable_items.append(f"[[{clean_entity}]]")

        # Process topics and concepts
        if topics:
            for topic in topics:
                clean_topic = self._clean_wikilink_text(topic)
                if clean_topic and len(clean_topic) > 2:
                    # Avoid duplicates
                    topic_link = f"[[{clean_topic}]]"
                    if topic_link not in all_linkable_items:
                        matching_note = self._find_matching_note(clean_topic, existing_notes)
                        if matching_note:
                            all_linkable_items.append(f"[[{matching_note}]]")
                        else:
                            all_linkable_items.append(topic_link)

        # If no links found, return empty section
        if not all_linkable_items:
            return ""

        # Format the wikilinks section
        lines = ["## Related Notes and Concepts\n"]

        # Group by type if we can distinguish
        entity_links = [link for link in all_linkable_items if any(
            name.lower() in link.lower() for name in entities
        )] if entities else []

        topic_links = [link for link in all_linkable_items if link not in entity_links]

        if entity_links:
            lines.append("**People & Entities:**")
            lines.append(" • ".join(entity_links))
            lines.append("")

        if topic_links:
            if entity_links:  # Only add header if we also have entities
                lines.append("**Topics & Concepts:**")
            lines.append(" • ".join(topic_links))
            lines.append("")

        return "\n".join(lines)

    def _clean_wikilink_text(self, text: str) -> str:
        """Clean text for use in wikilinks."""
        # Remove special characters but keep spaces and hyphens
        clean_text = re.sub(r'[^\w\s\-]', '', text)
        # Normalize whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        # Title case for consistency
        clean_text = clean_text.title()
        return clean_text

    def _find_matching_note(self, search_term: str, existing_notes: List[str]) -> str:
        """Find the best matching existing note for a search term."""
        if not existing_notes:
            return None

        search_lower = search_term.lower()

        # Look for exact matches first
        for note in existing_notes:
            if note.lower() == search_lower:
                return note

        # Look for partial matches
        for note in existing_notes:
            if search_lower in note.lower() or note.lower() in search_lower:
                return note

        # Look for word matches
        search_words = set(search_lower.split())
        for note in existing_notes:
            note_words = set(note.lower().split())
            if search_words & note_words:  # If there's any word overlap
                return note

        return None

    def create_complete_document(self, conversation_data: Dict[str, Any],
                               metadata: ConversationMetadata,
                               include_timestamps: bool = False,
                               existing_notes: List[str] = None) -> str:
        """
        Create a complete markdown document with all sections.

        Args:
            conversation_data: Dictionary containing conversation history and context
            metadata: Conversation metadata
            include_timestamps: Whether to include timestamps in conversation
            existing_notes: List of existing note titles for wikilink generation

        Returns:
            Complete formatted markdown document
        """
        # Extract conversation text for analysis
        if 'context_history' in conversation_data:
            conversation_text = "\n".join(conversation_data['context_history'])
            formatted_conversation = self.format_conversation_from_history(
                conversation_data['context_history'], include_timestamps
            )
        elif 'exchanges' in conversation_data:
            conversation_text = "\n".join([ex.content for ex in conversation_data['exchanges']])
            formatted_conversation = self.format_conversation(
                conversation_data['exchanges'], include_timestamps
            )
        else:
            conversation_text = str(conversation_data.get('text', ''))
            formatted_conversation = f"## Conversation\n\n{conversation_text}\n"

        # Extract key insights and action items
        key_insights = self.extract_key_insights(conversation_text, metadata.topic_type)
        action_items = self.extract_action_items(conversation_text)

        # Generate title from first insight or conversation start
        title_source = key_insights[0] if key_insights else conversation_text[:100]
        title = self.generate_title(title_source, metadata.topic_type)

        # Extract entities and topics for wikilinks
        entities = conversation_data.get('entities', [])
        topics = conversation_data.get('topics', [])
        wikilinks_section = self.create_wikilinks(entities, topics, existing_notes)

        # Create frontmatter
        frontmatter = self.create_frontmatter(
            metadata, title, key_insights, action_items, topics
        )

        # Build the complete document
        document_parts = [frontmatter]

        # Add summary section
        summary_section = self.create_summary_section(conversation_text, metadata)
        document_parts.append(summary_section)

        # Add key insights section
        insights_section = self.format_key_insights_section(key_insights)
        document_parts.append(insights_section)

        # Add action items section
        action_items_section = self.format_action_items_section(action_items)
        document_parts.append(action_items_section)

        # Add main conversation
        document_parts.append(formatted_conversation)

        # Add wikilinks section if we have any
        if wikilinks_section.strip():
            document_parts.append(wikilinks_section)

        return "\n".join(document_parts)