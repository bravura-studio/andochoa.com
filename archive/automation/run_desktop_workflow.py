#!/usr/bin/env python3
"""
Desktop Workflow Runner
Command-line interface for desktop workflows
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_dir))

from desktop_workflow_engine import main

if __name__ == "__main__":
    sys.exit(main())
