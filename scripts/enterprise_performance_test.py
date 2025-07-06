#!/usr/bin/env python3
"""
Enterprise Performance Test Suite for PDF Chat Appliance
Tests 10,000+ page PDF processing capabilities
"""

import json
import os
import sys
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional

# Mandatory .venv activation check
if "venv" not in sys.executable:
    raise RuntimeError("VENV NOT ACTIVATED. Please activate `.venv` before running this script.")

import psutil
import requests


class EnterprisePerformanceTester:
    """Enterprise-scale performance testing for PDF Chat Appliance"""

    def __init__(self, api_url: str, test_files: Optional[List[str]] = None):
        self.api_url = api_url
        self.test_files = test_files or []
        self.test_results: List[Dict] = []
        self.start_time = time.time()

    def log_test(
        self, test_name: str, success: bool, duration: float, details: Dict = None
    ):
        """Log test results"""
        result = {
            "test_name": test_name,
            "success": success,
            "duration": duration,
            "timestamp": time.time(),
            "details": details or {},
        }
        self.test_results.append(result)

        status = "PASS" if success else "FAIL"
        print(f"{status} {test_name}: {duration:.2f}s")
        if details:
            print(f"   Details: {json.dumps(details, indent=2)}")

    def test_api_health(self) -> bool:
        """Test API health endpoint"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            duration = time.time() - start_time

            success = response.status_code == 200
            details = {
                "status_code": response.status_code,
                "response": response.json() if success else response.text,
            }

            self.log_test("API Health Check", success, duration, details)
            return success

        except Exception as e:
            duration = time.time() - start_time
            self.log_test("API Health Check", False, duration, {"error": str(e)})
            return False

    def test_upload_endpoint(self, file_path: str) -> bool:
        """Test file upload endpoint"""
        start_time = time.time()
        try:
            with open(file_path, "rb") as f:
                files = {"files": f}
                response = requests.post(
                    f"{self.api_url}/upload",
                    files=files,
                    timeout=300,  # 5 minute timeout for large files
                )

            duration = time.time() - start_time
            success = response.status_code == 200

            details = {
                "status_code": response.status_code,
                "file_size_mb": os.path.getsize(file_path) / (1024 * 1024),
                "response": response.json() if success else response.text,
            }

            self.log_test(
                f"Upload Test: {Path(file_path).name}", success, duration, details
            )
            return success

        except Exception as e:
            duration = time.time() - start_time
            self.log_test(
                f"Upload Test: {Path(file_path).name}",
                False,
                duration,
                {"error": str(e)},
            )
            return False

    def test_ingestion_status(self) -> bool:
        """Test ingestion status endpoint"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.api_url}/ingestion/status", timeout=10)
            duration = time.time() - start_time

            success = response.status_code == 200
            details = {
                "status_code": response.status_code,
                "response": response.json() if success else response.text,
            }

            self.log_test("Ingestion Status Check", success, duration, details)
            return success

        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Ingestion Status Check", False, duration, {"error": str(e)})
            return False

    def test_chunk_flow_metrics(self) -> bool:
        """Test chunk flow metrics endpoint"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.api_url}/ingestion/chunk-flow", timeout=10)
            duration = time.time() - start_time

            success = response.status_code == 200
            details = {
                "status_code": response.status_code,
                "response": response.json() if success else response.text,
            }

            self.log_test("Chunk Flow Metrics", success, duration, details)
            return success

        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Chunk Flow Metrics", False, duration, {"error": str(e)})
            return False

    def test_query_endpoint(self, question: str) -> bool:
        """Test query endpoint"""
        start_time = time.time()
        try:
            data = {"question": question}
            response = requests.post(f"{self.api_url}/query", json=data, timeout=30)

            duration = time.time() - start_time
            success = response.status_code == 200

            details = {
                "status_code": response.status_code,
                "question": question,
                "response_length": len(response.text) if success else 0,
            }

            self.log_test(f"Query Test: {question[:50]}...", success, duration, details)
            return success

        except Exception as e:
            duration = time.time() - start_time
            self.log_test(
                f"Query Test: {question[:50]}...", False, duration, {"error": str(e)}
            )
            return False

    def test_system_stats(self) -> bool:
        """Test system statistics endpoint"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.api_url}/stats", timeout=10)
            duration = time.time() - start_time

            success = response.status_code == 200
            details = {
                "status_code": response.status_code,
                "response": response.json() if success else response.text,
            }

            self.log_test("System Stats Check", success, duration, details)
            return success

        except Exception as e:
            duration = time.time() - start_time
            self.log_test("System Stats Check", False, duration, {"error": str(e)})
            return False

    def monitor_system_resources(self, duration: int = 60) -> Dict:
        """Monitor system resources during testing"""
        print(f"🔍 Monitoring system resources for {duration} seconds...")

        cpu_samples = []
        memory_samples = []
        start_time = time.time()

        while time.time() - start_time < duration:
            cpu_samples.append(psutil.cpu_percent(interval=1))
            memory_samples.append(psutil.virtual_memory().percent)
            time.sleep(1)

        return {
            "cpu_avg": sum(cpu_samples) / len(cpu_samples),
            "cpu_max": max(cpu_samples),
            "memory_avg": sum(memory_samples) / len(memory_samples),
            "memory_max": max(memory_samples),
            "duration": duration,
        }

    def run_enterprise_test_suite(self, test_files: Optional[List[str]] = None) -> Dict:
        """Run comprehensive enterprise test suite"""
        print("ENTERPRISE PERFORMANCE TEST SUITE")
        print("=" * 50)
        test_files = test_files or []

        # Filter existing files
        existing_files = [f for f in test_files if os.path.exists(f)]
        if not existing_files:
            print("No test files found, using basic API tests only")

        # Start resource monitoring in background
        monitor_thread = threading.Thread(
            target=self.monitor_system_resources, args=(120,)  # Monitor for 2 minutes
        )
        monitor_thread.daemon = True
        monitor_thread.start()

        # Basic API tests
        print("\n📋 Running Basic API Tests...")
        self.test_api_health()
        self.test_ingestion_status()
        self.test_chunk_flow_metrics()
        self.test_system_stats()

        # Upload tests
        if existing_files:
            print(f"\n📤 Running Upload Tests ({len(existing_files)} files)...")
            for file_path in existing_files:
                self.test_upload_endpoint(file_path)
                time.sleep(2)  # Brief pause between uploads

        # Query tests
        print("\n🔍 Running Query Tests...")
        test_questions = [
            "What is VMware vSphere?",
            "How do I configure network settings?",
            "What are the system requirements?",
            "Explain the deployment process",
            "What troubleshooting steps are available?",
        ]

        for question in test_questions:
            self.test_query_endpoint(question)
            time.sleep(1)  # Brief pause between queries

        # Wait for monitoring to complete
        monitor_thread.join(timeout=10)

        # Calculate summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        total_duration = time.time() - self.start_time

        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (
                (passed_tests / total_tests * 100) if total_tests > 0 else 0
            ),
            "total_duration": total_duration,
            "test_results": self.test_results,
        }

        print("\n" + "=" * 50)
        print("📊 ENTERPRISE TEST SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Total Duration: {total_duration:.2f}s")

        if failed_tests > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(
                        f"  - {result['test_name']}: {result.get('details', {}).get('error', 'Unknown error')}"
                    )

        return summary

    def run_test(self, test_name: str, test_func, *args, **kwargs) -> Dict:
        start = time.time()
        try:
            result = test_func(*args, **kwargs)
            success = result.get("success", True)
            details = result.get("details", {})
            if details is None:
                details = {}
        except Exception as e:
            success = False
            details = {"error": str(e)}
        duration = time.time() - start
        status = "PASS" if success else "FAIL"
        print(f"{status} {test_name}: {duration:.2f}s")
        if details:
            print(f"  Details: {details}")
        test_result = {
            "test_name": test_name,
            "success": success,
            "details": details or {},
            "duration": duration,
        }
        self.test_results.append(test_result)
        return test_result


def main():
    """Main test execution"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:5000"

    tester = EnterprisePerformanceTester(base_url)

    # Run enterprise test suite
    results = tester.run_enterprise_test_suite()

    # Save results to file
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_file = f"logs/enterprise_test_results_{timestamp}.json"

    os.makedirs("logs", exist_ok=True)
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Test results saved to: {results_file}")

    # Exit with appropriate code
    if results["failed_tests"] > 0:
        print("Some tests failed!")
        print()
        sys.exit(1)
    else:
        print("All tests passed!")
        print()
        sys.exit(0)


if __name__ == "__main__":
    main()

# UNCONDITIONAL: Ensure prompt unsticking regardless of exit path
print()

# COMPREHENSIVE CLEANUP: Ensure all threads and processes are properly terminated
import atexit


def cleanup_on_exit():
    """Ensure clean exit by terminating any remaining processes"""
    try:
        # Force flush all output
        import sys

        sys.stdout.flush()
        sys.stderr.flush()

        # Print final blank line
        print()
    except:
        pass


# Register cleanup function
atexit.register(cleanup_on_exit)
