#!/usr/bin/env python3
"""
Vault Monitor Runner
Main entry point for starting the vault monitoring service
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_dir))

from vault_monitor import main

if __name__ == "__main__":
    sys.exit(main())