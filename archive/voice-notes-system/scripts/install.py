#!/usr/bin/env python3
"""
Voice Notes System - Installation Script

Automated installation script with support for:
- Virtual environment creation
- Dependency installation
- Configuration setup
- Auto-update mechanism
- Platform-specific optimizations
"""

import os
import sys
import subprocess
import platform
import argparse
import tempfile
import shutil
import json
from pathlib import Path
from urllib.request import urlopen, urlretrieve
from urllib.error import URLError

# Version and repository information
CURRENT_VERSION = "1.0.0"
REPOSITORY_URL = "https://github.com/your-org/voice-notes-system"
RELEASES_API_URL = "https://api.github.com/repos/your-org/voice-notes-system/releases/latest"
DOWNLOAD_BASE_URL = "https://github.com/your-org/voice-notes-system/archive"

# Installation paths
DEFAULT_INSTALL_PATHS = {
    "Windows": Path.home() / "AppData" / "Local" / "Voice Notes System",
    "Darwin": Path.home() / "Applications" / "Voice Notes System",
    "Linux": Path.home() / ".local" / "share" / "voice-notes-system"
}

class VoiceNotesInstaller:
    """Voice Notes System installer with auto-update capability."""

    def __init__(self, install_path=None, force_update=False, development=False):
        """Initialize installer with configuration options."""
        self.system = platform.system()
        self.install_path = Path(install_path) if install_path else DEFAULT_INSTALL_PATHS.get(self.system)
        self.force_update = force_update
        self.development = development
        self.venv_path = self.install_path / "venv"
        self.config_path = self.install_path / "config"

        if not self.install_path:
            raise ValueError(f"Unsupported platform: {self.system}")

    def check_requirements(self):
        """Check system requirements for installation."""
        print("🔍 Checking system requirements...")

        # Check Python version
        if sys.version_info < (3, 9):
            raise RuntimeError("Python 3.9 or higher is required")
        print(f"✅ Python {sys.version.split()[0]} found")

        # Check for required system tools
        required_tools = ["pip"]
        if self.system == "Darwin":
            required_tools.extend(["xcode-select"])
        elif self.system == "Linux":
            required_tools.extend(["gcc", "portaudio19-dev"])

        for tool in required_tools:
            try:
                subprocess.run([tool, "--version"], capture_output=True, check=True)
                print(f"✅ {tool} found")
            except (subprocess.CalledProcessError, FileNotFoundError):
                if tool in ["gcc", "portaudio19-dev", "xcode-select"]:
                    print(f"⚠️  {tool} not found (may need manual installation)")
                else:
                    raise RuntimeError(f"Required tool '{tool}' not found")

    def get_latest_version(self):
        """Get latest version from GitHub releases."""
        try:
            with urlopen(RELEASES_API_URL) as response:
                data = json.loads(response.read().decode())
                return data["tag_name"].lstrip("v")
        except (URLError, KeyError, json.JSONDecodeError):
            print("⚠️  Could not check for latest version, using current version")
            return CURRENT_VERSION

    def download_release(self, version):
        """Download and extract release archive."""
        print(f"⬇️  Downloading Voice Notes System v{version}...")

        download_url = f"{DOWNLOAD_BASE_URL}/v{version}.zip"
        temp_dir = Path(tempfile.mkdtemp())
        archive_path = temp_dir / f"voice-notes-{version}.zip"

        try:
            urlretrieve(download_url, archive_path)
            print(f"✅ Downloaded to {archive_path}")

            # Extract archive
            shutil.unpack_archive(archive_path, temp_dir)
            extracted_dir = temp_dir / f"voice-notes-system-{version}"

            if not extracted_dir.exists():
                # Try alternative naming
                for item in temp_dir.iterdir():
                    if item.is_dir() and "voice-notes" in item.name.lower():
                        extracted_dir = item
                        break

            return extracted_dir

        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise RuntimeError(f"Failed to download release: {e}")

    def create_virtual_environment(self):
        """Create Python virtual environment."""
        print("🐍 Creating virtual environment...")

        if self.venv_path.exists():
            if self.force_update:
                shutil.rmtree(self.venv_path)
            else:
                print("✅ Virtual environment already exists")
                return

        subprocess.run([
            sys.executable, "-m", "venv", str(self.venv_path)
        ], check=True)

        print(f"✅ Virtual environment created at {self.venv_path}")

    def get_pip_executable(self):
        """Get pip executable path for the virtual environment."""
        if self.system == "Windows":
            return self.venv_path / "Scripts" / "pip.exe"
        else:
            return self.venv_path / "bin" / "pip"

    def get_python_executable(self):
        """Get Python executable path for the virtual environment."""
        if self.system == "Windows":
            return self.venv_path / "Scripts" / "python.exe"
        else:
            return self.venv_path / "bin" / "python"

    def install_dependencies(self, source_path):
        """Install Python dependencies."""
        print("📦 Installing dependencies...")

        pip_executable = self.get_pip_executable()
        requirements_file = source_path / "requirements.txt"

        if not requirements_file.exists():
            raise FileNotFoundError("requirements.txt not found in source")

        # Upgrade pip first
        subprocess.run([
            str(pip_executable), "install", "--upgrade", "pip"
        ], check=True)

        # Install requirements
        subprocess.run([
            str(pip_executable), "install", "-r", str(requirements_file)
        ], check=True)

        print("✅ Dependencies installed successfully")

    def copy_application_files(self, source_path):
        """Copy application files to installation directory."""
        print("📁 Copying application files...")

        # Create installation directory
        self.install_path.mkdir(parents=True, exist_ok=True)

        # Copy source files
        source_dirs = ["src", "config", "assets", "docs"]
        for dir_name in source_dirs:
            source_dir = source_path / dir_name
            if source_dir.exists():
                dest_dir = self.install_path / dir_name
                if dest_dir.exists():
                    shutil.rmtree(dest_dir)
                shutil.copytree(source_dir, dest_dir)
                print(f"✅ Copied {dir_name}/")

        # Copy important files
        important_files = [
            "README.md", "CHANGELOG.md", "CONTRIBUTING.md",
            "setup_config.py", "validate_config.py", "start_mcp_server.py",
            ".env.template"
        ]
        for filename in important_files:
            source_file = source_path / filename
            if source_file.exists():
                shutil.copy2(source_file, self.install_path / filename)
                print(f"✅ Copied {filename}")

    def setup_configuration(self):
        """Set up initial configuration."""
        print("⚙️  Setting up configuration...")

        # Create config directory
        self.config_path.mkdir(exist_ok=True)

        # Copy environment template
        env_template = self.install_path / ".env.template"
        env_file = self.install_path / ".env"

        if env_template.exists() and not env_file.exists():
            shutil.copy2(env_template, env_file)
            print("✅ Created .env file from template")

        # Make setup script executable
        setup_script = self.install_path / "setup_config.py"
        if setup_script.exists():
            setup_script.chmod(0o755)
            print("✅ Made setup script executable")

    def create_launcher_scripts(self):
        """Create launcher scripts for different platforms."""
        print("🚀 Creating launcher scripts...")

        scripts_dir = self.install_path / "scripts"
        scripts_dir.mkdir(exist_ok=True)

        python_exe = self.get_python_executable()

        if self.system == "Windows":
            # Create batch file
            launcher_script = scripts_dir / "voice-notes.bat"
            with open(launcher_script, "w") as f:
                f.write(f"""@echo off
cd /d "{self.install_path}"
"{python_exe}" -m src.voice_notes_app %*
""")
            print("✅ Created Windows launcher script")

        else:
            # Create shell script
            launcher_script = scripts_dir / "voice-notes"
            with open(launcher_script, "w") as f:
                f.write(f"""#!/bin/bash
cd "{self.install_path}"
"{python_exe}" -m src.voice_notes_app "$@"
""")
            launcher_script.chmod(0o755)
            print("✅ Created Unix launcher script")

    def create_desktop_entry(self):
        """Create desktop entry for Linux systems."""
        if self.system != "Linux":
            return

        print("🖥️  Creating desktop entry...")

        desktop_dir = Path.home() / ".local" / "share" / "applications"
        desktop_dir.mkdir(parents=True, exist_ok=True)

        desktop_file = desktop_dir / "voice-notes-system.desktop"
        launcher_script = self.install_path / "scripts" / "voice-notes"

        with open(desktop_file, "w") as f:
            f.write(f"""[Desktop Entry]
Name=Voice Notes System
Comment=AI-powered voice recording and conversation system
Exec={launcher_script}
Icon={self.install_path}/assets/voice-notes-icon.png
Terminal=false
Type=Application
Categories=Office;AudioVideo;Audio;
StartupNotify=true
""")

        print("✅ Created desktop entry")

    def create_auto_updater(self):
        """Create auto-update mechanism."""
        print("🔄 Setting up auto-updater...")

        updater_script = self.install_path / "scripts" / "update.py"
        with open(updater_script, "w") as f:
            f.write(f'''#!/usr/bin/env python3
"""Auto-updater script for Voice Notes System."""

import sys
import subprocess
from pathlib import Path

def main():
    """Run the installer with update flag."""
    installer_path = Path(__file__).parent.parent / "scripts" / "install.py"
    install_path = "{self.install_path}"

    subprocess.run([
        sys.executable, str(installer_path),
        "--install-path", install_path,
        "--force-update"
    ])

if __name__ == "__main__":
    main()
''')

        updater_script.chmod(0o755)
        print("✅ Created auto-updater script")

    def create_uninstaller(self):
        """Create uninstaller script."""
        print("🗑️  Creating uninstaller...")

        uninstaller_script = self.install_path / "scripts" / "uninstall.py"
        with open(uninstaller_script, "w") as f:
            f.write(f'''#!/usr/bin/env python3
"""Uninstaller script for Voice Notes System."""

import shutil
import sys
from pathlib import Path

def main():
    """Uninstall Voice Notes System."""
    install_path = Path("{self.install_path}")

    print("🗑️  Uninstalling Voice Notes System...")

    if install_path.exists():
        shutil.rmtree(install_path)
        print("✅ Voice Notes System uninstalled successfully")
    else:
        print("⚠️  Installation directory not found")

    # Remove desktop entry on Linux
    desktop_file = Path.home() / ".local" / "share" / "applications" / "voice-notes-system.desktop"
    if desktop_file.exists():
        desktop_file.unlink()
        print("✅ Removed desktop entry")

if __name__ == "__main__":
    main()
''')

        uninstaller_script.chmod(0o755)
        print("✅ Created uninstaller script")

    def run_post_install_setup(self):
        """Run post-installation setup."""
        print("🔧 Running post-installation setup...")

        python_exe = self.get_python_executable()
        setup_script = self.install_path / "setup_config.py"

        if setup_script.exists():
            print("Running configuration setup...")
            subprocess.run([
                str(python_exe), str(setup_script)
            ], cwd=self.install_path)
        else:
            print("⚠️  Setup script not found, skipping automatic configuration")

    def install(self):
        """Run complete installation process."""
        print("🎯 Starting Voice Notes System installation...")
        print(f"📍 Install path: {self.install_path}")

        try:
            # Check system requirements
            self.check_requirements()

            # Get latest version
            if not self.development:
                latest_version = self.get_latest_version()
                print(f"📋 Latest version: v{latest_version}")

                # Download and extract
                source_path = self.download_release(latest_version)
            else:
                # Use current directory for development
                source_path = Path.cwd()
                print("🔧 Using development mode (current directory)")

            # Installation steps
            self.create_virtual_environment()
            self.install_dependencies(source_path)
            self.copy_application_files(source_path)
            self.setup_configuration()
            self.create_launcher_scripts()
            self.create_desktop_entry()
            self.create_auto_updater()
            self.create_uninstaller()

            # Clean up temporary files
            if not self.development and source_path.parent.name.startswith("tmp"):
                shutil.rmtree(source_path.parent, ignore_errors=True)

            print("\n🎉 Installation completed successfully!")
            print(f"📁 Installed to: {self.install_path}")
            print(f"🚀 Run: {self.install_path}/scripts/voice-notes")
            print(f"⚙️  Configure: {self.install_path}/setup_config.py")

            # Run post-install setup
            if not self.development:
                self.run_post_install_setup()

        except Exception as e:
            print(f"\n❌ Installation failed: {e}")
            sys.exit(1)

def main():
    """Main entry point for installer."""
    parser = argparse.ArgumentParser(description="Voice Notes System Installer")
    parser.add_argument(
        "--install-path",
        help="Custom installation path"
    )
    parser.add_argument(
        "--force-update",
        action="store_true",
        help="Force update existing installation"
    )
    parser.add_argument(
        "--development",
        action="store_true",
        help="Install from current directory (development mode)"
    )

    args = parser.parse_args()

    installer = VoiceNotesInstaller(
        install_path=args.install_path,
        force_update=args.force_update,
        development=args.development
    )

    installer.install()

if __name__ == "__main__":
    main()