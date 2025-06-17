# filepath: sga/__init__.py
"""
SGA (Sistema de Gestión Académica) Package
"""

# Re-export create_app from the root app module
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import create_app
except ImportError:
    # Fallback if app.py is not available
    def create_app():
        raise RuntimeError("create_app function not available")

__version__ = "2.0.0"
__author__ = "SGA Team"
