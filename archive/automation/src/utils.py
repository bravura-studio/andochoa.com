#!/usr/bin/env python3
"""
Utility functions for the vault automation system
Common helper functions for logging, file operations, and state management
"""

import json
import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


def setup_logging(log_level: int = logging.INFO, log_file: Optional[str] = None) -> logging.Logger:
    """Set up logging configuration"""
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use rotating file handler to manage log size
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    return logger


def load_state(state_file: Path, default: Optional[Dict] = None) -> Dict:
    """Load state from JSON file with error handling"""
    
    if default is None:
        default = {}
    
    try:
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
                
            # Merge with defaults to ensure all keys are present
            merged_state = default.copy()
            merged_state.update(state)
            return merged_state
        else:
            return default.copy()
            
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"Error loading state from {state_file}: {e}")
        return default.copy()


def save_state(state_file: Path, state: Dict) -> bool:
    """Save state to JSON file with error handling"""
    
    try:
        # Ensure parent directory exists
        state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Add metadata
        state_to_save = state.copy()
        state_to_save['_metadata'] = {
            'last_updated': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        # Write atomically by using temporary file
        temp_file = state_file.with_suffix('.tmp')
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(state_to_save, f, indent=2, ensure_ascii=False)
        
        # Atomic move
        temp_file.replace(state_file)
        
        return True
        
    except (IOError, OSError) as e:
        logging.error(f"Error saving state to {state_file}: {e}")
        return False


def ensure_directory(path: Path, create: bool = True) -> bool:
    """Ensure directory exists and is writable"""
    
    try:
        if not path.exists():
            if create:
                path.mkdir(parents=True, exist_ok=True)
            else:
                return False
        
        # Check if directory is writable
        test_file = path / '.write_test'
        try:
            test_file.touch()
            test_file.unlink()
            return True
        except (IOError, OSError):
            return False
            
    except (IOError, OSError) as e:
        logging.error(f"Error with directory {path}: {e}")
        return False


def safe_read_file(file_path: Path, encoding: str = 'utf-8') -> Optional[str]:
    """Safely read file content with error handling"""
    
    try:
        if file_path.exists() and file_path.is_file():
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        else:
            logging.warning(f"File does not exist: {file_path}")
            return None
            
    except (IOError, OSError, UnicodeDecodeError) as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return None


def safe_write_file(file_path: Path, content: str, encoding: str = 'utf-8', 
                   backup: bool = True) -> bool:
    """Safely write file content with backup and error handling"""
    
    try:
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create backup if file exists and backup is requested
        if backup and file_path.exists():
            backup_path = file_path.with_suffix(f'{file_path.suffix}.backup')
            try:
                file_path.replace(backup_path)
                logging.debug(f"Created backup: {backup_path}")
            except OSError as e:
                logging.warning(f"Could not create backup for {file_path}: {e}")
        
        # Write content atomically
        temp_file = file_path.with_suffix('.tmp')
        
        with open(temp_file, 'w', encoding=encoding) as f:
            f.write(content)
        
        temp_file.replace(file_path)
        return True
        
    except (IOError, OSError, UnicodeEncodeError) as e:
        logging.error(f"Error writing file {file_path}: {e}")
        return False


def get_file_age(file_path: Path) -> Optional[float]:
    """Get file age in seconds"""
    
    try:
        if file_path.exists():
            return datetime.now().timestamp() - file_path.stat().st_mtime
        return None
    except OSError:
        return None


def find_files_by_pattern(directory: Path, pattern: str, 
                         recursive: bool = True) -> list[Path]:
    """Find files matching a pattern"""
    
    try:
        if recursive:
            return list(directory.rglob(pattern))
        else:
            return list(directory.glob(pattern))
    except OSError as e:
        logging.error(f"Error searching for files in {directory}: {e}")
        return []


def parse_yaml_frontmatter(content: str) -> tuple[Optional[Dict], str]:
    """Parse YAML frontmatter from markdown content"""
    
    lines = content.split('\n')
    
    # Check if content starts with frontmatter
    if not lines or lines[0].strip() != '---':
        return None, content
    
    # Find closing frontmatter marker
    yaml_lines = []
    content_lines = lines[1:]
    frontmatter_end = None
    
    for i, line in enumerate(content_lines):
        if line.strip() == '---':
            frontmatter_end = i
            break
        yaml_lines.append(line)
    
    if frontmatter_end is None:
        return None, content
    
    # Parse YAML
    try:
        import yaml
        yaml_content = '\n'.join(yaml_lines)
        frontmatter = yaml.safe_load(yaml_content) if yaml_content.strip() else {}
        
        # Get remaining content
        remaining_content = '\n'.join(content_lines[frontmatter_end + 1:])
        
        return frontmatter, remaining_content
        
    except ImportError:
        logging.warning("PyYAML not available, cannot parse frontmatter")
        return None, content
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML frontmatter: {e}")
        return None, content


def update_yaml_frontmatter(content: str, updates: Dict) -> str:
    """Update YAML frontmatter in markdown content"""
    
    try:
        import yaml
        
        frontmatter, body_content = parse_yaml_frontmatter(content)
        
        if frontmatter is None:
            frontmatter = {}
        
        # Update frontmatter
        frontmatter.update(updates)
        
        # Reconstruct content
        yaml_content = yaml.dump(frontmatter, default_flow_style=False, 
                               allow_unicode=True, sort_keys=False)
        
        new_content = f"---\n{yaml_content}---\n{body_content}"
        
        return new_content
        
    except ImportError:
        logging.warning("PyYAML not available, cannot update frontmatter")
        return content
    except yaml.YAMLError as e:
        logging.error(f"Error updating YAML frontmatter: {e}")
        return content


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds//60:.0f}m {seconds%60:.0f}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours:.0f}h {minutes:.0f}m"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def validate_file_path(file_path: str, allowed_extensions: Optional[list] = None) -> bool:
    """Validate file path for safety"""
    
    try:
        path = Path(file_path)
        
        # Check for path traversal attempts
        if '..' in path.parts:
            return False
        
        # Check file extension if specified
        if allowed_extensions and path.suffix.lower() not in allowed_extensions:
            return False
        
        return True
        
    except Exception:
        return False


def get_system_info() -> Dict[str, Any]:
    """Get basic system information"""
    
    import platform
    import sys
    
    return {
        'python_version': sys.version,
        'platform': platform.platform(),
        'processor': platform.processor(),
        'machine': platform.machine(),
        'current_time': datetime.now().isoformat(),
        'working_directory': str(Path.cwd())
    }


def health_check() -> Dict[str, Any]:
    """Perform basic health check"""
    
    health = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'checks': {}
    }
    
    # Check Python version
    import sys
    if sys.version_info >= (3, 8):
        health['checks']['python_version'] = 'pass'
    else:
        health['checks']['python_version'] = 'fail'
        health['status'] = 'unhealthy'
    
    # Check required modules
    required_modules = ['requests', 'watchdog', 'yaml']
    for module in required_modules:
        try:
            __import__(module)
            health['checks'][f'module_{module}'] = 'pass'
        except ImportError:
            health['checks'][f'module_{module}'] = 'fail'
            health['status'] = 'unhealthy'
    
    return health


class Timer:
    """Simple timer context manager"""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        logging.debug(f"{self.name} took {format_duration(duration)}")
    
    def elapsed(self) -> float:
        """Get elapsed time in seconds"""
        if self.start_time:
            end = self.end_time or datetime.now()
            return (end - self.start_time).total_seconds()
        return 0.0


def main():
    """Test utility functions"""
    
    # Test logging setup
    logger = setup_logging(log_level=logging.DEBUG)
    logger.info("Testing utility functions")
    
    # Test health check
    health = health_check()
    print("Health check:", health)
    
    # Test timer
    with Timer("Test operation"):
        import time
        time.sleep(0.1)
    
    print("Utility functions test completed")


if __name__ == "__main__":
    main()