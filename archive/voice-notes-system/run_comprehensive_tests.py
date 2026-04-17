#!/usr/bin/env python3
"""
Comprehensive test runner for Voice Notes System.

Runs all test suites and generates comprehensive reports including:
- Unit tests
- Integration tests
- Performance benchmarks
- User acceptance tests
- Coverage reports
"""

import subprocess
import sys
import time
import json
import os
from pathlib import Path
from datetime import datetime


class TestRunner:
    """Comprehensive test runner and reporter."""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = {}
        self.start_time = None
        self.total_time = 0

    def run_command(self, command, description, timeout=300):
        """Run a command and capture results."""
        print(f"\n🧪 {description}")
        print(f"Command: {' '.join(command)}")
        print("-" * 60)

        start_time = time.time()
        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            execution_time = time.time() - start_time

            success = result.returncode == 0

            self.test_results[description] = {
                'success': success,
                'execution_time': execution_time,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }

            if success:
                print(f"✅ {description} completed successfully ({execution_time:.2f}s)")
            else:
                print(f"❌ {description} failed ({execution_time:.2f}s)")
                print(f"Return code: {result.returncode}")
                if result.stderr:
                    print(f"Error output:\n{result.stderr}")

            # Show relevant output
            if result.stdout:
                lines = result.stdout.split('\n')
                # Show summary lines (usually at the end)
                summary_lines = [line for line in lines if any(word in line.lower()
                    for word in ['passed', 'failed', 'error', 'warning', 'collected', 'seconds'])]
                if summary_lines:
                    print("\nSummary:")
                    for line in summary_lines[-5:]:  # Last 5 relevant lines
                        print(f"  {line}")

            return success

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            print(f"⏰ {description} timed out after {timeout}s")
            self.test_results[description] = {
                'success': False,
                'execution_time': execution_time,
                'stdout': '',
                'stderr': f'Timed out after {timeout}s',
                'return_code': -1
            }
            return False

        except Exception as e:
            execution_time = time.time() - start_time
            print(f"💥 {description} crashed: {e}")
            self.test_results[description] = {
                'success': False,
                'execution_time': execution_time,
                'stdout': '',
                'stderr': str(e),
                'return_code': -2
            }
            return False

    def run_unit_tests(self):
        """Run all unit tests."""
        command = [
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "--maxfail=5"
        ]
        return self.run_command(command, "Unit Tests", timeout=120)

    def run_integration_tests(self):
        """Run integration tests."""
        command = [
            sys.executable, "-m", "pytest",
            "tests/test_integration_pipeline.py",
            "-v",
            "--tb=short"
        ]
        return self.run_command(command, "Integration Tests", timeout=180)

    def run_performance_tests(self):
        """Run performance benchmarks (excluding slow tests)."""
        command = [
            sys.executable, "-m", "pytest",
            "tests/test_performance_benchmarks.py",
            "-v",
            "-m", "not slow",
            "--tb=short"
        ]
        return self.run_command(command, "Performance Tests", timeout=240)

    def run_user_acceptance_tests(self):
        """Run user acceptance tests."""
        command = [
            sys.executable, "-m", "pytest",
            "tests/test_user_acceptance.py",
            "-v",
            "--tb=short"
        ]
        return self.run_command(command, "User Acceptance Tests", timeout=180)

    def run_coverage_analysis(self):
        """Run tests with coverage analysis."""
        # First, install coverage if not available
        try:
            import coverage
        except ImportError:
            print("\n📦 Installing coverage package...")
            subprocess.run([sys.executable, "-m", "pip", "install", "coverage"],
                         cwd=self.project_root, check=False)

        # Run tests with coverage
        command = [
            sys.executable, "-m", "pytest",
            "tests/",
            "--cov=src/",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--tb=short",
            "--maxfail=10"
        ]
        return self.run_command(command, "Coverage Analysis", timeout=300)

    def run_code_quality_checks(self):
        """Run code quality checks."""
        # Check if flake8 is available
        try:
            command = [
                sys.executable, "-m", "flake8",
                "src/",
                "--max-line-length=120",
                "--ignore=E203,W503"
            ]
            return self.run_command(command, "Code Quality (flake8)", timeout=60)
        except FileNotFoundError:
            print("⚠️  flake8 not available, skipping code quality checks")
            return True

    def run_type_checking(self):
        """Run type checking with mypy if available."""
        try:
            command = [
                sys.executable, "-m", "mypy",
                "src/",
                "--ignore-missing-imports"
            ]
            return self.run_command(command, "Type Checking (mypy)", timeout=120)
        except FileNotFoundError:
            print("⚠️  mypy not available, skipping type checking")
            return True

    def run_security_checks(self):
        """Run security checks with bandit if available."""
        try:
            command = [
                sys.executable, "-m", "bandit",
                "-r", "src/",
                "-f", "txt"
            ]
            return self.run_command(command, "Security Analysis (bandit)", timeout=60)
        except FileNotFoundError:
            print("⚠️  bandit not available, skipping security checks")
            return True

    def generate_report(self):
        """Generate comprehensive test report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_execution_time': self.total_time,
            'summary': {
                'total_suites': len(self.test_results),
                'passed': sum(1 for result in self.test_results.values() if result['success']),
                'failed': sum(1 for result in self.test_results.values() if not result['success'])
            },
            'results': self.test_results
        }

        # Save JSON report
        report_file = self.project_root / 'test_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        # Print summary
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 80)
        print(f"Timestamp: {report['timestamp']}")
        print(f"Total execution time: {report['total_execution_time']:.2f}s")
        print(f"Test suites run: {report['summary']['total_suites']}")
        print(f"Passed: {report['summary']['passed']}")
        print(f"Failed: {report['summary']['failed']}")
        print()

        # Detailed results
        print("Detailed Results:")
        print("-" * 40)
        for suite_name, result in self.test_results.items():
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status} {suite_name} ({result['execution_time']:.2f}s)")

        print()

        # Recommendations
        failed_suites = [name for name, result in self.test_results.items() if not result['success']]
        if failed_suites:
            print("🔧 Recommendations:")
            print("-" * 20)
            for suite in failed_suites:
                result = self.test_results[suite]
                print(f"• Fix issues in {suite}")
                if result['stderr']:
                    # Extract key error messages
                    lines = result['stderr'].split('\n')
                    error_lines = [line for line in lines if 'error' in line.lower() or 'failed' in line.lower()]
                    for error_line in error_lines[:3]:  # Show first 3 errors
                        print(f"  - {error_line.strip()}")
        else:
            print("🎉 All test suites passed! The system is ready for deployment.")

        print(f"\nFull report saved to: {report_file}")

        # Coverage report location
        coverage_dir = self.project_root / 'htmlcov'
        if coverage_dir.exists():
            print(f"Coverage report: {coverage_dir / 'index.html'}")

        return report

    def run_all_tests(self):
        """Run all test suites."""
        print("🚀 Starting Comprehensive Test Suite for Voice Notes System")
        print("=" * 80)

        self.start_time = time.time()

        # Test suites in order of importance/dependency
        test_suites = [
            self.run_unit_tests,
            self.run_integration_tests,
            self.run_user_acceptance_tests,
            self.run_performance_tests,
            self.run_coverage_analysis,
            self.run_code_quality_checks,
            self.run_type_checking,
            self.run_security_checks
        ]

        # Run all test suites
        for test_suite in test_suites:
            success = test_suite()
            time.sleep(1)  # Brief pause between suites

        self.total_time = time.time() - self.start_time

        # Generate final report
        return self.generate_report()


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        runner = TestRunner()

        if test_type == "unit":
            runner.run_unit_tests()
        elif test_type == "integration":
            runner.run_integration_tests()
        elif test_type == "performance":
            runner.run_performance_tests()
        elif test_type == "acceptance":
            runner.run_user_acceptance_tests()
        elif test_type == "coverage":
            runner.run_coverage_analysis()
        elif test_type == "quality":
            runner.run_code_quality_checks()
        else:
            print(f"Unknown test type: {test_type}")
            print("Available types: unit, integration, performance, acceptance, coverage, quality")
            return 1
    else:
        # Run all tests
        runner = TestRunner()
        report = runner.run_all_tests()

        # Return appropriate exit code
        return 0 if report['summary']['failed'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())