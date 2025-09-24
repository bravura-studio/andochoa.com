cd "/Users/ochoa/Documents/Build in public/Content Bank/voice-notes-system"

rm -rf dist build "Voice Notes.spec"

"/Users/ochoa/Documents/Build in public/Content Bank/.venv/bin/pyinstaller" --noconfirm --windowed --name "Voice Notes" --add-data "config:config" src/voice_notes_app.py