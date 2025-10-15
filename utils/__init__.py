"""
Utils package for Darwin Agent Framework

This package contains utility modules for the Darwin Agent system including
primitive file loading, configuration management, and helper functions.
"""

from .primitive_loader import (
    PrimitiveLoaderError,
    PrimitiveManager,
    load_instructions,
    load_chatmode,
    load_prompt,
    load_memory,
    load_primitive
)

__all__ = [
    'PrimitiveLoaderError',
    'PrimitiveManager', 
    'load_instructions',
    'load_chatmode',
    'load_prompt',
    'load_memory',
    'load_primitive'
]

__version__ = '1.0.0'
__author__ = 'Darwin Agent Framework'