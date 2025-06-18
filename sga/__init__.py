import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import create_app
    
except ImportError:
    def create_app():
        raise RuntimeError("create_app function not available")

__version__ = "2.0.0"
__author__ = "SGA Team"
