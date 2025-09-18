#!/usr/bin/env python3
"""
Test suite for the Vault Automation System
Validates setup, configuration, and basic functionality
"""

import json
import sys
import tempfile
import time
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_dir))

from config import get_config, validate_environment
from utils import health_check, setup_logging
from workflow_engine import WorkflowEngine
from claude_integration import AgentCoordinator


class AutomationTester:
    """Test suite for automation system"""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.config = None
        
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Vault Automation System Test Suite")
        print("=" * 50)
        
        # System tests
        self.test_python_environment()
        self.test_dependencies()
        self.test_configuration()
        self.test_vault_structure()
        
        # Component tests
        self.test_utilities()
        self.test_workflow_engine()
        self.test_claude_integration()
        
        # Integration tests
        self.test_file_monitoring()
        self.test_workflow_execution()
        
        # Print results
        self.print_results()
        
        return self.tests_failed == 0
    
    def test_python_environment(self):
        """Test Python environment"""
        print("\n🐍 Testing Python Environment...")
        
        # Python version
        if sys.version_info >= (3, 8):
            self.pass_test("Python version check")
        else:
            self.fail_test(f"Python version too old: {sys.version}")
        
        # Health check
        health = health_check()
        if health['status'] == 'healthy':
            self.pass_test("System health check")
        else:
            self.fail_test(f"Health check failed: {health}")
    
    def test_dependencies(self):
        """Test required dependencies"""
        print("\n📦 Testing Dependencies...")
        
        required_modules = [
            'watchdog', 'requests', 'yaml', 'schedule'
        ]
        
        for module in required_modules:
            try:
                __import__(module)
                self.pass_test(f"Import {module}")
            except ImportError:
                self.fail_test(f"Missing dependency: {module}")
    
    def test_configuration(self):
        """Test configuration"""
        print("\n⚙️ Testing Configuration...")
        
        try:
            self.config = get_config()
            self.pass_test("Configuration loading")
        except Exception as e:
            self.fail_test(f"Configuration error: {e}")
            return
        
        # Validate environment
        if validate_environment():
            self.pass_test("Environment validation")
        else:
            self.fail_test("Environment validation failed")
        
        # Check required settings
        if self.config.claude_api_key:
            self.pass_test("Claude API key configured")
        else:
            self.fail_test("Claude API key not configured")
        
        # Check vault path
        vault_path = Path(self.config.vault_path)
        if vault_path.exists():
            self.pass_test("Vault path exists")
        else:
            self.fail_test(f"Vault path not found: {vault_path}")
    
    def test_vault_structure(self):
        """Test vault structure"""
        print("\n📁 Testing Vault Structure...")
        
        if not self.config:
            self.fail_test("Configuration not loaded")
            return
        
        vault_path = Path(self.config.vault_path)
        
        # Check required directories
        required_dirs = [
            'agents',
            'workflows', 
            '1-raw-ideas',
            'training-data',
            'training-data/great-writing',
            'training-data/world-view'
        ]
        
        for dir_name in required_dirs:
            dir_path = vault_path / dir_name
            if dir_path.exists():
                self.pass_test(f"Directory exists: {dir_name}")
            else:
                self.fail_test(f"Missing directory: {dir_name}")
        
        # Check required agent files
        required_agents = [
            'orchestrator-agent.md',
            'analyzer-agent.md', 
            'connector-agent.md',
            'style-learner-agent.md',
            'draftsmith-agent.md'
        ]
        
        agents_dir = vault_path / 'agents'
        for agent_file in required_agents:
            if (agents_dir / agent_file).exists():
                self.pass_test(f"Agent file exists: {agent_file}")
            else:
                self.fail_test(f"Missing agent file: {agent_file}")
    
    def test_utilities(self):
        """Test utility functions"""
        print("\n🛠️ Testing Utilities...")
        
        from utils import safe_read_file, safe_write_file, load_state, save_state
        
        # Test file operations
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / 'test.txt'
            test_content = "Test content 123"
            
            # Write test
            if safe_write_file(test_file, test_content):
                self.pass_test("File write operation")
            else:
                self.fail_test("File write operation")
            
            # Read test
            read_content = safe_read_file(test_file)
            if read_content == test_content:
                self.pass_test("File read operation")
            else:
                self.fail_test("File read operation")
            
            # State management test
            test_state = {'test': True, 'value': 42}
            state_file = Path(temp_dir) / 'state.json'
            
            if save_state(state_file, test_state):
                self.pass_test("State save operation")
            else:
                self.fail_test("State save operation")
            
            loaded_state = load_state(state_file)
            if loaded_state.get('test') and loaded_state.get('value') == 42:
                self.pass_test("State load operation")
            else:
                self.fail_test("State load operation")
    
    def test_workflow_engine(self):
        """Test workflow engine"""
        print("\n⚙️ Testing Workflow Engine...")
        
        try:
            engine = WorkflowEngine()
            
            # Test engine creation
            self.pass_test("Workflow engine initialization")
            
            # Test status
            status = engine.get_status()
            if isinstance(status, dict) and 'processing' in status:
                self.pass_test("Workflow engine status")
            else:
                self.fail_test("Workflow engine status")
            
            # Test queue
            initial_size = engine.queue.size()
            workflow_id = engine.queue_workflow(
                workflow_type='test_workflow',
                trigger_event='test',
                priority='low'
            )
            
            if engine.queue.size() == initial_size + 1:
                self.pass_test("Workflow queuing")
            else:
                self.fail_test("Workflow queuing")
            
            # Stop engine
            engine.stop_processing()
            
        except Exception as e:
            self.fail_test(f"Workflow engine error: {e}")
    
    def test_claude_integration(self):
        """Test Claude API integration (without actual API call)"""
        print("\n🤖 Testing Claude Integration...")
        
        try:
            from claude_integration import ClaudeAPI, AgentCoordinator
            
            # Test API client creation
            api = ClaudeAPI()
            self.pass_test("Claude API client creation")
            
            # Test coordinator creation
            coordinator = AgentCoordinator()
            self.pass_test("Agent coordinator creation")
            
            # Test agent prompt loading
            if self.config:
                agent_path = self.config.get_agent_path('analyzer')
                if agent_path.exists():
                    prompt = api._load_agent_prompt('analyzer')
                    if prompt:
                        self.pass_test("Agent prompt loading")
                    else:
                        self.fail_test("Agent prompt loading")
                else:
                    self.fail_test("Analyzer agent file not found")
            
        except Exception as e:
            self.fail_test(f"Claude integration error: {e}")
    
    def test_file_monitoring(self):
        """Test file monitoring setup (without starting monitor)"""
        print("\n👁️ Testing File Monitoring...")
        
        try:
            from vault_monitor import VaultMonitor, VaultEventHandler
            from workflow_engine import WorkflowEngine
            
            # Test monitor creation (don't start it)
            engine = WorkflowEngine()
            monitor = VaultMonitor()
            
            self.pass_test("File monitor initialization")
            
            # Test event handler
            handler = VaultEventHandler(engine)
            
            # Test path validation
            test_path = '/test/1-raw-ideas/test.md'
            if hasattr(handler, '_determine_workflow'):
                workflow_type = handler._determine_workflow('1-raw-ideas/test.md')
                if workflow_type == 'analyze_new_content':
                    self.pass_test("File path workflow determination")
                else:
                    self.fail_test("File path workflow determination")
            
            engine.stop_processing()
            
        except Exception as e:
            self.fail_test(f"File monitoring error: {e}")
    
    def test_workflow_execution(self):
        """Test workflow execution (mock)"""
        print("\n🔄 Testing Workflow Execution...")
        
        try:
            engine = WorkflowEngine()
            
            # Test workflow queuing
            workflow_id = engine.queue_workflow(
                workflow_type='system_health_check',
                trigger_event='test',
                priority='high'
            )
            
            if workflow_id:
                self.pass_test("Workflow queuing with ID")
            else:
                self.fail_test("Workflow queuing with ID")
            
            # Test workflow status
            queue_status = engine.get_queue_status()
            if isinstance(queue_status, list):
                self.pass_test("Queue status retrieval")
            else:
                self.fail_test("Queue status retrieval")
            
            engine.stop_processing()
            
        except Exception as e:
            self.fail_test(f"Workflow execution test error: {e}")
    
    def pass_test(self, test_name):
        """Record a passing test"""
        print(f"  ✅ {test_name}")
        self.tests_passed += 1
    
    def fail_test(self, test_name):
        """Record a failing test"""
        print(f"  ❌ {test_name}")
        self.tests_failed += 1
    
    def print_results(self):
        """Print test results summary"""
        total_tests = self.tests_passed + self.tests_failed
        
        print("\n" + "=" * 50)
        print(f"📊 Test Results Summary")
        print(f"  Total tests: {total_tests}")
        print(f"  Passed: {self.tests_passed} ✅")
        print(f"  Failed: {self.tests_failed} ❌")
        
        if self.tests_failed == 0:
            print("\n🎉 All tests passed! System is ready for use.")
        else:
            print(f"\n⚠️ {self.tests_failed} test(s) failed. Please fix the issues above.")
        
        print("\n📋 Next steps:")
        if self.tests_failed == 0:
            print("  - Start the vault monitor: python run_monitor.py")
            print("  - Test with actual content: add files to 1-raw-ideas/")
            print("  - Try manual workflows: python -m src.workflow_engine --workflow system_health_check")
        else:
            print("  - Fix configuration issues")
            print("  - Run setup again: python setup_automation.py")
            print("  - Check .env file settings")


def main():
    """Main test function"""
    tester = AutomationTester()
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())