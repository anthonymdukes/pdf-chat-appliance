#!/usr/bin/env python3
"""
Test script for the automated documentation generation system.
"""

import sys
import subprocess
from pathlib import Path

def test_documentation_generator():
    """Test the documentation generation script."""
    print("🧪 Testing automated documentation generation...")
    
    # Test script path
    script_path = Path("scripts/generate_docs.py")
    
    if not script_path.exists():
        print("❌ Documentation generator script not found!")
        return False
    
    try:
        # Test script execution
        print("🚀 Running documentation generator...")
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Documentation generator executed successfully!")
            print("📝 Output:")
            print(result.stdout)
            
            # Check generated files
            docs_dir = Path("docs")
            if docs_dir.exists():
                generated_files = list(docs_dir.glob("*.md"))
                api_files = list((docs_dir / "api").glob("*.md")) if (docs_dir / "api").exists() else []
                
                print(f"📁 Generated {len(generated_files)} main documentation files")
                print(f"🔌 Generated {len(api_files)} API documentation files")
                
                # List generated files
                for file in generated_files:
                    print(f"   - {file.name}")
                for file in api_files:
                    print(f"   - api/{file.name}")
                
                return True
            else:
                print("❌ Documentation directory not created!")
                return False
        else:
            print("❌ Documentation generator failed!")
            print("Error output:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Documentation generator timed out!")
        return False
    except Exception as e:
        print(f"❌ Error testing documentation generator: {e}")
        return False

def test_documentation_quality():
    """Test the quality of generated documentation."""
    print("\n🔍 Testing documentation quality...")
    
    docs_dir = Path("docs")
    if not docs_dir.exists():
        print("❌ No documentation directory found!")
        return False
    
    # Check for required files
    required_files = [
        "CHANGELOG.md",
        "HEALTH_REPORT.md", 
        "INDEX.md",
        "README_UPDATES.md"
    ]
    
    api_required_files = [
        "generated_api.md"
    ]
    
    missing_files = []
    
    # Check main documentation
    for file in required_files:
        if not (docs_dir / file).exists():
            missing_files.append(file)
    
    # Check API documentation
    api_dir = docs_dir / "api"
    if api_dir.exists():
        for file in api_required_files:
            if not (api_dir / file).exists():
                missing_files.append(f"api/{file}")
    else:
        missing_files.extend([f"api/{file}" for file in api_required_files])
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    else:
        print("✅ All required documentation files present!")
    
    # Check file content quality
    quality_issues = []
    
    for file in docs_dir.glob("*.md"):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for basic content
                if len(content.strip()) < 100:
                    quality_issues.append(f"{file.name}: Too short")
                
                # Check for timestamp
                if "Generated:" not in content:
                    quality_issues.append(f"{file.name}: Missing generation timestamp")
                    
        except Exception as e:
            quality_issues.append(f"{file.name}: Error reading file - {e}")
    
    if quality_issues:
        print("⚠️ Quality issues found:")
        for issue in quality_issues:
            print(f"   - {issue}")
        return False
    else:
        print("✅ Documentation quality checks passed!")
        return True

def main():
    """Main test function."""
    print("🧪 DOCUMENTATION GENERATOR TEST SUITE")
    print("=" * 50)
    
    # Test 1: Basic functionality
    test1_passed = test_documentation_generator()
    
    # Test 2: Quality checks
    test2_passed = test_documentation_quality()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 30)
    print(f"Documentation Generation: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Quality Checks: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Documentation automation system is working correctly!")
        return True
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("Please check the documentation generator implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 