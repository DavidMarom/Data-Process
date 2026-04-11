import sys
from pathlib import Path

# Add root to python path (For data loading to work properly)
sys.path.insert(0, str(Path(__file__).parent))

from src.manager import run

run()

