#!/usr/bin/env python3
"""
Test suite for Darwin Agent agentic primitive files

This module tests the validity and completeness of all agentic primitive files
including chat modes, instructions, memory, and workflow prompts.

Author: Darwin Agent Framework
Date: October 15, 2025
"""

import os
import re
import json
import yaml
import pytest
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path for imports
import sys
current_dir = Path(__file__).parent
project_root = current_dir.parent if current_dir.name == 'tests' else current_dir
sys.path.insert(0, str(project_root))

from utils.primitive_loader import (
    PrimitiveManager, 
    PrimitiveLoaderError,
    load_instructions,
    load_chatmode,
    load_prompt,
    load_memory
)


class TestAgenticPrimitives:
    """Test suite for agentic primitive file validation"""
    
    @pytest.fixture(scope="class")
    def primitive_manager(self):
        """Fixture to provide primitive manager instance"""
        return PrimitiveManager(project_root)
    
    @pytest.fixture(scope="class")
    def chatmode_files(self):
        """Fixture to discover all chatmode files"""
        chatmode_dir = project_root / "darwin-agent" / "modes"
        if chatmode_dir.exists():
            return list(chatmode_dir.glob("*.chatmode.md"))
        return []
    
    @pytest.fixture(scope="class")
    def workflow_files(self):
        """Fixture to discover all workflow files"""
        workflow_files = []
        
        # Check for main workflow prompt
        main_workflow = project_root / "scraping-workflow.prompt.md"
        if main_workflow.exists():
            workflow_files.append(main_workflow)
        
        # Check for additional workflow files
        for pattern in ["*.prompt.md", "*.workflow.md"]:
            workflow_files.extend(project_root.glob(pattern))
        
        return workflow_files
    
    def test_instructions_file_exists(self):
        """Test that .instructions.md file exists and is readable"""
        instructions_file = project_root / ".instructions.md"
        assert instructions_file.exists(), f"Instructions file not found: {instructions_file}"
        assert instructions_file.is_file(), f"Instructions path is not a file: {instructions_file}"
        
        # Test file is readable
        content = instructions_file.read_text(encoding='utf-8')
        assert len(content) > 0, "Instructions file is empty"
        assert len(content) > 1000, f"Instructions file too short: {len(content)} characters"
    
    def test_instructions_loading(self, primitive_manager):
        """Test loading instructions through primitive manager"""
        try:
            instructions = primitive_manager.load_instructions('.instructions.md')
            assert isinstance(instructions, str), "Instructions should be returned as string"
            assert len(instructions) > 1000, f"Instructions too short: {len(instructions)} characters"
            assert "Darwin.md" in instructions, "Instructions should mention Darwin.md"
        except PrimitiveLoaderError as e:
            pytest.fail(f"Failed to load instructions: {e}")
    
    def test_instructions_apply_to_patterns(self, primitive_manager):
        """Test that instructions contain applyTo patterns for GitHub Copilot"""
        try:
            instructions = primitive_manager.load_instructions('.instructions.md')
            
            # Check for YAML frontmatter with applyTo
            frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
            match = re.match(frontmatter_pattern, instructions, re.DOTALL)
            
            if match:
                yaml_content = match.group(1)
                try:
                    metadata = yaml.safe_load(yaml_content)
                    if 'applyTo' in metadata:
                        apply_to = metadata['applyTo']
                        assert isinstance(apply_to, list), "applyTo should be a list"
                        assert len(apply_to) > 0, "applyTo should not be empty"
                        
                        # Check for common Python patterns
                        patterns = ' '.join(apply_to)
                        assert any(pattern in patterns for pattern in ['*.py', 'python', '.py$']), \
                            f"applyTo should include Python file patterns, got: {apply_to}"
                except yaml.YAMLError as e:
                    pytest.fail(f"Invalid YAML in instructions frontmatter: {e}")
        except PrimitiveLoaderError as e:
            pytest.fail(f"Failed to load instructions: {e}")
    
    def test_memory_file_exists(self):
        """Test that .memory.md file exists and is valid"""
        memory_file = project_root / ".memory.md"
        assert memory_file.exists(), f"Memory file not found: {memory_file}"
        assert memory_file.is_file(), f"Memory path is not a file: {memory_file}"
        
        # Test file is readable
        content = memory_file.read_text(encoding='utf-8')
        assert len(content) > 0, "Memory file is empty"
    
    def test_memory_loading(self, primitive_manager):
        """Test loading memory through primitive manager"""
        try:
            memory = primitive_manager.load_memory('.memory.md')
            assert isinstance(memory, dict), "Memory should be returned as dictionary"
            
            # Check required fields
            assert 'content' in memory, "Memory should have content field"
            assert 'success_rates' in memory, "Memory should have success_rates field"
            assert 'session_count' in memory, "Memory should have session_count field"
            
            # Validate success rates
            success_rates = memory['success_rates']
            assert isinstance(success_rates, dict), "Success rates should be a dictionary"
            
            # Check for expected methods
            expected_methods = {'drissionpage', 'selenium', 'beautifulsoup', 'auto'}
            found_methods = set(success_rates.keys())
            intersection = expected_methods.intersection(found_methods)
            assert len(intersection) > 0, f"No expected methods found in success rates: {found_methods}"
            
            # Validate success rate values
            for method, rate in success_rates.items():
                assert isinstance(rate, (int, float)), f"Success rate for {method} should be numeric: {rate}"
                assert 0 <= rate <= 100, f"Success rate for {method} should be 0-100: {rate}"
                
        except PrimitiveLoaderError as e:
            pytest.fail(f"Failed to load memory: {e}")
    
    def test_memory_markdown_structure(self, primitive_manager):
        """Test that memory file has proper Markdown structure"""
        try:
            memory = primitive_manager.load_memory('.memory.md')
            content = memory['content']
            
            # Check for key sections
            required_sections = [
                'Method Success Rates',
                'Recent Learnings',
                'Current Session Status'
            ]
            
            for section in required_sections:
                assert section in content, f"Memory should contain '{section}' section"
            
            # Check for table structure (success rates table)
            table_pattern = r'\|.*\|.*\|'
            assert re.search(table_pattern, content), "Memory should contain at least one table"
            
            # Check for learning entries with timestamps
            learning_pattern = r'### \d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC'
            learning_matches = re.findall(learning_pattern, content)
            assert len(learning_matches) > 0, "Memory should contain timestamped learning entries"
            
        except PrimitiveLoaderError as e:
            pytest.fail(f"Failed to load memory for structure test: {e}")
    
    def test_chatmode_files_exist(self, chatmode_files):
        """Test that chatmode files exist"""
        assert len(chatmode_files) > 0, "No chatmode files found"
        
        # Check for expected chatmode files
        expected_chatmodes = {'planner', 'executor', 'judge'}
        found_chatmodes = {f.stem.replace('.chatmode', '') for f in chatmode_files}
        
        for expected in expected_chatmodes:
            assert expected in found_chatmodes, f"Missing expected chatmode: {expected}.chatmode.md"
    
    def test_chatmode_yaml_frontmatter(self, chatmode_files):
        """Test that each chatmode file has valid YAML frontmatter"""
        for chatmode_file in chatmode_files:
            content = chatmode_file.read_text(encoding='utf-8')
            
            # Check for YAML frontmatter delimiters
            frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
            match = re.match(frontmatter_pattern, content, re.DOTALL)
            
            assert match, f"Chatmode file {chatmode_file.name} missing YAML frontmatter"
            
            yaml_content = match.group(1)
            try:
                metadata = yaml.safe_load(yaml_content)
                assert isinstance(metadata, dict), f"YAML frontmatter should be a dictionary in {chatmode_file.name}"
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML frontmatter in {chatmode_file.name}: {e}")
    
    def test_chatmode_required_fields(self, chatmode_files, primitive_manager):
        """Test that each chatmode has required fields"""
        for chatmode_file in chatmode_files:
            try:
                chatmode = primitive_manager.load_chatmode(chatmode_file)
                
                # Check required fields
                assert 'description' in chatmode['metadata'], f"Missing description in {chatmode_file.name}"
                assert 'name' in chatmode, f"Missing name in {chatmode_file.name}"
                assert 'content' in chatmode, f"Missing content in {chatmode_file.name}"
                
                # Validate field types and content
                description = chatmode['metadata']['description']
                assert isinstance(description, str), f"Description should be string in {chatmode_file.name}"
                assert len(description) > 10, f"Description too short in {chatmode_file.name}: {description}"
                
                name = chatmode['name']
                assert isinstance(name, str), f"Name should be string in {chatmode_file.name}"
                assert len(name) > 0, f"Name should not be empty in {chatmode_file.name}"
                
                content = chatmode['content']
                assert isinstance(content, str), f"Content should be string in {chatmode_file.name}"
                assert len(content) > 100, f"Content too short in {chatmode_file.name}: {len(content)} characters"
                
            except PrimitiveLoaderError as e:
                pytest.fail(f"Failed to load chatmode {chatmode_file.name}: {e}")
    
    def test_chatmode_content_structure(self, chatmode_files, primitive_manager):
        """Test chatmode content has proper structure"""
        for chatmode_file in chatmode_files:
            try:
                chatmode = primitive_manager.load_chatmode(chatmode_file)
                content = chatmode['content']
                
                # Check for key sections
                assert '# ' in content, f"Chatmode {chatmode_file.name} should have main heading"
                assert '## ' in content, f"Chatmode {chatmode_file.name} should have subheadings"
                
                # Check for role/domain content
                role_indicators = ['Role', 'Domain', 'Specialist', 'Agent', 'Expert']
                has_role_content = any(indicator in content for indicator in role_indicators)
                assert has_role_content, f"Chatmode {chatmode_file.name} should contain role/domain information"
                
                # Check for Darwin.md specific content
                darwin_indicators = ['Darwin.md', 'darwin', 'scraping', 'extraction']
                has_darwin_content = any(indicator in content.lower() for indicator in darwin_indicators)
                assert has_darwin_content, f"Chatmode {chatmode_file.name} should contain Darwin.md specific content"
                
            except PrimitiveLoaderError as e:
                pytest.fail(f"Failed to load chatmode {chatmode_file.name} for content test: {e}")
    
    def test_workflow_prompt_exists(self, workflow_files):
        """Test that workflow prompt files exist"""
        assert len(workflow_files) > 0, "No workflow prompt files found"
        
        # Check for main workflow file
        main_workflow = project_root / "scraping-workflow.prompt.md"
        assert main_workflow.exists(), "Main scraping-workflow.prompt.md not found"
    
    def test_workflow_prompt_loading(self, workflow_files, primitive_manager):
        """Test loading workflow prompt files"""
        for workflow_file in workflow_files:
            try:
                prompt = primitive_manager.load_prompt(workflow_file)
                
                # Check required fields
                assert 'title' in prompt, f"Missing title in {workflow_file.name}"
                assert 'content' in prompt, f"Missing content in {workflow_file.name}"
                
                # Validate content
                title = prompt['title']
                assert isinstance(title, str), f"Title should be string in {workflow_file.name}"
                assert len(title) > 0, f"Title should not be empty in {workflow_file.name}"
                
                content = prompt['content']
                assert isinstance(content, str), f"Content should be string in {workflow_file.name}"
                assert len(content) > 200, f"Content too short in {workflow_file.name}: {len(content)} characters"
                
            except PrimitiveLoaderError as e:
                pytest.fail(f"Failed to load workflow prompt {workflow_file.name}: {e}")
    
    def test_workflow_required_phases(self, primitive_manager):
        """Test that main workflow has required phases"""
        main_workflow = project_root / "scraping-workflow.prompt.md"
        if not main_workflow.exists():
            pytest.skip("Main workflow file not found")
        
        try:
            prompt = primitive_manager.load_prompt(main_workflow)
            content = prompt['content']
            
            # Check for workflow phases
            expected_phases = [
                'Context',
                'Plan', 
                'Execute',
                'Evaluate'
            ]
            
            found_phases = []
            for phase in expected_phases:
                if phase.lower() in content.lower():
                    found_phases.append(phase)
            
            assert len(found_phases) >= 3, f"Workflow should contain at least 3 phases, found: {found_phases}"
            
            # Check for validation gates
            validation_patterns = ['🚨', 'validation', 'gate', 'checkpoint']
            has_validation = any(pattern in content.lower() for pattern in validation_patterns)
            assert has_validation, "Workflow should contain validation gates or checkpoints"
            
        except PrimitiveLoaderError as e:
            pytest.fail(f"Failed to load main workflow: {e}")
    
    def test_file_reference_integrity(self, primitive_manager):
        """Test that file references in workflows exist (no broken links)"""
        # Get all primitive files
        files_to_check = []
        
        # Add workflow files
        main_workflow = project_root / "scraping-workflow.prompt.md"
        if main_workflow.exists():
            files_to_check.append(main_workflow)
        
        # Add chatmode files
        chatmode_dir = project_root / "darwin-agent" / "modes"
        if chatmode_dir.exists():
            files_to_check.extend(chatmode_dir.glob("*.chatmode.md"))
        
        # Check for file references
        broken_references = []
        
        for file_path in files_to_check:
            try:
                content = file_path.read_text(encoding='utf-8')
                
                # Look for markdown links [text](file.md)
                link_pattern = r'\[([^\]]+)\]\(([^)]+\.md)\)'
                links = re.findall(link_pattern, content)
                
                for link_text, link_target in links:
                    # Resolve relative paths
                    if not link_target.startswith(('http://', 'https://')):
                        target_path = file_path.parent / link_target
                        if not target_path.exists():
                            broken_references.append({
                                'file': file_path.name,
                                'link_text': link_text,
                                'target': link_target,
                                'resolved_path': str(target_path)
                            })
                
                # Look for file includes or references
                include_patterns = [
                    r'@include\s+([^\s]+\.md)',
                    r'import\s+([^\s]+\.md)',
                    r'load\s+([^\s]+\.md)'
                ]
                
                for pattern in include_patterns:
                    includes = re.findall(pattern, content)
                    for include_target in includes:
                        target_path = file_path.parent / include_target
                        if not target_path.exists():
                            broken_references.append({
                                'file': file_path.name,
                                'type': 'include',
                                'target': include_target,
                                'resolved_path': str(target_path)
                            })
                            
            except Exception as e:
                pytest.fail(f"Error checking file references in {file_path.name}: {e}")
        
        if broken_references:
            error_msg = "Broken file references found:\n"
            for ref in broken_references:
                error_msg += f"  - {ref['file']}: {ref.get('type', 'link')} to {ref['target']} (not found at {ref['resolved_path']})\n"
            pytest.fail(error_msg)
    
    def test_yaml_parsing_robustness(self, primitive_manager):
        """Test that all YAML parsing is robust and doesn't fail unexpectedly"""
        # Test with various YAML edge cases
        test_yamls = [
            # Valid YAML
            "description: 'Test description'\nversion: 1.0",
            
            # YAML with special characters
            "description: 'Test with: colons and \"quotes\"'\nlist: [item1, item2]",
            
            # YAML with multiline
            "description: |\n  Multi-line\n  description\n  here",
            
            # YAML with nested structures
            "metadata:\n  description: 'Nested'\n  config:\n    enabled: true"
        ]
        
        for i, yaml_content in enumerate(test_yamls):
            try:
                parsed = yaml.safe_load(yaml_content)
                assert isinstance(parsed, dict), f"Test YAML {i} should parse to dict"
            except yaml.YAMLError as e:
                pytest.fail(f"Test YAML {i} should be valid: {e}")
    
    def test_primitive_manager_caching(self, primitive_manager):
        """Test that primitive manager caching works correctly"""
        instructions_file = '.instructions.md'
        
        # Load instructions twice
        instructions1 = primitive_manager.load_instructions(instructions_file)
        instructions2 = primitive_manager.load_instructions(instructions_file)
        
        # Should be identical (from cache)
        assert instructions1 == instructions2, "Cached instructions should be identical"
        
        # Check cache info
        cache_info = primitive_manager.get_cache_info()
        assert cache_info['cache_size'] > 0, "Cache should contain files"
        assert instructions_file.replace('./', '') in str(cache_info['cached_files']), "Instructions should be cached"
    
    def test_error_handling_resilience(self, primitive_manager):
        """Test error handling for invalid or missing files"""
        # Test loading non-existent file
        with pytest.raises(PrimitiveLoaderError):
            primitive_manager.load_instructions('nonexistent.md')
        
        # Test loading file with invalid YAML
        invalid_yaml_file = project_root / "test_invalid.md"
        try:
            invalid_yaml_file.write_text("---\ninvalid: yaml: content: here\n---\nContent")
            
            with pytest.raises(PrimitiveLoaderError):
                primitive_manager.load_chatmode(invalid_yaml_file)
                
        finally:
            # Clean up test file
            if invalid_yaml_file.exists():
                invalid_yaml_file.unlink()
    
    def test_all_primitive_files_integration(self, primitive_manager):
        """Integration test: load all primitive files together"""
        loaded_files = {}
        errors = []
        
        # Try to load all expected files
        file_loaders = [
            ('.instructions.md', 'load_instructions'),
            ('.memory.md', 'load_memory'),
            ('scraping-workflow.prompt.md', 'load_prompt'),
        ]
        
        for filepath, loader_method in file_loaders:
            try:
                loader_func = getattr(primitive_manager, loader_method)
                result = loader_func(filepath)
                loaded_files[filepath] = result
            except PrimitiveLoaderError as e:
                errors.append(f"{filepath}: {e}")
        
        # Try to load chatmode files
        chatmode_dir = project_root / "darwin-agent" / "modes"
        if chatmode_dir.exists():
            for chatmode_file in chatmode_dir.glob("*.chatmode.md"):
                try:
                    result = primitive_manager.load_chatmode(chatmode_file)
                    loaded_files[str(chatmode_file)] = result
                except PrimitiveLoaderError as e:
                    errors.append(f"{chatmode_file.name}: {e}")
        
        # Report results
        if errors:
            error_msg = "Failed to load primitive files:\n" + "\n".join(f"  - {error}" for error in errors)
            pytest.fail(error_msg)
        
        assert len(loaded_files) >= 4, f"Should load at least 4 files, loaded: {len(loaded_files)}"
        
        # Verify cache performance
        cache_info = primitive_manager.get_cache_info()
        assert cache_info['cache_size'] >= len(loaded_files), "All loaded files should be cached"


def test_pytest_framework_available():
    """Test that pytest framework is properly available"""
    import pytest
    assert hasattr(pytest, 'fixture'), "pytest fixtures should be available"
    assert hasattr(pytest, 'mark'), "pytest marks should be available"


if __name__ == '__main__':
    """Run tests directly if executed as script"""
    pytest.main([__file__, '-v', '--tb=short'])