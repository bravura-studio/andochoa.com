#!/usr/bin/env python3
"""
Voice Notes System - Version Management

Handles version tracking, update checking, and release management.
"""

import os
import json
import sys
import subprocess
import re
from pathlib import Path
from datetime import datetime
from urllib.request import urlopen
from urllib.error import URLError
from typing import Optional, Dict, Any

class VersionManager:
    """Manages application versioning and updates."""

    def __init__(self, install_path: Optional[Path] = None):
        """Initialize version manager."""
        self.install_path = install_path or Path.cwd()
        self.version_file = self.install_path / "VERSION"
        self.config_dir = self.install_path / "config"

        # Repository information
        self.repo_url = "https://github.com/your-org/voice-notes-system"
        self.api_url = "https://api.github.com/repos/your-org/voice-notes-system"

    def get_current_version(self) -> str:
        """Get current installed version."""
        # Try version file first
        if self.version_file.exists():
            return self.version_file.read_text().strip()

        # Try package version
        try:
            import voice_notes_system
            return getattr(voice_notes_system, "__version__", "unknown")
        except ImportError:
            pass

        # Try git tag if in development
        try:
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                capture_output=True,
                text=True,
                cwd=self.install_path
            )
            if result.returncode == 0:
                return result.stdout.strip().lstrip("v")
        except FileNotFoundError:
            pass

        return "1.0.0"  # Default version

    def get_latest_version(self) -> Optional[str]:
        """Get latest version from GitHub releases."""
        try:
            releases_url = f"{self.api_url}/releases/latest"
            with urlopen(releases_url, timeout=10) as response:
                data = json.loads(response.read().decode())
                return data["tag_name"].lstrip("v")
        except (URLError, KeyError, json.JSONDecodeError, OSError):
            return None

    def check_for_updates(self) -> Dict[str, Any]:
        """Check if updates are available."""
        current = self.get_current_version()
        latest = self.get_latest_version()

        result = {
            "current_version": current,
            "latest_version": latest,
            "update_available": False,
            "update_info": None
        }

        if latest:
            # Compare versions
            if self._compare_versions(latest, current) > 0:
                result["update_available"] = True
                result["update_info"] = self._get_release_info(latest)

        return result

    def _compare_versions(self, version1: str, version2: str) -> int:
        """Compare two version strings. Returns 1 if v1 > v2, -1 if v1 < v2, 0 if equal."""
        def normalize_version(v):
            # Convert version string to tuple of integers
            return tuple(map(int, re.findall(r'\d+', v)))

        v1_parts = normalize_version(version1)
        v2_parts = normalize_version(version2)

        # Pad shorter version with zeros
        max_len = max(len(v1_parts), len(v2_parts))
        v1_parts += (0,) * (max_len - len(v1_parts))
        v2_parts += (0,) * (max_len - len(v2_parts))

        if v1_parts > v2_parts:
            return 1
        elif v1_parts < v2_parts:
            return -1
        else:
            return 0

    def _get_release_info(self, version: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific release."""
        try:
            releases_url = f"{self.api_url}/releases/tags/v{version}"
            with urlopen(releases_url, timeout=10) as response:
                data = json.loads(response.read().decode())
                return {
                    "version": version,
                    "name": data.get("name", f"Version {version}"),
                    "body": data.get("body", ""),
                    "published_at": data.get("published_at", ""),
                    "download_url": data.get("zipball_url", ""),
                    "prerelease": data.get("prerelease", False),
                    "draft": data.get("draft", False)
                }
        except (URLError, KeyError, json.JSONDecodeError, OSError):
            return None

    def save_version_info(self, version: str) -> None:
        """Save version information to file."""
        self.version_file.write_text(version)

        # Also save extended version info
        version_info = {
            "version": version,
            "install_date": datetime.now().isoformat(),
            "install_path": str(self.install_path),
            "python_version": sys.version,
            "platform": sys.platform
        }

        version_info_file = self.config_dir / "version_info.json"
        self.config_dir.mkdir(exist_ok=True)

        with open(version_info_file, "w") as f:
            json.dump(version_info, f, indent=2)

    def get_version_history(self) -> list:
        """Get list of available versions from GitHub."""
        try:
            releases_url = f"{self.api_url}/releases"
            with urlopen(releases_url, timeout=10) as response:
                data = json.loads(response.read().decode())

                versions = []
                for release in data:
                    if not release.get("draft", False):
                        versions.append({
                            "version": release["tag_name"].lstrip("v"),
                            "name": release.get("name", ""),
                            "published_at": release.get("published_at", ""),
                            "prerelease": release.get("prerelease", False)
                        })

                return versions
        except (URLError, KeyError, json.JSONDecodeError, OSError):
            return []

    def create_update_notification(self, update_info: Dict[str, Any]) -> str:
        """Create formatted update notification."""
        current = update_info["current_version"]
        latest = update_info["latest_version"]

        message = f"""
🔄 Voice Notes System Update Available!

Current Version: {current}
Latest Version:  {latest}

"""

        if update_info.get("update_info"):
            release_info = update_info["update_info"]
            message += f"Release: {release_info.get('name', f'Version {latest}')}\n"

            # Add changelog excerpt
            body = release_info.get("body", "")
            if body:
                # Extract first few lines of changelog
                lines = body.split('\n')[:5]
                message += f"\nChanges:\n" + '\n'.join(f"  {line}" for line in lines if line.strip())
                if len(body.split('\n')) > 5:
                    message += "\n  ..."

        message += f"\n\nTo update, run: python scripts/install.py --force-update"
        message += f"\nView full changelog: {self.repo_url}/releases/tag/v{latest}"

        return message

    def should_check_for_updates(self) -> bool:
        """Determine if it's time to check for updates based on configuration."""
        config_file = self.config_dir / "config.yaml"
        if not config_file.exists():
            return True  # Default to checking

        try:
            import yaml
            with open(config_file) as f:
                config = yaml.safe_load(f)

            update_config = config.get("updates", {})

            # Check if updates are disabled
            if not update_config.get("enabled", True):
                return False

            # Check frequency
            frequency = update_config.get("check_frequency", "daily")
            last_check_file = self.config_dir / ".last_update_check"

            if not last_check_file.exists():
                return True

            try:
                last_check = datetime.fromisoformat(last_check_file.read_text().strip())
                now = datetime.now()

                if frequency == "daily":
                    return (now - last_check).days >= 1
                elif frequency == "weekly":
                    return (now - last_check).days >= 7
                elif frequency == "monthly":
                    return (now - last_check).days >= 30
                else:  # "never"
                    return False

            except (ValueError, OSError):
                return True

        except (ImportError, yaml.YAMLError, OSError):
            return True

    def record_update_check(self) -> None:
        """Record that an update check was performed."""
        last_check_file = self.config_dir / ".last_update_check"
        self.config_dir.mkdir(exist_ok=True)
        last_check_file.write_text(datetime.now().isoformat())

    def get_changelog_since_version(self, since_version: str) -> str:
        """Get changelog entries since a specific version."""
        try:
            releases_url = f"{self.api_url}/releases"
            with urlopen(releases_url, timeout=10) as response:
                data = json.loads(response.read().decode())

                changelog = []
                for release in data:
                    version = release["tag_name"].lstrip("v")

                    # Stop when we reach the "since" version
                    if self._compare_versions(version, since_version) <= 0:
                        break

                    if not release.get("draft", False):
                        changelog.append({
                            "version": version,
                            "name": release.get("name", f"Version {version}"),
                            "body": release.get("body", ""),
                            "published_at": release.get("published_at", "")
                        })

                # Format changelog
                formatted_changelog = []
                for entry in changelog:
                    formatted_changelog.append(f"## {entry['name']}")
                    if entry["body"]:
                        formatted_changelog.append(entry["body"])
                    formatted_changelog.append("")

                return "\n".join(formatted_changelog)

        except (URLError, KeyError, json.JSONDecodeError, OSError):
            return "Unable to fetch changelog."

def main():
    """Command-line interface for version management."""
    import argparse

    parser = argparse.ArgumentParser(description="Voice Notes System Version Manager")
    parser.add_argument("--current", action="store_true", help="Show current version")
    parser.add_argument("--latest", action="store_true", help="Show latest available version")
    parser.add_argument("--check", action="store_true", help="Check for updates")
    parser.add_argument("--history", action="store_true", help="Show version history")
    parser.add_argument("--changelog", metavar="VERSION", help="Show changelog since version")
    parser.add_argument("--install-path", help="Installation path")

    args = parser.parse_args()

    vm = VersionManager(Path(args.install_path) if args.install_path else None)

    if args.current:
        print(f"Current version: {vm.get_current_version()}")

    elif args.latest:
        latest = vm.get_latest_version()
        if latest:
            print(f"Latest version: {latest}")
        else:
            print("Unable to fetch latest version")

    elif args.check:
        update_info = vm.check_for_updates()
        if update_info["update_available"]:
            print(vm.create_update_notification(update_info))
        else:
            print(f"You have the latest version ({update_info['current_version']})")

    elif args.history:
        versions = vm.get_version_history()
        if versions:
            print("Available versions:")
            for version in versions[:10]:  # Show last 10 versions
                status = " (pre-release)" if version["prerelease"] else ""
                print(f"  {version['version']}{status} - {version['name']}")
        else:
            print("Unable to fetch version history")

    elif args.changelog:
        changelog = vm.get_changelog_since_version(args.changelog)
        print(f"Changelog since version {args.changelog}:")
        print(changelog)

    else:
        # Default: show current and check for updates
        current = vm.get_current_version()
        print(f"Current version: {current}")

        if vm.should_check_for_updates():
            update_info = vm.check_for_updates()
            if update_info["update_available"]:
                print(vm.create_update_notification(update_info))
            vm.record_update_check()

if __name__ == "__main__":
    main()