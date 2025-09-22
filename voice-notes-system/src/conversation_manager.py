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
class InputQuality:
    """Metrics for assessing input quality and depth potential."""
    word_count: int
    sentence_count: int
    complexity_score: float
    emotional_intensity: float
    specificity_score: float
    engagement_potential: float

    @property
    def overall_score(self) -> float:
        """Calculate overall quality score (0-1)."""
        # Weighted average of different quality metrics
        weights = {
            'complexity': 0.25,
            'emotional_intensity': 0.25,
            'specificity': 0.25,
            'engagement_potential': 0.25
        }
        return (
            weights['complexity'] * min(self.complexity_score, 1.0) +
            weights['emotional_intensity'] * min(self.emotional_intensity, 1.0) +
            weights['specificity'] * min(self.specificity_score, 1.0) +
            weights['engagement_potential'] * min(self.engagement_potential, 1.0)
        )


@dataclass
class ConversationState:
    """Tracks the current state of an ongoing conversation."""
    topic_type: TopicType
    depth_level: ConversationDepth
    follow_up_count: int = 0
    context_history: List[str] = None
    is_complete: bool = False
    input_quality: Optional[InputQuality] = None
    user_engagement_score: float = 1.0  # Tracks user fatigue (1.0 = fully engaged, 0.0 = disengaged)
    response_lengths: List[int] = None  # Track response length trends
    processing_mode: str = "standard"  # User's preferred processing mode
    natural_conclusion_detected: bool = False

    def __post_init__(self):
        if self.context_history is None:
            self.context_history = []
        if self.response_lengths is None:
            self.response_lengths = []


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

    def assess_input_quality(self, transcript: str) -> InputQuality:
        """
        Assess the quality and depth potential of input transcript.

        Args:
            transcript: The voice note transcript text

        Returns:
            InputQuality metrics for the input
        """
        if not transcript:
            return InputQuality(0, 0, 0.0, 0.0, 0.0, 0.0)

        words = transcript.split()
        sentences = [s.strip() for s in transcript.split('.') if s.strip()]

        word_count = len(words)
        sentence_count = len(sentences)

        # Calculate complexity score based on vocabulary and sentence structure
        complexity_score = self._calculate_complexity_score(transcript, words)

        # Calculate emotional intensity based on emotional keywords
        emotional_intensity = self._calculate_emotional_intensity(transcript.lower())

        # Calculate specificity score based on concrete vs abstract language
        specificity_score = self._calculate_specificity_score(transcript.lower(), words)

        # Calculate engagement potential based on question words and open-ended content
        engagement_potential = self._calculate_engagement_potential(transcript.lower())

        quality = InputQuality(
            word_count=word_count,
            sentence_count=sentence_count,
            complexity_score=complexity_score,
            emotional_intensity=emotional_intensity,
            specificity_score=specificity_score,
            engagement_potential=engagement_potential
        )

        logger.info(f"Input quality assessment: overall={quality.overall_score:.2f}, "
                   f"complexity={complexity_score:.2f}, emotion={emotional_intensity:.2f}, "
                   f"specificity={specificity_score:.2f}, engagement={engagement_potential:.2f}")

        return quality

    def _calculate_complexity_score(self, transcript: str, words: List[str]) -> float:
        """Calculate linguistic complexity score (0-1)."""
        if not words:
            return 0.0

        # Average word length (longer words suggest complexity)
        avg_word_length = sum(len(word) for word in words) / len(words)
        word_length_score = min(avg_word_length / 6.0, 1.0)  # Normalize to 0-1, lowered threshold

        # Sentence length variance and overall length
        sentences = [s.strip() for s in transcript.split('.') if s.strip()]
        if len(sentences) > 1:
            sentence_lengths = [len(s.split()) for s in sentences]
            avg_length = sum(sentence_lengths) / len(sentence_lengths)
            variance = sum((length - avg_length) ** 2 for length in sentence_lengths) / len(sentence_lengths)
            variance_score = min(variance / 30.0, 1.0)  # Lowered threshold for variance
        else:
            # Single sentence - base on length
            single_length = len(words)
            variance_score = min(single_length / 20.0, 1.0)

        # Complex connectors and phrases
        complex_patterns = [
            r'\b(however|nevertheless|furthermore|moreover|consequently|therefore)\b',
            r'\b(although|because|since|whereas|while|unless|but)\b',
            r'\b(in contrast|on the other hand|as a result|for instance|for example)\b'
        ]

        complex_matches = 0
        for pattern in complex_patterns:
            complex_matches += len(re.findall(pattern, transcript.lower()))

        complexity_bonus = min(complex_matches / 3.0, 1.0)  # Lowered threshold

        return (word_length_score * 0.4 + variance_score * 0.4 + complexity_bonus * 0.2)

    def _calculate_emotional_intensity(self, transcript_lower: str) -> float:
        """Calculate emotional intensity score (0-1)."""
        emotional_patterns = {
            'high_intensity': [
                r'\b(amazing|incredible|devastating|overwhelming|terrifying|ecstatic|furious|struggling|excited)\b',
                r'\b(absolutely|completely|totally|extremely|incredibly|desperately|really)\b',
                r'[!]{2,}|[?]{2,}'  # Multiple punctuation
            ],
            'medium_intensity': [
                r'\b(worried|frustrated|happy|sad|angry|surprised|disappointed|interested|concerned)\b',
                r'\b(very|quite|pretty|fairly|somewhat|rather|fairly)\b',
                r'[!]|[?]'  # Single punctuation
            ],
            'low_intensity': [
                r'\b(okay|fine|alright|decent|reasonable|acceptable)\b',
                r'\b(maybe|perhaps|possibly|probably|likely)\b'
            ]
        }

        high_count = sum(len(re.findall(pattern, transcript_lower)) for pattern in emotional_patterns['high_intensity'])
        medium_count = sum(len(re.findall(pattern, transcript_lower)) for pattern in emotional_patterns['medium_intensity'])
        low_count = sum(len(re.findall(pattern, transcript_lower)) for pattern in emotional_patterns['low_intensity'])

        # Weighted score with more generous scoring
        intensity_score = (high_count * 1.0 + medium_count * 0.6 + low_count * 0.3) / 5.0
        return min(intensity_score, 1.0)

    def _calculate_specificity_score(self, transcript_lower: str, words: List[str]) -> float:
        """Calculate specificity score based on concrete vs abstract language (0-1)."""
        if not words:
            return 0.0

        # Specific indicators (concrete language)
        specific_patterns = [
            r'\b\d+\b',  # Numbers
            r'\b(today|yesterday|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b',
            r'\b(morning|afternoon|evening|night|am|pm)\b',
            r'\b(here|there|this|that|these|those)\b',
            r'\b[A-Z][a-z]+\b'  # Proper nouns (simplified)
        ]

        # Abstract indicators
        abstract_patterns = [
            r'\b(maybe|perhaps|possibly|generally|usually|often|sometimes|things|stuff|something|anything)\b',
            r'\b(concept|idea|notion|thought|feeling|sense|way|aspect|issue|situation)\b'
        ]

        specific_count = sum(len(re.findall(pattern, transcript_lower)) for pattern in specific_patterns)
        abstract_count = sum(len(re.findall(pattern, transcript_lower)) for pattern in abstract_patterns)

        if specific_count + abstract_count == 0:
            return 0.5  # Neutral if no indicators

        return specific_count / (specific_count + abstract_count)

    def _calculate_engagement_potential(self, transcript_lower: str) -> float:
        """Calculate engagement potential based on open-ended content (0-1)."""
        # Question words and phrases that suggest deeper exploration
        question_patterns = [
            r'\b(why|how|what|when|where|who|which|what if)\b',
            r'\b(should|could|would|might|may)\b',
            r'\b(wondering|thinking|considering|curious|interested|worried|concerned)\b'
        ]

        # Open-ended content indicators
        openended_patterns = [
            r'\b(explore|discuss|understand|figure out|work through|dive into|consider)\b',
            r'\b(confuse|unclear|unsure|uncertain|ambiguous|struggling|decision)\b',
            r'\b(option|alternative|possibility|approach|strategy|choice)\b'
        ]

        # Definitive closing patterns (reduce engagement potential)
        closing_patterns = [
            r'\b(done|finished|complete|final|decided|resolved|solved|clear)\b',
            r'\b(that\'s it|that\'s all|nothing more|end of|wrap up)\b'
        ]

        question_count = sum(len(re.findall(pattern, transcript_lower)) for pattern in question_patterns)
        openended_count = sum(len(re.findall(pattern, transcript_lower)) for pattern in openended_patterns)
        closing_count = sum(len(re.findall(pattern, transcript_lower)) for pattern in closing_patterns)

        # More generous scoring for engagement
        engagement_score = (question_count * 0.8 + openended_count * 0.6 - closing_count * 0.4) / 3.0
        return max(0.0, min(engagement_score, 1.0))

    def determine_conversation_depth(self, transcript: str, processing_mode: str = "standard") -> ConversationDepth:
        """
        Determine conversation depth based on transcript content, quality assessment, and processing mode.

        Args:
            transcript: The voice note transcript text
            processing_mode: User's preferred processing mode (quick/standard/deep)

        Returns:
            ConversationDepth level (minimal, standard, or deep)
        """
        if not transcript:
            return ConversationDepth.STANDARD

        transcript_lower = transcript.lower()

        # Respect user's processing mode preference
        if processing_mode == "quick":
            # Quick mode: bias toward minimal depth
            max_depth = ConversationDepth.STANDARD
            logger.info("Quick processing mode: limiting to standard depth max")
        elif processing_mode == "deep":
            # Deep mode: bias toward deeper conversations
            min_depth = ConversationDepth.STANDARD
            logger.info("Deep processing mode: starting at standard depth min")
        else:
            # Standard mode: use normal logic
            max_depth = None
            min_depth = None

        # Check for explicit depth triggers first
        minimal_triggers = self.depth_triggers.get("minimal", [])
        for trigger in minimal_triggers:
            if trigger.lower() in transcript_lower:
                logger.info(f"Minimal depth detected: trigger '{trigger}' found")
                return ConversationDepth.MINIMAL

        deep_triggers = self.depth_triggers.get("deep", [])
        for trigger in deep_triggers:
            if trigger.lower() in transcript_lower:
                if processing_mode == "quick":
                    logger.info(f"Deep trigger found but quick mode active: using standard depth")
                    return ConversationDepth.STANDARD
                logger.info(f"Deep depth detected: trigger '{trigger}' found")
                return ConversationDepth.DEEP

        # Assess input quality for adaptive depth determination
        input_quality = self.assess_input_quality(transcript)

        # Use quality metrics to determine depth
        if input_quality.overall_score >= 0.7 and input_quality.engagement_potential >= 0.6:
            # High quality, high engagement potential -> Deep
            target_depth = ConversationDepth.DEEP
        elif input_quality.overall_score <= 0.3 or input_quality.word_count < 10:
            # Low quality or very short -> Minimal
            target_depth = ConversationDepth.MINIMAL
        else:
            # Medium quality -> Standard
            target_depth = ConversationDepth.STANDARD

        # Apply processing mode constraints
        if processing_mode == "quick" and target_depth == ConversationDepth.DEEP:
            target_depth = ConversationDepth.STANDARD
        elif processing_mode == "deep" and target_depth == ConversationDepth.MINIMAL:
            target_depth = ConversationDepth.STANDARD

        logger.info(f"Adaptive depth determination: {target_depth.value} "
                   f"(quality={input_quality.overall_score:.2f}, mode={processing_mode})")
        return target_depth

    def detect_user_fatigue(self, state: ConversationState, user_response: str = None) -> float:
        """
        Detect user fatigue based on response patterns and conversation history.

        Args:
            state: Current conversation state
            user_response: User's latest response (optional)

        Returns:
            Fatigue score (0.0 = no fatigue, 1.0 = high fatigue)
        """
        fatigue_indicators = []

        # Track response length trends
        if user_response:
            response_length = len(user_response.split())
            state.response_lengths.append(response_length)

            # Analyze length trend (declining lengths suggest fatigue)
            if len(state.response_lengths) >= 3:
                recent_lengths = state.response_lengths[-3:]
                if all(recent_lengths[i] >= recent_lengths[i+1] for i in range(len(recent_lengths)-1)):
                    fatigue_indicators.append(("declining_length", 0.3))

            # Very short responses
            if response_length <= 5:
                fatigue_indicators.append(("very_short_response", 0.4))

            # Check for fatigue keywords
            fatigue_keywords = [
                r'\b(tired|exhausted|enough|done|stop|finish|wrap up|that\'s all)\b',
                r'\b(i don\'t know|not sure|whatever|fine|okay|sure)\b',
                r'\b(yeah|yep|mmh|uh huh|right|correct)\b'
            ]

            response_lower = user_response.lower()
            for pattern in fatigue_keywords:
                if re.search(pattern, response_lower):
                    fatigue_indicators.append(("fatigue_keywords", 0.2))
                    break

        # Conversation length fatigue
        if state.follow_up_count >= 4:
            fatigue_indicators.append(("long_conversation", 0.3))

        # Repetitive responses (simplified detection)
        if len(state.context_history) >= 3:
            recent_responses = [item.split("User: ")[-1] for item in state.context_history[-2:]
                             if "User: " in item]
            if len(recent_responses) >= 2 and len(set(recent_responses)) == 1:
                fatigue_indicators.append(("repetitive_responses", 0.5))

        # Calculate overall fatigue score
        fatigue_score = min(sum(score for _, score in fatigue_indicators), 1.0)

        # Update state engagement score
        state.user_engagement_score = max(0.0, 1.0 - fatigue_score)

        if fatigue_indicators:
            logger.info(f"User fatigue detected: {fatigue_score:.2f} "
                       f"(indicators: {[indicator for indicator, _ in fatigue_indicators]})")

        return fatigue_score

    def detect_natural_conclusion(self, state: ConversationState, user_response: str = None) -> bool:
        """
        Detect if the conversation has reached a natural conclusion.

        Args:
            state: Current conversation state
            user_response: User's latest response (optional)

        Returns:
            True if natural conclusion detected
        """
        if state.natural_conclusion_detected:
            return True

        conclusion_indicators = []

        if user_response:
            response_lower = user_response.lower().strip()

            # Explicit conclusion phrases
            conclusion_phrases = [
                r'\b(that makes sense|i understand|that\'s helpful|got it|clear now)\b',
                r'\b(i feel better|that helps|thank you|thanks|perfect|great)\b',
                r'\b(i know what to do|i have a plan|i\'m ready|let\'s do this)\b',
                r'\b(that\'s what i needed|exactly what i wanted|that covers it)\b'
            ]

            for pattern in conclusion_phrases:
                if re.search(pattern, response_lower):
                    conclusion_indicators.append(("explicit_conclusion", True))
                    break

            # Resolution language
            resolution_patterns = [
                r'\b(resolved|solved|figured out|decided|settled|determined)\b',
                r'\b(clear path|next steps|action plan|way forward)\b',
                r'\b(makes total sense|completely understand|perfectly clear)\b',
                r'\b(overthinking|too good to pass up|opportunity)\b'  # Added for decision-making contexts
            ]

            for pattern in resolution_patterns:
                if re.search(pattern, response_lower):
                    conclusion_indicators.append(("resolution_language", True))
                    break

            # Emotional resolution (for struggle topics)
            if state.topic_type == TopicType.STRUGGLE:
                relief_patterns = [
                    r'\b(feel better|relief|weight off|less stressed|calmer|lighter)\b',
                    r'\b(not as bad|manageable|doable|possible|hopeful)\b'
                ]
                for pattern in relief_patterns:
                    if re.search(pattern, response_lower):
                        conclusion_indicators.append(("emotional_resolution", True))
                        break

            # Achievement confirmation (for win topics)
            if state.topic_type == TopicType.WIN:
                confirmation_patterns = [
                    r'\b(proud of|celebrating|worth it|accomplished|achieved)\b',
                    r'\b(really happy|so excited|feels great|amazing feeling)\b'
                ]
                for pattern in confirmation_patterns:
                    if re.search(pattern, response_lower):
                        conclusion_indicators.append(("achievement_confirmation", True))
                        break

        # Topic-specific conclusion detection
        if state.topic_type == TopicType.PLANNING and state.follow_up_count >= 2:
            # Planning topics often conclude when concrete steps are identified
            if user_response and any(word in user_response.lower() for word in
                                   ['steps', 'plan', 'schedule', 'timeline', 'next', 'action']):
                conclusion_indicators.append(("planning_concrete_steps", True))

        # Natural conversation flow conclusion
        if (state.follow_up_count >= 2 and
            state.user_engagement_score < 0.6 and  # Some fatigue detected
            not conclusion_indicators):  # But no explicit conclusion
            # This suggests natural wind-down rather than abrupt ending
            conclusion_indicators.append(("natural_wind_down", True))

        has_conclusion = len(conclusion_indicators) > 0

        if has_conclusion:
            state.natural_conclusion_detected = True
            logger.info(f"Natural conclusion detected: {[indicator for indicator, _ in conclusion_indicators]}")

        return has_conclusion

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

    def create_conversation_state(self, transcript: str, processing_mode: str = "standard") -> ConversationState:
        """
        Create initial conversation state from transcript analysis.

        Args:
            transcript: The initial voice note transcript
            processing_mode: User's preferred processing mode

        Returns:
            ConversationState object with topic, depth, and initial context
        """
        topic_type, reasoning = self.analyze_topic_type(transcript)
        depth_level = self.determine_conversation_depth(transcript, processing_mode)
        input_quality = self.assess_input_quality(transcript)

        state = ConversationState(
            topic_type=topic_type,
            depth_level=depth_level,
            follow_up_count=0,
            context_history=[f"Initial transcript: {transcript[:200]}..." if len(transcript) > 200 else transcript],
            is_complete=False,
            input_quality=input_quality,
            user_engagement_score=1.0,  # Start fully engaged
            response_lengths=[],
            processing_mode=processing_mode,
            natural_conclusion_detected=False
        )

        logger.info(f"Created adaptive conversation state: {topic_type.value}, {depth_level.value} depth, "
                   f"quality={input_quality.overall_score:.2f}, mode={processing_mode}")
        return state

    def update_conversation_context(self, state: ConversationState,
                                  user_response: str, ai_prompt: str) -> None:
        """
        Update conversation state with new exchanges and adaptive metrics.

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

        # Update adaptive metrics
        fatigue_score = self.detect_user_fatigue(state, user_response)
        natural_conclusion = self.detect_natural_conclusion(state, user_response)

        # Adaptive conversation ending logic
        max_prompts = self._get_adaptive_max_prompts(state)

        # Check various completion conditions
        completion_reasons = []

        if state.follow_up_count >= max_prompts:
            completion_reasons.append(f"reached adaptive max prompts ({max_prompts})")

        if natural_conclusion:
            completion_reasons.append("natural conclusion detected")

        if fatigue_score >= 0.7:
            completion_reasons.append(f"high user fatigue ({fatigue_score:.2f})")

        if state.follow_up_count >= self.max_follow_ups:
            completion_reasons.append(f"global max follow-ups ({self.max_follow_ups})")

        # Mark complete if any completion condition is met
        if completion_reasons:
            state.is_complete = True
            logger.info(f"Conversation marked complete: {', '.join(completion_reasons)}")

        # Trim context history if it gets too long (keep last 10 exchanges)
        if len(state.context_history) > 10:
            state.context_history = state.context_history[-10:]

        logger.debug(f"Updated adaptive conversation context: {state.follow_up_count} follow-ups, "
                    f"engagement={state.user_engagement_score:.2f}, fatigue={fatigue_score:.2f}, "
                    f"natural_conclusion={natural_conclusion}")

    def _get_adaptive_max_prompts(self, state: ConversationState) -> int:
        """
        Get adaptive maximum number of prompts based on conversation state.

        Args:
            state: Current conversation state

        Returns:
            Adaptive maximum number of prompts
        """
        base_max = self._get_max_prompts_for_depth(state.depth_level)

        # Adjust based on input quality
        if state.input_quality:
            if state.input_quality.overall_score >= 0.8:
                # Very high quality input deserves more exploration
                base_max += 1
            elif state.input_quality.overall_score <= 0.3:
                # Low quality input should be shorter
                base_max = max(1, base_max - 1)

        # Adjust based on user engagement
        if state.user_engagement_score >= 0.8:
            # Highly engaged user can handle more depth
            base_max += 1
        elif state.user_engagement_score <= 0.4:
            # Low engagement should end sooner
            base_max = max(1, base_max - 1)

        # Processing mode adjustments
        if state.processing_mode == "quick":
            base_max = min(base_max, 2)  # Cap at 2 for quick mode
        elif state.processing_mode == "deep":
            base_max += 1  # Allow one extra for deep mode

        return max(1, base_max)  # Always allow at least 1 follow-up

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

    def generate_initial_prompt(self, transcript: str, processing_mode: str = "standard") -> Tuple[str, ConversationState]:
        """
        Generate the initial conversation prompt and create adaptive conversation state.

        Args:
            transcript: The voice note transcript
            processing_mode: User's preferred processing mode

        Returns:
            Tuple of (initial_prompt, conversation_state)
        """
        # Create adaptive conversation state from transcript
        state = self.create_conversation_state(transcript, processing_mode)

        # Generate the initial prompt
        prompt = self.generate_followup(state)

        if prompt is None:
            # Fallback for minimal conversations
            prompt = "Thank you for sharing that. Is there anything specific you'd like to explore about this?"

        logger.info(f"Generated adaptive initial prompt for {state.topic_type.value} topic "
                   f"(quality={state.input_quality.overall_score:.2f}, depth={state.depth_level.value})")
        return prompt, state

    def should_continue(self, state: ConversationState, user_response: str = None) -> bool:
        """
        Determine if conversation should continue based on adaptive state analysis.

        Args:
            state: Current conversation state
            user_response: User's latest response (optional)

        Returns:
            True if conversation should continue, False if it should end
        """
        # Check if already marked as complete
        if state.is_complete:
            return False

        # Update metrics if we have a user response
        if user_response:
            fatigue_score = self.detect_user_fatigue(state, user_response)
            natural_conclusion = self.detect_natural_conclusion(state, user_response)

            # High fatigue should end conversation
            if fatigue_score >= 0.7:
                logger.info(f"Conversation should end: high user fatigue ({fatigue_score:.2f})")
                return False

            # Natural conclusion detected
            if natural_conclusion:
                logger.info(f"Conversation should end: natural conclusion detected")
                return False

        # Check adaptive maximum follow-ups
        adaptive_max = self._get_adaptive_max_prompts(state)
        if state.follow_up_count >= adaptive_max:
            logger.info(f"Conversation should end: reached adaptive max prompts ({adaptive_max})")
            return False

        # Legacy completion detection for backward compatibility
        if user_response:
            completion_detected = self._detect_completion_in_response(user_response)
            if completion_detected:
                logger.info(f"Conversation should end: legacy completion indicator detected")
                return False

        # Check global maximum
        if state.follow_up_count >= self.max_follow_ups:
            logger.info(f"Conversation should end: reached global max follow-ups ({self.max_follow_ups})")
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