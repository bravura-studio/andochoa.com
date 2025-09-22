"""
Adaptive conversation management system for voice notes.
Handles topic analysis, conversation style selection, and adaptive dialogue flow.
"""

import yaml
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TopicType(Enum):
    """Supported topic types for conversation classification."""
    STRUGGLE = "struggle"
    WIN = "win"
    REFLECTION = "reflection"
    PLANNING = "planning"
    IDEA = "idea"
    UPDATE = "update"
    OTHER = "other"


class ConversationDepth(Enum):
    """Conversation depth levels."""
    MINIMAL = "minimal"
    STANDARD = "standard"
    DEEP = "deep"


@dataclass
class ConversationState:
    """Tracks the current state of an ongoing conversation."""
    topic_type: TopicType
    depth_level: ConversationDepth
    follow_up_count: int = 0
    context_history: List[str] = None
    is_complete: bool = False

    def __post_init__(self):
        if self.context_history is None:
            self.context_history = []


class ConversationManager:
    """
    Manages adaptive conversations based on voice note transcripts.
    Analyzes topic types and generates appropriate follow-up prompts.
    """

    def __init__(self, config_path: str = "config/prompts.yaml"):
        """Initialize with prompt configuration."""
        self.config_path = config_path
        self.prompts = self._load_prompts()
        self.max_follow_ups = self.prompts.get("conversation_flow", {}).get("max_follow_ups", 5)
        self.completion_indicators = self.prompts.get("conversation_flow", {}).get("completion_indicators", [])
        self.depth_triggers = self.prompts.get("conversation_flow", {}).get("depth_triggers", {})

    def _load_prompts(self) -> Dict:
        """Load prompt templates from YAML configuration."""
        try:
            with open(self.config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logger.error(f"Prompts configuration file not found: {self.config_path}")
            return {}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing prompts YAML: {e}")
            return {}

    def analyze_topic_type(self, transcript: str) -> Tuple[TopicType, str]:
        """
        Analyze transcript to determine topic type.

        Args:
            transcript: The voice note transcript text

        Returns:
            Tuple of (TopicType, reasoning) where reasoning explains the classification
        """
        if not transcript or not transcript.strip():
            return TopicType.OTHER, "Empty or invalid transcript"

        transcript_lower = transcript.lower()

        # Define keyword patterns for each topic type
        patterns = {
            TopicType.STRUGGLE: [
                r'\b(struggle|struggling|difficult|hard|problem|issue|challenge|stuck|frustrated|overwhelmed|stressed)\b',
                r'\b(can\'t|couldn\'t|unable|failing|failed|worry|worried|anxious)\b'
            ],
            TopicType.WIN: [
                r'\b(success|successful|achieved|accomplished|completed|finished|won|victory|breakthrough)\b',
                r'\b(excited|proud|happy|thrilled|amazing|awesome|great|excellent|perfect)\b',
                r'\b(finally|at last|managed to|able to)\b'
            ],
            TopicType.REFLECTION: [
                r'\b(thinking|thought|realize|realized|understand|learned|insight|perspective|reflection)\b',
                r'\b(interesting|curious|wonder|wondering|philosophy|meaning|purpose)\b',
                r'\b(what if|it seems|i notice|i\'ve been)\b'
            ],
            TopicType.PLANNING: [
                r'\b(plan|planning|strategy|goal|goals|objective|target|schedule|timeline|roadmap)\b',
                r'\b(need to|should|will|going to|next|future|upcoming|prepare|organize)\b',
                r'\b(steps|action|approach|method|process)\b'
            ],
            TopicType.IDEA: [
                r'\b(idea|concept|innovation|creative|invention|solution|possibility|opportunity)\b',
                r'\b(what about|imagine|envision|brainstorm|think about|came up with)\b',
                r'\b(new|novel|different|alternative|better way)\b'
            ],
            TopicType.UPDATE: [
                r'\b(update|progress|status|report|happened|occurred|went|did|finished)\b',
                r'\b(today|yesterday|this week|recently|currently|now|just)\b',
                r'\b(meeting|call|event|situation|development)\b'
            ]
        }

        # Score each topic type based on pattern matches
        scores = {}
        for topic_type, pattern_list in patterns.items():
            score = 0
            matched_terms = []

            for pattern in pattern_list:
                matches = re.findall(pattern, transcript_lower)
                score += len(matches)
                matched_terms.extend(matches)

            scores[topic_type] = {
                'score': score,
                'matches': matched_terms
            }

        # Find the highest scoring topic type
        best_topic = TopicType.OTHER
        best_score = 0
        best_matches = []

        for topic_type, data in scores.items():
            if data['score'] > best_score:
                best_score = data['score']
                best_topic = topic_type
                best_matches = data['matches']

        # Generate reasoning
        if best_score == 0:
            reasoning = "No clear topic indicators found, classified as general content"
        else:
            reasoning = f"Classified as {best_topic.value} based on keywords: {', '.join(set(best_matches[:3]))}"

        logger.info(f"Topic analysis: {best_topic.value} (score: {best_score}) - {reasoning}")
        return best_topic, reasoning

    def determine_conversation_depth(self, transcript: str) -> ConversationDepth:
        """
        Determine conversation depth based on transcript content and depth triggers.

        Args:
            transcript: The voice note transcript text

        Returns:
            ConversationDepth level (minimal, standard, or deep)
        """
        if not transcript:
            return ConversationDepth.STANDARD

        transcript_lower = transcript.lower()

        # Check for minimal depth triggers
        minimal_triggers = self.depth_triggers.get("minimal", [])
        for trigger in minimal_triggers:
            if trigger.lower() in transcript_lower:
                logger.info(f"Minimal depth detected: trigger '{trigger}' found")
                return ConversationDepth.MINIMAL

        # Check for deep depth triggers
        deep_triggers = self.depth_triggers.get("deep", [])
        for trigger in deep_triggers:
            if trigger.lower() in transcript_lower:
                logger.info(f"Deep depth detected: trigger '{trigger}' found")
                return ConversationDepth.DEEP

        # Check transcript length as additional factor
        word_count = len(transcript.split())
        if word_count < 10:
            return ConversationDepth.MINIMAL
        elif word_count > 50:
            return ConversationDepth.DEEP

        logger.info("Standard depth level assigned")
        return ConversationDepth.STANDARD

    def select_conversation_style(self, topic_type: TopicType) -> Dict[str, any]:
        """
        Select appropriate conversation style based on topic type.

        Args:
            topic_type: The classified topic type

        Returns:
            Dictionary containing initial_prompt and follow_up_prompts for the topic
        """
        conversation_styles = self.prompts.get("conversation_styles", {})
        topic_key = topic_type.value

        if topic_key not in conversation_styles:
            logger.warning(f"No conversation style found for topic: {topic_key}, using 'other'")
            topic_key = "other"

        style = conversation_styles.get(topic_key, {})

        # Ensure we have default values if the configuration is incomplete
        result = {
            "initial_prompt": style.get("initial_prompt", "I'd like to understand more about what you're sharing."),
            "follow_up_prompts": style.get("follow_up_prompts", [
                "Can you tell me more about this?",
                "What's most important to you about this topic?",
                "What would be helpful to explore further?"
            ])
        }

        logger.info(f"Selected conversation style for {topic_type.value}: {len(result['follow_up_prompts'])} follow-ups available")
        return result

    def create_conversation_state(self, transcript: str) -> ConversationState:
        """
        Create initial conversation state from transcript analysis.

        Args:
            transcript: The initial voice note transcript

        Returns:
            ConversationState object with topic, depth, and initial context
        """
        topic_type, reasoning = self.analyze_topic_type(transcript)
        depth_level = self.determine_conversation_depth(transcript)

        state = ConversationState(
            topic_type=topic_type,
            depth_level=depth_level,
            follow_up_count=0,
            context_history=[f"Initial transcript: {transcript[:200]}..." if len(transcript) > 200 else transcript],
            is_complete=False
        )

        logger.info(f"Created conversation state: {topic_type.value}, {depth_level.value} depth")
        return state

    def update_conversation_context(self, state: ConversationState,
                                  user_response: str, ai_prompt: str) -> None:
        """
        Update conversation state with new exchanges.

        Args:
            state: Current conversation state to update
            user_response: User's response to the last prompt
            ai_prompt: The AI prompt that was sent
        """
        # Add the exchange to context history
        exchange = f"AI: {ai_prompt}\nUser: {user_response}"
        state.context_history.append(exchange)

        # Increment follow-up count
        state.follow_up_count += 1

        # Check if conversation should end based on max follow-ups
        if state.follow_up_count >= self.max_follow_ups:
            state.is_complete = True
            logger.info(f"Conversation marked complete: reached max follow-ups ({self.max_follow_ups})")

        # Trim context history if it gets too long (keep last 10 exchanges)
        if len(state.context_history) > 10:
            state.context_history = state.context_history[-10:]

        logger.debug(f"Updated conversation context: {state.follow_up_count} follow-ups, "
                    f"{len(state.context_history)} context items")

    def get_conversation_context(self, state: ConversationState) -> str:
        """
        Get formatted conversation context for prompt generation.

        Args:
            state: Current conversation state

        Returns:
            Formatted string containing relevant conversation context
        """
        if not state.context_history:
            return ""

        # Format the context for inclusion in prompts
        context_lines = []
        context_lines.append(f"Conversation Topic: {state.topic_type.value}")
        context_lines.append(f"Depth Level: {state.depth_level.value}")
        context_lines.append(f"Follow-up Count: {state.follow_up_count}")
        context_lines.append("\nConversation History:")

        # Include last few exchanges for context
        recent_history = state.context_history[-3:] if len(state.context_history) > 3 else state.context_history
        for i, item in enumerate(recent_history):
            context_lines.append(f"{i+1}. {item}")

        return "\n".join(context_lines)

    def generate_followup(self, state: ConversationState) -> Optional[str]:
        """
        Generate appropriate follow-up prompt based on conversation state.

        Args:
            state: Current conversation state

        Returns:
            Follow-up prompt string, or None if conversation should end
        """
        # Check if conversation is already marked as complete
        if state.is_complete:
            return None

        # Get the conversation style for this topic
        style = self.select_conversation_style(state.topic_type)

        # If this is the first follow-up, use the initial prompt
        if state.follow_up_count == 0:
            return style["initial_prompt"]

        # Get available follow-up prompts
        follow_up_prompts = style["follow_up_prompts"]

        if not follow_up_prompts:
            logger.warning(f"No follow-up prompts available for topic: {state.topic_type.value}")
            return None

        # Adjust number of follow-ups based on conversation depth
        max_prompts = self._get_max_prompts_for_depth(state.depth_level)

        if state.follow_up_count >= max_prompts:
            logger.info(f"Reached max prompts for {state.depth_level.value} depth: {max_prompts}")
            return None

        # Select prompt based on follow-up count (cycling through available prompts)
        prompt_index = (state.follow_up_count - 1) % len(follow_up_prompts)
        selected_prompt = follow_up_prompts[prompt_index]

        logger.info(f"Generated follow-up {state.follow_up_count}: {selected_prompt[:50]}...")
        return selected_prompt

    def _get_max_prompts_for_depth(self, depth: ConversationDepth) -> int:
        """
        Get maximum number of prompts based on conversation depth.

        Args:
            depth: Conversation depth level

        Returns:
            Maximum number of prompts for this depth
        """
        depth_limits = {
            ConversationDepth.MINIMAL: 1,
            ConversationDepth.STANDARD: 3,
            ConversationDepth.DEEP: 5
        }
        return depth_limits.get(depth, 3)

    def generate_initial_prompt(self, transcript: str) -> Tuple[str, ConversationState]:
        """
        Generate the initial conversation prompt and create conversation state.

        Args:
            transcript: The voice note transcript

        Returns:
            Tuple of (initial_prompt, conversation_state)
        """
        # Create conversation state from transcript
        state = self.create_conversation_state(transcript)

        # Generate the initial prompt
        prompt = self.generate_followup(state)

        if prompt is None:
            # Fallback for minimal conversations
            prompt = "Thank you for sharing that. Is there anything specific you'd like to explore about this?"

        logger.info(f"Generated initial prompt for {state.topic_type.value} topic")
        return prompt, state

    def should_continue(self, state: ConversationState, user_response: str = None) -> bool:
        """
        Determine if conversation should continue based on state and user response.

        Args:
            state: Current conversation state
            user_response: User's latest response (optional)

        Returns:
            True if conversation should continue, False if it should end
        """
        # Check if already marked as complete
        if state.is_complete:
            return False

        # Check if we've reached maximum follow-ups for this depth
        max_prompts = self._get_max_prompts_for_depth(state.depth_level)
        if state.follow_up_count >= max_prompts:
            logger.info(f"Conversation should end: reached max prompts ({max_prompts}) for {state.depth_level.value} depth")
            return False

        # Check user response for completion indicators
        if user_response:
            completion_detected = self._detect_completion_in_response(user_response)
            if completion_detected:
                logger.info(f"Conversation should end: completion indicator detected in user response")
                return False

        return True

    def _detect_completion_in_response(self, response: str) -> bool:
        """
        Check if user response contains completion indicators.

        Args:
            response: User's response text

        Returns:
            True if completion indicators are found
        """
        if not response:
            return False

        response_lower = response.lower().strip()

        # Check for explicit completion indicators from config
        for indicator in self.completion_indicators:
            if indicator.lower() in response_lower:
                logger.debug(f"Completion indicator found: '{indicator}'")
                return True

        # Check for short responses that suggest disengagement
        if len(response.split()) <= 3:
            short_endings = ["ok", "thanks", "good", "fine", "done", "yes", "no", "sure", "alright"]
            if response_lower in short_endings:
                logger.debug(f"Short completion response detected: '{response_lower}'")
                return True

        # Check for responses that suggest topic exhaustion
        exhaustion_patterns = [
            r'\b(nothing else|that\'s all|no more|all set|we\'re good)\b',
            r'\b(i\'m done|finished|complete|covered everything)\b',
            r'\b(that covers it|that\'s it|end of|wrap up)\b'
        ]

        for pattern in exhaustion_patterns:
            if re.search(pattern, response_lower):
                logger.debug(f"Topic exhaustion pattern found: {pattern}")
                return True

        return False

    def extract_insights(self, state: ConversationState) -> Dict[str, any]:
        """
        Extract key insights and summary from completed conversation.

        Args:
            state: Completed conversation state

        Returns:
            Dictionary containing conversation insights and metadata
        """
        if not state.context_history:
            return {"error": "No conversation history to analyze"}

        # Combine all conversation exchanges
        full_conversation = "\n".join(state.context_history)

        insights = {
            "topic_type": state.topic_type.value,
            "depth_level": state.depth_level.value,
            "total_exchanges": state.follow_up_count,
            "conversation_length": len(full_conversation),
            "conversation_history": state.context_history,
            "completion_reason": self._determine_completion_reason(state)
        }

        logger.info(f"Extracted insights from {state.topic_type.value} conversation with {state.follow_up_count} exchanges")
        return insights

    def _determine_completion_reason(self, state: ConversationState) -> str:
        """
        Determine why the conversation was completed.

        Args:
            state: Conversation state

        Returns:
            String describing completion reason
        """
        max_prompts = self._get_max_prompts_for_depth(state.depth_level)

        if state.follow_up_count >= max_prompts:
            return f"Reached maximum depth for {state.depth_level.value} conversation ({max_prompts} prompts)"
        elif state.follow_up_count >= self.max_follow_ups:
            return f"Reached global maximum follow-ups ({self.max_follow_ups})"
        else:
            return "User indicated completion or natural ending detected"

    def finalize_conversation(self, state: ConversationState) -> Dict[str, any]:
        """
        Mark conversation as complete and extract final insights.

        Args:
            state: Conversation state to finalize

        Returns:
            Final conversation summary and insights
        """
        state.is_complete = True
        insights = self.extract_insights(state)

        logger.info(f"Conversation finalized: {insights['topic_type']} with {insights['total_exchanges']} exchanges")
        return insights