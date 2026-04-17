# Product Requirements Document: Voice Notes Capture System

## Introduction/Overview

The Voice Notes Capture System transforms spontaneous thoughts into structured insights through natural voice recording and AI-powered conversation. This feature enables founders to capture ideas instantly via global hotkey, engage in adaptive AI dialogue that mimics a cofounder conversation, and automatically save formatted notes to the Obsidian vault. The system addresses the friction between having an insight and documenting it properly, reducing the barrier from minutes to seconds.

## Goals

1. **Reduce capture friction**: Enable thought capture within 2 seconds via global hotkey (Cmd+Shift+R)
2. **Enhance insight depth**: Generate 40% deeper insights through AI-prompted exploration
3. **Maintain thought flow**: Capture ideas without breaking context or current task
4. **Increase capture volume**: Target 5-10 voice notes daily vs 1-2 written notes
5. **Improve content quality**: Generate journal-ready insights requiring <5 minutes editing

## User Stories

1. **As a founder walking to lunch**, I want to instantly capture a product realization so that I don't lose the insight while returning to my desk.

2. **As a founder processing customer feedback**, I want to verbally explore implications with an AI cofounder so that I can identify hidden patterns and action items.

3. **As a founder reviewing metrics**, I want to quickly document anomalies and hypotheses so that I can reference them in my weekly journal.

4. **As a founder having a breakthrough**, I want the AI to help me dig deeper into why this matters so that I transform fleeting thoughts into actionable insights.

5. **As a founder ending my day**, I want to brain-dump today's struggles and wins so that I have rich material for my weekly founder journal.

## Functional Requirements

### Core Recording Features
1. **The system must** activate recording instantly via global hotkey (Cmd+Shift+R)
2. **The system must** show visual indicator when recording is active (system tray icon change)
3. **The system must** support unlimited recording duration with auto-stop after 30 seconds of silence
4. **The system must** provide manual stop recording via same hotkey or ESC key
5. **The system must** play subtle audio feedback for start/stop recording events

### Transcription Pipeline
6. **The system must** use OpenAI Whisper API for transcription (targeting >95% accuracy)
7. **The system must** process audio within 3 seconds of recording completion
8. **The system must** handle multiple languages with auto-detection
9. **The system must** preserve filler words and pauses for context in raw transcript
10. **The system must** fall back to basic speech-to-text if Whisper API fails

### AI Conversation Engine
11. **The system must** analyze transcript to determine topic type (struggle/win/metric/observation)
12. **The system must** adapt conversation depth based on initial input quality (short vs detailed)
13. **The system must** select appropriate prompting style based on topic type:
    - Struggles → Challenging questioner
    - Wins → Peer discussion for lessons learned
    - Metrics → Analytical deep-dive
    - Observations → Gentle coaching for exploration
14. **The system must** generate 1-5 follow-up prompts based on conversation flow
15. **The system must** detect when user has exhausted the topic and end gracefully
16. **The system must** extract action items, key insights, and entities automatically

### User Control Options
17. **The system must** offer processing modes before each recording:
    - Quick capture (transcribe only)
    - Standard (1-2 AI exchanges)
    - Deep dive (full conversation)
18. **The system must** allow user to skip AI conversation via keyboard shortcut
19. **The system must** enable ending conversation at any point
20. **The system must** support "thinking time" pauses without ending recording

### File Management
21. **The system must** save notes with hybrid naming: `YYYY-MM-DD-HHMM-[topic-summary].md`
22. **The system must** auto-generate topic summary from main insight (max 5 words)
23. **The system must** save to `Content Bank/1-raw-ideas/voice-notes/` directory
24. **The system must** create daily subfolders when >5 notes per day
25. **The system must** generate YAML frontmatter with full metadata:
    ```yaml
    claude_analysis:
      topics: ["extracted", "topics"]
      type: "struggle|win|metric|observation"
      entities: ["Person", "Company", "Tool"]
      recording_date: "2025-01-10"
      duration_seconds: 234
      conversation_depth: 3
      processing_mode: "deep_dive"
      key_insight: "One sentence summary"
    ```

### Integration Features
26. **The system must** format notes in standard Insight Engine markdown structure
27. **The system must** generate appropriate wikilinks to existing notes
28. **The system must** provide manual trigger for Analyzer agent processing
29. **The system must** log all captures in daily activity summary
30. **The system must** delete audio files after successful transcription

### Error Handling
31. **The system must** save raw audio if transcription fails completely
32. **The system must** fallback to basic speech-to-text without AI on API failures
33. **The system must** retry failed API calls up to 3 times with exponential backoff
34. **The system must** notify user of failures via system notification
35. **The system must** maintain local queue of unprocessed recordings

## Non-Goals (Out of Scope)

1. **Will NOT** include text-to-speech for AI responses (silent operation)
2. **Will NOT** support video recording or screen capture
3. **Will NOT** provide real-time transcription during recording
4. **Will NOT** integrate with external services beyond OpenAI
5. **Will NOT** support collaborative recording sessions
6. **Will NOT** include mobile app in v1 (future consideration)
7. **Will NOT** auto-trigger Analyzer/Connector agents
8. **Will NOT** support custom wake words or voice commands
9. **Will NOT** maintain conversation history between sessions
10. **Will NOT** provide voice clone or personalized TTS

## Design Considerations

### User Interface
- **System Tray Application**: Minimal UI with status indicator
  - Green: Ready
  - Red: Recording
  - Yellow: Processing
  - Gray: Offline/Error
- **Desktop Notifications**: Subtle, non-intrusive status updates
- **Keyboard-First**: All interactions possible without mouse
- **Visual Feedback**: Recording timer and waveform in system tray popup

### Conversation UX Patterns
```
USER: [Initial thought - 15 seconds]
AI: "I hear you're struggling with [X]. What's the real cost of not solving this?"
USER: [Elaboration - 30 seconds]
AI: "Interesting. How would your best competitor handle this?"
USER: [Deeper insight - 20 seconds]
AI: "Should we capture any action items from this?"
USER: [Wrap up or continue]
```

### File Format Template
```markdown
---
[YAML frontmatter]
---

# [Auto-generated Title Based on Key Insight]

## Recording Context
*Triggered by: [What sparked this thought]*
*Processing mode: [Quick/Standard/Deep]*

## Initial Capture
[Raw initial thought, lightly formatted]

## AI Exploration

### Exchange 1: [Question Theme]
**AI**: [Prompt question]
**Response**: [User's elaboration]

### Exchange 2: [Question Theme]
**AI**: [Follow-up]
**Response**: [Deeper exploration]

## Key Insights
- [Primary realization]
- [Secondary insight]
- [Surprising connection]

## Action Items
- [ ] [Extracted action]
- [ ] [Another action]

## Related Notes
- [[Automatically detected related note]]
- [[Another connection]]

---
*Duration: X:XX | Depth: N exchanges | Generated: YYYY-MM-DD HH:MM*
```

## Technical Considerations

### Architecture Stack
- **Language**: Python 3.11+
- **Audio Capture**: `sounddevice` library with PortAudio
- **Transcription**: OpenAI Whisper API (whisper-1 model)
- **AI Processing**: Claude via MCP server integration
- **Global Hotkeys**: `pynput` or `keyboard` library
- **System Tray**: `pystray` with PIL for icons
- **File System**: Direct write via existing MCP tools
- **Configuration**: YAML config file for API keys and preferences

### API Integration
- **Whisper API**: Direct HTTP calls to OpenAI endpoint
- **Claude MCP**: Leverage existing server connection
- **Rate Limiting**: Implement queue with 50 requests/minute limit
- **Cost Control**: Track usage, alert at $5/day threshold

### Performance Requirements
- **Hotkey Response**: <100ms to start recording
- **Transcription Speed**: <3 seconds for 60-second audio
- **AI Response**: <2 seconds per exchange
- **File Save**: <500ms to write to vault
- **Memory Usage**: <200MB resident memory

### Development Environment
```python
# Required packages
dependencies = {
    'sounddevice': '0.4.6',
    'numpy': '1.24.0',
    'openai': '1.0.0',
    'pynput': '1.7.6',
    'pystray': '0.19.4',
    'Pillow': '10.0.0',
    'pyyaml': '6.0',
    'python-dateutil': '2.8.2'
}
```

## Success Metrics

### Week 1 Success Criteria
- **Capture Volume**: 20+ voice notes recorded
- **Transcription Accuracy**: >92% word accuracy
- **API Costs**: <$2 total spend
- **System Stability**: Zero crashes, <3 failed captures
- **User Friction**: <5 seconds from thought to recording

### Month 1 Success Criteria
- **Daily Usage**: 5+ voice notes per day average
- **Insight Quality**: 60% of notes referenced in weekly journal
- **Conversation Value**: 70% of AI prompts rated helpful
- **Time Savings**: 50% reduction in idea-to-note time
- **Action Items**: 30+ extracted actions executed

### Quarter 1 Success Criteria
- **Behavior Change**: Voice becomes primary capture method
- **Content Improvement**: Weekly journals show 40% more depth
- **Knowledge Graph**: 100+ new wikilinks created from voice notes
- **ROI**: 10x time savings vs manual note-taking
- **Platform Expansion**: Mobile companion app in development

## Open Questions

1. **Privacy Concerns**: Should we add local transcription option for sensitive topics?
2. **Batch Processing**: Would scheduled batch processing of recordings be valuable?
3. **Voice Profiles**: Should system adapt to speaking patterns over time?
4. **Export Options**: Need for audio archive or transcript export features?
5. **Team Features**: Future support for multiple user profiles?
6. **Integration Depth**: Direct calendar/task manager integration needed?
7. **Analytics**: What metrics would be most valuable to track?
8. **Backup Strategy**: How to handle cloud backup of recordings pre-transcription?

---

## Appendix: Conversation Prompt Bank

### For Struggles
- "What's the real cost of not solving this problem?"
- "What would happen if you did the opposite?"
- "Who else has solved this? What did they do?"
- "What's the smallest experiment you could run tomorrow?"

### For Wins  
- "What made this possible that wasn't true before?"
- "How could you systematize this success?"
- "Who else needs to know about this approach?"
- "What's the next level version of this win?"

### For Metrics
- "What story is this number trying to tell you?"
- "What would have to be true for this to double?"
- "Which assumption about your business does this challenge?"
- "What's the one action this metric demands?"

### For Observations
- "Why did this surprise you?"
- "What pattern is this part of?"
- "How does this connect to your main challenge?"
- "What experiment does this observation suggest?"

---

*PRD Version: 1.0*
*Created: 2025-01-10*
*Author: AI Development Assistant*
*Status: Ready for Implementation*