#!/usr/bin/env python3
"""
Voice Notes System - Build Script

Creates distribution packages for different platforms:
- Python wheel and source distribution
- Windows executable (via PyInstaller)
- macOS application bundle
- Linux AppImage
- Docker images
"""

import os
import sys
import subprocess
import shutil
import platform
import argparse
from pathlib import Path
import tempfile
import json

class VoiceNotesBuildSystem:
    """Build system for Voice Notes System."""

    def __init__(self, build_dir=None, clean=False):
        """Initialize build system."""
        self.root_dir = Path(__file__).parent.parent
        self.build_dir = Path(build_dir) if build_dir else self.root_dir / "build"
        self.dist_dir = self.root_dir / "dist"
        self.clean = clean

        # Platform detection
        self.system = platform.system()
        self.architecture = platform.machine()

        # Build configuration
        self.app_name = "Voice Notes System"
        self.app_version = self._get_version()
        self.python_executable = sys.executable

    def _get_version(self):
        """Get application version."""
        version_file = self.root_dir / "src" / "__init__.py"
        if version_file.exists():
            with open(version_file) as f:
                for line in f:
                    if line.startswith("__version__"):
                        return line.split("=")[1].strip().strip('"').strip("'")
        return "1.0.0"

    def clean_build_dirs(self):
        """Clean build and dist directories."""
        print("🧹 Cleaning build directories...")

        for directory in [self.build_dir, self.dist_dir]:
            if directory.exists():
                shutil.rmtree(directory)
                print(f"✅ Cleaned {directory}")

        # Clean Python cache
        for cache_dir in self.root_dir.rglob("__pycache__"):
            shutil.rmtree(cache_dir, ignore_errors=True)

        for cache_file in self.root_dir.rglob("*.pyc"):
            cache_file.unlink(missing_ok=True)

        print("✅ Cleaned Python cache files")

    def build_python_packages(self):
        """Build Python wheel and source distribution."""
        print("📦 Building Python packages...")

        # Ensure build tools are available
        subprocess.run([
            self.python_executable, "-m", "pip", "install",
            "--upgrade", "build", "wheel", "setuptools"
        ], check=True)

        # Build packages
        subprocess.run([
            self.python_executable, "-m", "build"
        ], cwd=self.root_dir, check=True)

        print("✅ Python packages built successfully")

    def build_windows_executable(self):
        """Build Windows executable using PyInstaller."""
        if self.system != "Windows":
            print("⚠️  Skipping Windows executable (not on Windows)")
            return

        print("🪟 Building Windows executable...")

        # Install PyInstaller
        subprocess.run([
            self.python_executable, "-m", "pip", "install", "pyinstaller"
        ], check=True)

        # Create PyInstaller spec file
        spec_content = self._create_pyinstaller_spec()
        spec_file = self.build_dir / "voice-notes.spec"
        self.build_dir.mkdir(parents=True, exist_ok=True)

        with open(spec_file, "w") as f:
            f.write(spec_content)

        # Build executable
        subprocess.run([
            "pyinstaller", "--clean", "--noconfirm", str(spec_file)
        ], cwd=self.root_dir, check=True)

        print("✅ Windows executable built successfully")

    def build_macos_app(self):
        """Build macOS application bundle."""
        if self.system != "Darwin":
            print("⚠️  Skipping macOS app (not on macOS)")
            return

        print("🍎 Building macOS application...")

        # Install py2app
        subprocess.run([
            self.python_executable, "-m", "pip", "install", "py2app"
        ], check=True)

        # Create setup file for py2app
        setup_py_content = self._create_py2app_setup()
        setup_file = self.build_dir / "setup_app.py"
        self.build_dir.mkdir(parents=True, exist_ok=True)

        with open(setup_file, "w") as f:
            f.write(setup_py_content)

        # Build app
        subprocess.run([
            self.python_executable, str(setup_file), "py2app"
        ], cwd=self.root_dir, check=True)

        print("✅ macOS application built successfully")

    def build_linux_appimage(self):
        """Build Linux AppImage."""
        if self.system != "Linux":
            print("⚠️  Skipping Linux AppImage (not on Linux)")
            return

        print("🐧 Building Linux AppImage...")

        # This would require additional AppImage tools
        # For now, we'll create a tarball distribution
        self._create_linux_tarball()

        print("✅ Linux distribution built successfully")

    def _create_linux_tarball(self):
        """Create Linux tarball distribution."""
        tarball_name = f"voice-notes-system-{self.app_version}-linux-{self.architecture}.tar.gz"
        tarball_path = self.dist_dir / tarball_name

        # Create temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            app_dir = Path(temp_dir) / "voice-notes-system"
            app_dir.mkdir()

            # Copy application files
            for item in ["src", "config", "assets", "docs"]:
                src_path = self.root_dir / item
                if src_path.exists():
                    if src_path.is_dir():
                        shutil.copytree(src_path, app_dir / item)
                    else:
                        shutil.copy2(src_path, app_dir / item)

            # Copy important files
            for item in ["README.md", "LICENSE", "requirements.txt"]:
                src_file = self.root_dir / item
                if src_file.exists():
                    shutil.copy2(src_file, app_dir / item)

            # Create launcher script
            launcher_script = app_dir / "voice-notes"
            with open(launcher_script, "w") as f:
                f.write("""#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Setting up virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

python -m src.voice_notes_app "$@"
""")
            launcher_script.chmod(0o755)

            # Create tarball
            self.dist_dir.mkdir(parents=True, exist_ok=True)
            subprocess.run([
                "tar", "-czf", str(tarball_path), "-C", temp_dir, "voice-notes-system"
            ], check=True)

    def build_docker_images(self):
        """Build Docker images."""
        print("🐳 Building Docker images...")

        dockerfile_path = self.root_dir / "Dockerfile"
        if not dockerfile_path.exists():
            print("⚠️  Dockerfile not found, skipping Docker build")
            return

        # Build main image
        subprocess.run([
            "docker", "build",
            "-t", f"voice-notes-system:{self.app_version}",
            "-t", "voice-notes-system:latest",
            str(self.root_dir)
        ], check=True)

        print("✅ Docker images built successfully")

    def _create_pyinstaller_spec(self):
        """Create PyInstaller spec file content."""
        return f'''# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Application configuration
app_name = "{self.app_name}"
app_version = "{self.app_version}"
root_dir = Path(r"{self.root_dir}")

# Analysis configuration
a = Analysis(
    [str(root_dir / "src" / "voice_notes_app.py")],
    pathex=[str(root_dir)],
    binaries=[],
    datas=[
        (str(root_dir / "config"), "config"),
        (str(root_dir / "assets"), "assets"),
        (str(root_dir / "docs"), "docs"),
    ],
    hiddenimports=[
        "voice_notes_system",
        "sounddevice",
        "soundfile",
        "pynput",
        "pystray",
        "plyer",
        "openai",
        "aiohttp",
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=["pytest", "black", "flake8"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=str(root_dir / "packaging" / "version_info.txt"),
    icon=str(root_dir / "assets" / "voice-notes-icon.ico"),
)
'''

    def _create_py2app_setup(self):
        """Create py2app setup file content."""
        return f'''#!/usr/bin/env python3
"""
py2app setup script for Voice Notes System macOS app.
"""

from setuptools import setup
from pathlib import Path

APP = ["{self.root_dir}/src/voice_notes_app.py"]
DATA_FILES = [
    ("config", ["{self.root_dir}/config"]),
    ("assets", ["{self.root_dir}/assets"]),
    ("docs", ["{self.root_dir}/docs"]),
]

OPTIONS = {{
    "argv_emulation": True,
    "iconfile": "{self.root_dir}/assets/voice-notes-icon.icns",
    "plist": {{
        "CFBundleName": "{self.app_name}",
        "CFBundleDisplayName": "{self.app_name}",
        "CFBundleVersion": "{self.app_version}",
        "CFBundleShortVersionString": "{self.app_version}",
        "CFBundleIdentifier": "com.voicenotes.system",
        "LSMinimumSystemVersion": "10.15",
        "NSMicrophoneUsageDescription": "Voice Notes System needs access to your microphone to record voice notes.",
        "NSHighResolutionCapable": True,
    }},
    "packages": ["voice_notes_system"],
    "includes": ["sounddevice", "soundfile", "pynput", "pystray", "openai"],
    "excludes": ["pytest", "black", "flake8"],
}}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={{"py2app": OPTIONS}},
    setup_requires=["py2app"],
)
'''

    def create_installer_packages(self):
        """Create platform-specific installer packages."""
        print("📦 Creating installer packages...")

        if self.system == "Windows":
            self._create_windows_installer()
        elif self.system == "Darwin":
            self._create_macos_installer()
        elif self.system == "Linux":
            self._create_linux_packages()

    def _create_windows_installer(self):
        """Create Windows installer using NSIS or Inno Setup."""
        # This would require NSIS or Inno Setup to be installed
        print("⚠️  Windows installer creation requires NSIS or Inno Setup")

    def _create_macos_installer(self):
        """Create macOS installer package."""
        # This would use pkgbuild and productbuild
        print("⚠️  macOS installer creation requires Xcode tools")

    def _create_linux_packages(self):
        """Create Linux packages (deb, rpm)."""
        # This would require fpm or platform-specific tools
        print("⚠️  Linux package creation requires additional tools")

    def run_tests(self):
        """Run test suite before building."""
        print("🧪 Running test suite...")

        try:
            subprocess.run([
                self.python_executable, "-m", "pytest",
                "tests/", "-v", "--tb=short"
            ], cwd=self.root_dir, check=True)
            print("✅ All tests passed")
            return True
        except subprocess.CalledProcessError:
            print("❌ Tests failed")
            return False

    def build_all(self, skip_tests=False):
        """Build all distribution packages."""
        print(f"🚀 Building Voice Notes System v{self.app_version}")
        print(f"📍 Platform: {self.system} {self.architecture}")

        if self.clean:
            self.clean_build_dirs()

        # Run tests first (unless skipped)
        if not skip_tests:
            if not self.run_tests():
                print("❌ Build aborted due to test failures")
                return False

        try:
            # Build Python packages (always)
            self.build_python_packages()

            # Build platform-specific packages
            if self.system == "Windows":
                self.build_windows_executable()
            elif self.system == "Darwin":
                self.build_macos_app()
            elif self.system == "Linux":
                self.build_linux_appimage()

            # Build Docker images (if Docker is available)
            try:
                self.build_docker_images()
            except subprocess.CalledProcessError:
                print("⚠️  Docker build failed (Docker may not be available)")

            # Create installer packages
            self.create_installer_packages()

            print(f"\n🎉 Build completed successfully!")
            print(f"📁 Distribution files in: {self.dist_dir}")

            # List created files
            if self.dist_dir.exists():
                print("\n📦 Created packages:")
                for file in self.dist_dir.iterdir():
                    if file.is_file():
                        size = file.stat().st_size / (1024 * 1024)  # MB
                        print(f"  {file.name} ({size:.1f} MB)")

            return True

        except Exception as e:
            print(f"\n❌ Build failed: {e}")
            return False

def main():
    """Command-line interface for build system."""
    parser = argparse.ArgumentParser(description="Voice Notes System Build Script")
    parser.add_argument("--build-dir", help="Custom build directory")
    parser.add_argument("--clean", action="store_true", help="Clean build directories first")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--python-only", action="store_true", help="Build only Python packages")
    parser.add_argument("--docker-only", action="store_true", help="Build only Docker images")

    args = parser.parse_args()

    builder = VoiceNotesBuildSystem(
        build_dir=args.build_dir,
        clean=args.clean
    )

    if args.python_only:
        builder.build_python_packages()
    elif args.docker_only:
        builder.build_docker_images()
    else:
        success = builder.build_all(skip_tests=args.skip_tests)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()