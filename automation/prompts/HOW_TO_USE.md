# How to Use Claude Desktop Integration

## Quick Start:

1. **When you get a notification**: A prompt is ready for Claude Desktop
2. **Open the prompt file**: It will auto-open, or check the `prompts/` folder
3. **Copy the prompt**: Copy everything after "Agent Prompt" line
4. **Paste to Claude Desktop**: Open Claude Desktop and paste
5. **Copy Claude's response**: Copy the ENTIRE response from Claude
6. **Save response**: Save to the specified response file in `responses/` folder

## File Structure:

- `prompts/` - Ready-to-use prompts for Claude Desktop
- `responses/` - Save Claude Desktop responses here
- `contexts/` - System context files (don't modify)

## Tips:

- Keep Claude Desktop app open during workflows
- Copy ENTIRE responses, including any markdown formatting
- File names matter - use exact names specified in prompts
- System processes responses automatically after you save them

## Workflow Example:

1. System detects new file in vault
2. 🔔 Notification: "Claude Prompt Ready: Analyzer Agent"
3. Open auto-opened prompt file
4. Copy prompt → Paste to Claude Desktop
5. Copy Claude's response → Save to response file
6. System automatically processes response and updates vault
7. 🔔 Next agent notification (if needed)

That's it! The system handles everything else automatically.
