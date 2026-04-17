#!/usr/bin/env python3
"""
Configuration Validation Script

Validates that all configuration files and settings are properly set up.
"""

import sys
import asyncio
from pathlib import Path


def validate_file_structure():
    """Validate that all required files and directories exist."""
    print("=== Validating File Structure ===")

    required_files = [
        "config/config.yaml",
        "config/prompts.yaml",
        ".env.template",
        "src/config_manager.py",
        "src/mcp_client.py",
        "requirements.txt"
    ]

    required_dirs = [
        "src",
        "config",
        "tests",
        "logs",
        "temp_audio"
    ]

    all_valid = True

    # Check files
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")
            all_valid = False

    # Check directories
    for dir_path in required_dirs:
        if Path(dir_path).is_dir():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ - Missing")
            all_valid = False

    return all_valid


def validate_configuration():
    """Validate configuration settings."""
    print("\n=== Validating Configuration ===")

    try:
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from config_manager import ConfigManager

        config = ConfigManager()
        validation_results = config.validate_configuration()

        all_valid = True
        for item, is_valid in validation_results.items():
            status = "✅" if is_valid else "❌"
            print(f"{status} {item}")
            if not is_valid:
                all_valid = False

        return all_valid

    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return False


async def test_api_connections():
    """Test API connections."""
    print("\n=== Testing API Connections ===")

    try:
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from config_manager import ConfigManager
        from mcp_client import MCPClient, MockMCPClient
        import openai

        config = ConfigManager()
        all_connected = True

        # Test OpenAI connection
        try:
            openai_config = config.get_openai_config()
            client = openai.OpenAI(api_key=openai_config['api_key'])

            # Test with models list (lightweight)
            models = client.models.list()
            print("✅ OpenAI API connection successful")

            # Check Whisper availability
            whisper_available = any(model.id == "whisper-1" for model in models.data)
            if whisper_available:
                print("✅ Whisper-1 model available")
            else:
                print("⚠️  Whisper-1 model not found")

        except Exception as e:
            print(f"❌ OpenAI API connection failed: {e}")
            all_connected = False

        # Test MCP connection
        try:
            mcp_config = config.get_mcp_config()

            if not mcp_config.get('server_url'):
                print("⚠️  MCP server URL not configured - using mock client for testing")
                mcp_client = MockMCPClient()
            else:
                mcp_client = MCPClient(
                    server_url=mcp_config['server_url'],
                    api_key=mcp_config.get('api_key'),
                    timeout=mcp_config.get('timeout', 30)
                )

            async with mcp_client:
                if await mcp_client.health_check():
                    print("✅ MCP server connection successful")

                    # Get server info
                    server_info = await mcp_client.get_server_info()
                    server_name = server_info.get('name', 'Unknown')
                    print(f"✅ MCP server: {server_name}")
                else:
                    print("❌ MCP server health check failed")
                    all_connected = False

        except Exception as e:
            print(f"❌ MCP connection failed: {e}")
            all_connected = False

        return all_connected

    except Exception as e:
        print(f"❌ Error testing connections: {e}")
        return False


def check_dependencies():
    """Check that all required Python packages are installed."""
    print("\n=== Checking Dependencies ===")

    # Package name mappings for import vs pip name differences
    required_packages = {
        'openai': 'openai',
        'aiohttp': 'aiohttp',
        'pynput': 'pynput',
        'pystray': 'pystray',
        'sounddevice': 'sounddevice',
        'soundfile': 'soundfile',
        'numpy': 'numpy',
        'PyYAML': 'yaml',
        'python-dotenv': 'dotenv',
        'Pillow': 'PIL',
        'plyer': 'plyer',
        'SpeechRecognition': 'speech_recognition'
    }

    all_installed = True

    for pip_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {pip_name}")
        except ImportError:
            print(f"❌ {pip_name} - Not installed")
            all_installed = False

    return all_installed


def generate_report():
    """Generate a comprehensive validation report."""
    print("\n" + "=" * 60)
    print("VOICE NOTES SYSTEM - CONFIGURATION VALIDATION REPORT")
    print("=" * 60)

    # Run all validations
    file_structure_ok = validate_file_structure()
    dependencies_ok = check_dependencies()
    config_ok = validate_configuration()

    # Test connections
    try:
        connections_ok = asyncio.run(test_api_connections())
    except Exception as e:
        print(f"Error testing connections: {e}")
        connections_ok = False

    # Summary
    print("\n=== SUMMARY ===")

    results = {
        "File Structure": file_structure_ok,
        "Dependencies": dependencies_ok,
        "Configuration": config_ok,
        "API Connections": connections_ok
    }

    all_passed = True
    for category, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{category}: {status}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n🎉 All validations passed! System is ready to use.")
        return 0
    else:
        print("\n⚠️  Some validations failed. Please review the results above.")
        print("\nNext steps:")

        if not file_structure_ok:
            print("- Run the project setup to create missing files/directories")

        if not dependencies_ok:
            print("- Install missing dependencies: pip install -r requirements.txt")

        if not config_ok:
            print("- Run setup_config.py to configure API keys and settings")

        if not connections_ok:
            print("- Check your API keys and network connectivity")

        return 1


def main():
    """Main validation function."""
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("Voice Notes System Configuration Validator")
        print("Usage: python validate_config.py")
        print("       python validate_config.py --help")
        return 0

    return generate_report()


if __name__ == "__main__":
    sys.exit(main())