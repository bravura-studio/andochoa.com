#!/usr/bin/env python3
"""
Desktop Vault Monitor Runner  
Main entry point for desktop-based vault monitoring
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_dir))

from desktop_vault_monitor import main

if __name__ == "__main__":
    sys.exit(main())
