#!/usr/bin/env python3
"""
Voice Notes System - Setup Script

AI-powered voice recording and conversation system that captures audio,
transcribes it using OpenAI Whisper, and integrates with Claude Desktop.
"""

from setuptools import setup, find_packages
import os
import sys
from pathlib import Path

# Ensure we can import from src during setup
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Read version from __init__.py
def get_version():
    """Extract version from package __init__.py."""
    init_file = Path(__file__).parent / "src" / "__init__.py"
    if init_file.exists():
        with open(init_file) as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    return "1.0.0"

# Read long description from README
def get_long_description():
    """Get long description from README.md."""
    readme_file = Path(__file__).parent / "README.md"
    if readme_file.exists():
        with open(readme_file, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# Read requirements from file
def get_requirements():
    """Parse requirements.txt and return production dependencies."""
    requirements_file = Path(__file__).parent / "requirements.txt"
    if not requirements_file.exists():
        return []

    requirements = []
    with open(requirements_file, "r") as f:
        for line in f:
            line = line.strip()
            # Skip comments, empty lines, and development dependencies
            if (line and
                not line.startswith("#") and
                not line.startswith("pytest") and
                not line.startswith("black") and
                not line.startswith("flake8")):
                requirements.append(line)

    return requirements

# System-specific dependencies
def get_platform_requirements():
    """Get platform-specific requirements."""
    platform_deps = []

    if sys.platform == "darwin":  # macOS
        platform_deps.extend([
            "pyobjc-framework-Cocoa>=8.0",
            "pyobjc-framework-AVFoundation>=8.0"
        ])
    elif sys.platform == "win32":  # Windows
        platform_deps.extend([
            "pywin32>=300",
            "winsound"
        ])
    elif sys.platform.startswith("linux"):  # Linux
        platform_deps.extend([
            "python3-dev",
            "portaudio19-dev"
        ])

    return platform_deps

# Package data and assets
def get_package_data():
    """Get package data files."""
    package_data = {
        "voice_notes_system": [
            "config/*.yaml",
            "config/*.yml",
            "assets/*.png",
            "assets/*.ico",
            "templates/*.md",
            "templates/*.txt"
        ]
    }
    return package_data

# Console scripts entry points
def get_console_scripts():
    """Define console script entry points."""
    return [
        "voice-notes=voice_notes_system.cli:main",
        "voice-notes-setup=voice_notes_system.setup_config:main",
        "voice-notes-validate=voice_notes_system.validate_config:main",
        "voice-notes-server=voice_notes_system.mcp_server:main",
        "voice-notes-tray=voice_notes_system.system_tray:main"
    ]

# GUI entry points
def get_gui_scripts():
    """Define GUI script entry points."""
    return [
        "Voice Notes System=voice_notes_system.voice_notes_app:main"
    ]

# Classifiers for PyPI
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Multimedia :: Sound/Audio :: Capture/Recording",
    "Topic :: Office/Business :: Productivity",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Utilities",
    "Environment :: MacOS X",
    "Environment :: Win32 (MS Windows)",
    "Environment :: X11 Applications",
    "Natural Language :: English"
]

# Keywords for PyPI
KEYWORDS = [
    "voice", "notes", "audio", "recording", "transcription", "whisper",
    "ai", "claude", "productivity", "speech-to-text", "voice-to-text",
    "note-taking", "conversation", "mcp", "desktop", "system-tray"
]

# Project URLs
PROJECT_URLS = {
    "Homepage": "https://github.com/your-org/voice-notes-system",
    "Documentation": "https://github.com/your-org/voice-notes-system/blob/main/docs/",
    "Source": "https://github.com/your-org/voice-notes-system",
    "Tracker": "https://github.com/your-org/voice-notes-system/issues",
    "Changelog": "https://github.com/your-org/voice-notes-system/blob/main/CHANGELOG.md",
    "Funding": "https://github.com/sponsors/your-org"
}

# Optional dependencies
EXTRAS_REQUIRE = {
    "dev": [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.0.0",
        "pytest-mock>=3.10.0",
        "black>=23.0.0",
        "flake8>=5.0.0",
        "mypy>=1.0.0",
        "pre-commit>=3.0.0",
        "bandit>=1.7.0"
    ],
    "performance": [
        "psutil>=5.9.0",
        "memory-profiler>=0.60.0"
    ],
    "encryption": [
        "cryptography>=3.4.8"
    ],
    "cloud": [
        "boto3>=1.26.0",
        "google-cloud-storage>=2.7.0",
        "azure-storage-blob>=12.14.0"
    ],
    "all": [
        "pytest>=7.0.0", "pytest-asyncio>=0.21.0", "pytest-cov>=4.0.0",
        "pytest-mock>=3.10.0", "black>=23.0.0", "flake8>=5.0.0",
        "mypy>=1.0.0", "pre-commit>=3.0.0", "bandit>=1.7.0",
        "psutil>=5.9.0", "memory-profiler>=0.60.0",
        "cryptography>=3.4.8",
        "boto3>=1.26.0", "google-cloud-storage>=2.7.0", "azure-storage-blob>=12.14.0"
    ]
}

# Main setup configuration
setup(
    # Basic package information
    name="voice-notes-system",
    version=get_version(),
    author="Your Name",
    author_email="your.email@example.com",
    maintainer="Voice Notes Team",
    maintainer_email="team@voicenotes.example.com",

    # Package description
    description="AI-powered voice recording and conversation system with Claude Desktop integration",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",

    # URLs and links
    url="https://github.com/your-org/voice-notes-system",
    project_urls=PROJECT_URLS,

    # Package discovery
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data=get_package_data(),
    include_package_data=True,

    # Dependencies
    python_requires=">=3.9",
    install_requires=get_requirements(),
    extras_require=EXTRAS_REQUIRE,

    # Entry points
    entry_points={
        "console_scripts": get_console_scripts(),
        "gui_scripts": get_gui_scripts()
    },

    # Metadata
    classifiers=CLASSIFIERS,
    keywords=", ".join(KEYWORDS),
    license="MIT",
    platforms=["any"],

    # Package options
    zip_safe=False,

    # Testing
    test_suite="tests",
    tests_require=EXTRAS_REQUIRE["dev"],

    # Data files
    data_files=[
        ("share/voice-notes-system/config", [
            "config/config.yaml",
            "config/prompts.yaml"
        ]),
        ("share/voice-notes-system/docs", [
            "docs/USER_GUIDE.md",
            "docs/INSTALLATION_GUIDE.md",
            "docs/TROUBLESHOOTING.md"
        ]),
        ("share/applications", ["packaging/voice-notes-system.desktop"]),
        ("share/icons/hicolor/256x256/apps", ["assets/voice-notes-icon.png"])
    ],

    # Options
    options={
        "build": {
            "build_base": "build"
        },
        "bdist_wheel": {
            "universal": False
        }
    }
)