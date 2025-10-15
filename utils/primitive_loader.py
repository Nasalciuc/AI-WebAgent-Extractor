"""
Agentic Primitive Loader - File parsing utilities for Darwin Agent Framework

This module provides utilities for loading and parsing agentic primitive files
including instructions, chat modes, prompts, and memory files with YAML frontmatter.

Author: Darwin Agent Framework
Date: October 15, 2025
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Union

import yaml


class PrimitiveLoaderError(Exception):
    """Custom exception for primitive loading errors."""
    pass


def _parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """
    Parse YAML frontmatter from markdown content.
    
    Args:
        content: Raw file content potentially containing YAML frontmatter
        
    Returns:
        Tuple of (metadata_dict, markdown_content)
        
    Raises:
        PrimitiveLoaderError: If YAML parsing fails
    """
    # Check for YAML frontmatter delimiters
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(frontmatter_pattern, content, re.DOTALL)
    
    if not match:
        # No frontmatter found, return empty metadata and full content
        return {}, content.strip()
    
    yaml_content, markdown_content = match.groups()
    
    try:
        # Parse YAML frontmatter
        metadata = yaml.safe_load(yaml_content) or {}
        return metadata, markdown_content.strip()
    except yaml.YAMLError as e:
        raise PrimitiveLoaderError(f"Failed to parse YAML frontmatter: {e}")


def _load_file_content(filepath: Union[str, Path]) -> str:
    """
    Load content from a file with proper error handling.
    
    Args:
        filepath: Path to the file to load
        
    Returns:
        File content as string
        
    Raises:
        PrimitiveLoaderError: If file doesn't exist or can't be read
    """
    path = Path(filepath)
    
    if not path.exists():
        raise PrimitiveLoaderError(f"File not found: {filepath}")
    
    if not path.is_file():
        raise PrimitiveLoaderError(f"Path is not a file: {filepath}")
    
    try:
        return path.read_text(encoding='utf-8')
    except (IOError, OSError) as e:
        raise PrimitiveLoaderError(f"Failed to read file {filepath}: {e}")


def load_instructions(filepath: Union[str, Path]) -> str:
    """
    Load instructions from a .instructions.md file.
    
    Args:
        filepath: Path to the .instructions.md file
        
    Returns:
        Instructions content as string (without YAML frontmatter)
        
    Raises:
        PrimitiveLoaderError: If file loading or parsing fails
        
    Example:
        >>> instructions = load_instructions('.instructions.md')
        >>> print(f"Instructions loaded: {len(instructions)} characters")
    """
    try:
        content = _load_file_content(filepath)
        _, markdown_content = _parse_frontmatter(content)
        return markdown_content
    except Exception as e:
        raise PrimitiveLoaderError(f"Failed to load instructions from {filepath}: {e}")


def load_chatmode(filepath: Union[str, Path]) -> Dict[str, Any]:
    """
    Load and parse a .chatmode.md file with YAML frontmatter.
    
    Args:
        filepath: Path to the .chatmode.md file
        
    Returns:
        Dictionary containing:
        - 'metadata': YAML frontmatter as dict
        - 'content': Markdown content as string
        - 'name': Chat mode name (from metadata or filename)
        - 'description': Chat mode description (from metadata)
        - 'capabilities': List of capabilities (from metadata)
        
    Raises:
        PrimitiveLoaderError: If file loading or parsing fails
        
    Example:
        >>> chatmode = load_chatmode('modes/planner.chatmode.md')
        >>> print(f"Chat mode: {chatmode['name']}")
        >>> print(f"Capabilities: {chatmode['capabilities']}")
    """
    try:
        content = _load_file_content(filepath)
        metadata, markdown_content = _parse_frontmatter(content)
        
        # Extract chat mode name from filename if not in metadata
        path = Path(filepath)
        default_name = path.stem.replace('.chatmode', '')
        
        return {
            'metadata': metadata,
            'content': markdown_content,
            'name': metadata.get('name', default_name),
            'description': metadata.get('description', ''),
            'capabilities': metadata.get('capabilities', []),
            'version': metadata.get('version', '1.0'),
            'author': metadata.get('author', 'Darwin Agent'),
            'filepath': str(path.absolute())
        }
    except Exception as e:
        raise PrimitiveLoaderError(f"Failed to load chat mode from {filepath}: {e}")


def load_prompt(filepath: Union[str, Path]) -> Dict[str, Any]:
    """
    Load and parse a .prompt.md file with YAML frontmatter.
    
    Args:
        filepath: Path to the .prompt.md file
        
    Returns:
        Dictionary containing:
        - 'metadata': YAML frontmatter as dict
        - 'content': Markdown content as string
        - 'title': Prompt title (from metadata or filename)
        - 'phases': List of workflow phases (from metadata)
        - 'validation_gates': List of validation requirements (from metadata)
        
    Raises:
        PrimitiveLoaderError: If file loading or parsing fails
        
    Example:
        >>> prompt = load_prompt('scraping-workflow.prompt.md')
        >>> print(f"Workflow: {prompt['title']}")
        >>> print(f"Phases: {len(prompt['phases'])}")
    """
    try:
        content = _load_file_content(filepath)
        metadata, markdown_content = _parse_frontmatter(content)
        
        # Extract prompt title from filename if not in metadata
        path = Path(filepath)
        default_title = path.stem.replace('.prompt', '').replace('-', ' ').title()
        
        return {
            'metadata': metadata,
            'content': markdown_content,
            'title': metadata.get('title', default_title),
            'description': metadata.get('description', ''),
            'phases': metadata.get('phases', []),
            'validation_gates': metadata.get('validation_gates', []),
            'version': metadata.get('version', '1.0'),
            'author': metadata.get('author', 'Darwin Agent'),
            'filepath': str(path.absolute())
        }
    except Exception as e:
        raise PrimitiveLoaderError(f"Failed to load prompt from {filepath}: {e}")


def load_memory(filepath: Union[str, Path]) -> Dict[str, Any]:
    """
    Load and parse a .memory.md file containing agent memory data.
    
    Args:
        filepath: Path to the .memory.md file
        
    Returns:
        Dictionary containing:
        - 'metadata': YAML frontmatter as dict (if present)
        - 'content': Markdown content as string
        - 'last_updated': Last update timestamp (from metadata or file)
        - 'session_count': Number of sessions (parsed from content)
        - 'success_rates': Method success rates (parsed from content)
        - 'learnings': Recent learnings (parsed from content)
        
    Raises:
        PrimitiveLoaderError: If file loading or parsing fails
        
    Example:
        >>> memory = load_memory('.memory.md')
        >>> print(f"Success rates: {memory['success_rates']}")
        >>> print(f"Recent learnings: {len(memory['learnings'])}")
    """
    try:
        content = _load_file_content(filepath)
        metadata, markdown_content = _parse_frontmatter(content)
        
        path = Path(filepath)
        
        # Parse success rates from content using regex
        success_rates = {}
        rate_pattern = r'\|\s*(\w+)\s*\|\s*(\d+)%'
        for match in re.finditer(rate_pattern, markdown_content):
            method, rate = match.groups()
            success_rates[method.lower()] = int(rate)
        
        # Parse session count
        session_pattern = r'Total Sessions.*?(\d+)'
        session_match = re.search(session_pattern, markdown_content)
        session_count = int(session_match.group(1)) if session_match else 0
        
        # Parse recent learnings (sections starting with ###)
        learnings = []
        learning_pattern = r'### (\d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC)\s*\n\*\*Topic\*\*: ([^\n]+)\n((?:- [^\n]+\n?)*)'
        for match in re.finditer(learning_pattern, markdown_content):
            timestamp, topic, details = match.groups()
            learnings.append({
                'timestamp': timestamp,
                'topic': topic,
                'details': [line.strip('- ').strip() for line in details.strip().split('\n') if line.strip()]
            })
        
        return {
            'metadata': metadata,
            'content': markdown_content,
            'last_updated': metadata.get('last_updated', path.stat().st_mtime),
            'session_count': session_count,
            'success_rates': success_rates,
            'learnings': learnings,
            'filepath': str(path.absolute()),
            'file_size': path.stat().st_size
        }
    except Exception as e:
        raise PrimitiveLoaderError(f"Failed to load memory from {filepath}: {e}")


class PrimitiveManager:
    """
    Manager class for loading and caching agentic primitive files.
    
    This class provides a centralized way to load, cache, and manage
    agentic primitive files with automatic reloading when files change.
    """
    
    def __init__(self, base_path: Optional[Union[str, Path]] = None):
        """
        Initialize the primitive manager.
        
        Args:
            base_path: Base directory path for relative file lookups
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._file_mtimes: Dict[str, float] = {}
    
    def _get_full_path(self, filepath: Union[str, Path]) -> Path:
        """Get full path, resolving relative to base_path if needed."""
        path = Path(filepath)
        if not path.is_absolute():
            path = self.base_path / path
        return path
    
    def _is_cache_valid(self, filepath: Union[str, Path]) -> bool:
        """Check if cached version is still valid based on file modification time."""
        path_str = str(self._get_full_path(filepath))
        
        if path_str not in self._cache:
            return False
        
        try:
            current_mtime = Path(path_str).stat().st_mtime
            cached_mtime = self._file_mtimes.get(path_str, 0)
            return current_mtime == cached_mtime
        except (OSError, IOError):
            return False
    
    def _update_cache(self, filepath: Union[str, Path], data: Dict[str, Any]) -> None:
        """Update cache with new data and modification time."""
        path = self._get_full_path(filepath)
        path_str = str(path)
        
        self._cache[path_str] = data
        try:
            self._file_mtimes[path_str] = path.stat().st_mtime
        except (OSError, IOError):
            self._file_mtimes[path_str] = 0
    
    def load_instructions(self, filepath: Union[str, Path], use_cache: bool = True) -> str:
        """Load instructions with optional caching."""
        path_str = str(self._get_full_path(filepath))
        
        if use_cache and self._is_cache_valid(filepath):
            return self._cache[path_str]['content']
        
        content = load_instructions(filepath)
        if use_cache:
            self._update_cache(filepath, {'content': content, 'type': 'instructions'})
        
        return content
    
    def load_chatmode(self, filepath: Union[str, Path], use_cache: bool = True) -> Dict[str, Any]:
        """Load chat mode with optional caching."""
        path_str = str(self._get_full_path(filepath))
        
        if use_cache and self._is_cache_valid(filepath):
            return self._cache[path_str]
        
        data = load_chatmode(filepath)
        if use_cache:
            self._update_cache(filepath, data)
        
        return data
    
    def load_prompt(self, filepath: Union[str, Path], use_cache: bool = True) -> Dict[str, Any]:
        """Load prompt with optional caching."""
        path_str = str(self._get_full_path(filepath))
        
        if use_cache and self._is_cache_valid(filepath):
            return self._cache[path_str]
        
        data = load_prompt(filepath)
        if use_cache:
            self._update_cache(filepath, data)
        
        return data
    
    def load_memory(self, filepath: Union[str, Path], use_cache: bool = True) -> Dict[str, Any]:
        """Load memory with optional caching."""
        path_str = str(self._get_full_path(filepath))
        
        if use_cache and self._is_cache_valid(filepath):
            return self._cache[path_str]
        
        data = load_memory(filepath)
        if use_cache:
            self._update_cache(filepath, data)
        
        return data
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
        self._file_mtimes.clear()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about current cache state."""
        return {
            'cached_files': list(self._cache.keys()),
            'cache_size': len(self._cache),
            'total_memory_usage': sum(
                len(str(data)) for data in self._cache.values()
            )
        }


# Convenience function for quick loading without manager
def load_primitive(filepath: Union[str, Path], primitive_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Automatically detect and load any primitive file type.
    
    Args:
        filepath: Path to the primitive file
        primitive_type: Force specific type ('instructions', 'chatmode', 'prompt', 'memory')
                       If None, will auto-detect from file extension
    
    Returns:
        Dictionary with loaded data, format depends on file type
        
    Raises:
        PrimitiveLoaderError: If file type cannot be determined or loading fails
        
    Example:
        >>> data = load_primitive('modes/planner.chatmode.md')
        >>> print(f"Loaded {data['type']}: {data['name']}")
    """
    path = Path(filepath)
    
    # Determine type from extension if not specified
    if primitive_type is None:
        if '.instructions.' in path.name:
            primitive_type = 'instructions'
        elif '.chatmode.' in path.name:
            primitive_type = 'chatmode'
        elif '.prompt.' in path.name:
            primitive_type = 'prompt'
        elif '.memory.' in path.name:
            primitive_type = 'memory'
        else:
            raise PrimitiveLoaderError(f"Cannot determine primitive type for {filepath}")
    
    # Load based on type
    if primitive_type == 'instructions':
        content = load_instructions(filepath)
        return {'type': 'instructions', 'content': content}
    elif primitive_type == 'chatmode':
        return {**load_chatmode(filepath), 'type': 'chatmode'}
    elif primitive_type == 'prompt':
        return {**load_prompt(filepath), 'type': 'prompt'}
    elif primitive_type == 'memory':
        return {**load_memory(filepath), 'type': 'memory'}
    else:
        raise PrimitiveLoaderError(f"Unknown primitive type: {primitive_type}")


if __name__ == '__main__':
    """Example usage and testing."""
    import sys
    from pathlib import Path
    
    # Example usage
    try:
        base_dir = Path(__file__).parent.parent
        manager = PrimitiveManager(base_dir)
        
        print("🤖 Darwin Agent Primitive Loader - Test Suite")
        print("=" * 50)
        
        # Test loading instructions
        try:
            instructions = manager.load_instructions('.instructions.md')
            print(f"✅ Instructions loaded: {len(instructions)} characters")
        except PrimitiveLoaderError as e:
            print(f"❌ Instructions failed: {e}")
        
        # Test loading memory
        try:
            memory = manager.load_memory('.memory.md')
            print(f"✅ Memory loaded: {memory['session_count']} sessions, {len(memory['success_rates'])} methods")
        except PrimitiveLoaderError as e:
            print(f"❌ Memory failed: {e}")
        
        # Test loading prompt
        try:
            prompt = manager.load_prompt('scraping-workflow.prompt.md')
            print(f"✅ Prompt loaded: '{prompt['title']}' with {len(prompt['phases'])} phases")
        except PrimitiveLoaderError as e:
            print(f"❌ Prompt failed: {e}")
        
        # Test loading chat modes
        chatmode_dir = base_dir / 'darwin-agent' / 'modes'
        if chatmode_dir.exists():
            for chatmode_file in chatmode_dir.glob('*.chatmode.md'):
                try:
                    chatmode = manager.load_chatmode(chatmode_file)
                    print(f"✅ Chat mode loaded: '{chatmode['name']}' ({len(chatmode['capabilities'])} capabilities)")
                except PrimitiveLoaderError as e:
                    print(f"❌ Chat mode {chatmode_file.name} failed: {e}")
        
        # Show cache info
        cache_info = manager.get_cache_info()
        print(f"\n📊 Cache: {cache_info['cache_size']} files, {cache_info['total_memory_usage']} bytes")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        sys.exit(1)