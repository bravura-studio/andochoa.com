# Changelog

All notable changes to the Voice Notes System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-09-23

### Fixed
- **Critical production deployment issues resolved**
  - Fixed OpenAI API v1 compatibility errors in transcription service
  - Resolved asyncio event loop conflicts preventing file saves
  - Added missing `format_complete_note()` method in MarkdownFormatter
  - Fixed hotkey system file saving logic for proper audio file handling
  - Enhanced notification system with macOS AppleScript fallback

### Changed
- **Improved silence detection settings**
  - Increased silence duration from 2.0 to 10.0 seconds for better natural speech handling
  - Lowered silence threshold from 0.01 to 0.005 for improved sensitivity
- **Enhanced error handling**
  - Updated OpenAI API error handling for v1 SDK compatibility
  - Added robust fallback mechanisms for notification display
  - Improved synchronous/asynchronous processing coordination

### Added
- **Production deployment documentation**
  - Updated README with production setup instructions
  - Added macOS accessibility permissions setup guide
  - Enhanced quick start guide for immediate usage

### Technical Details
- Migrated from OpenAI legacy API to v1 SDK
- Implemented thread-safe audio processing with dedicated event loop
- Added comprehensive error recovery for production stability
- Enhanced global hotkey system with improved notification fallbacks

## Previous Versions
- [1.1.0] - Error recovery system implementation
- [1.0.0] - Initial voice notes system with MCP integration