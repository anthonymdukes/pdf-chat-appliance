"""
Pytest configuration for PDF Chat Appliance tests.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add memory package to path
memory_path = project_root / "memory"
if memory_path.exists():
    sys.path.insert(0, str(memory_path))
