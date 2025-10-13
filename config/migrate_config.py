#!/usr/bin/env python3
"""
Migration script to update existing configuration to use the new centralized system
"""

import os
import sys
import json
from pathlib import Path

def migrate_env_files():
    """Migrate environment files to centralized config"""
    project_root = Path(__file__).parent.parent
    
    # Check for old .env files
    old_locations = [
        project_root / "AI-WebAgent-Extractor" / ".env",
        project_root / ".env"
    ]
    
    new_location = project_root / "config" / ".env"
    
    print("=== Environment Configuration Migration ===")
    
    found_old_files = []
    for old_path in old_locations:
        if old_path.exists():
            found_old_files.append(old_path)
            print(f"Found old .env file: {old_path}")
    
    if not found_old_files:
        print("No old .env files found to migrate.")
        return
    
    # Read existing keys from old files
    env_vars = {}
    for old_path in found_old_files:
        print(f"Reading from: {old_path}")
        try:
            with open(old_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        except Exception as e:
            print(f"Error reading {old_path}: {e}")
    
    if env_vars:
        print(f"Found {len(env_vars)} environment variables:")
        for key in env_vars:
            print(f"  - {key}")
        
        # Create new centralized .env file
        if new_location.exists():
            backup_path = new_location.with_suffix('.env.backup')
            print(f"Backing up existing config to: {backup_path}")
            new_location.rename(backup_path)
        
        print(f"Creating new centralized config: {new_location}")
        with open(new_location, 'w') as f:
            f.write("# Centralized environment configuration for AI-WebAgent-Extractor\n")
            f.write("# Migrated from old .env files\n\n")
            
            # Write AI API keys first
            ai_keys = ['OPENAI_API_KEY', 'GEMINI_API_KEY']
            f.write("# AI API Keys\n")
            for key in ai_keys:
                if key in env_vars:
                    f.write(f"{key}={env_vars[key]}\n")
                else:
                    f.write(f"# {key}=your_{key.lower()}_here\n")
            
            # Write traffic analysis keys
            traffic_keys = ['SEMRUSH_API_KEY', 'SIMILARWEB_API_KEY']
            f.write("\n# Traffic Analysis API Keys (optional)\n")
            for key in traffic_keys:
                if key in env_vars:
                    f.write(f"{key}={env_vars[key]}\n")
                else:
                    f.write(f"# {key}=your_{key.lower()}_here\n")
            
            # Write configuration
            f.write("\n# Scraping Configuration\n")
            config_keys = ['DEFAULT_DELAY', 'MAX_RETRIES', 'MAX_WORKERS', 'AI_PROVIDER']
            defaults = {'DEFAULT_DELAY': '2', 'MAX_RETRIES': '3', 'MAX_WORKERS': '5', 'AI_PROVIDER': 'auto'}
            for key in config_keys:
                value = env_vars.get(key, defaults.get(key, ''))
                f.write(f"{key}={value}\n")
        
        # Remove old files after successful migration
        response = input("Migration complete! Remove old .env files? (y/N): ")
        if response.lower() == 'y':
            for old_path in found_old_files:
                try:
                    old_path.unlink()
                    print(f"Removed: {old_path}")
                except Exception as e:
                    print(f"Error removing {old_path}: {e}")
        else:
            print("Old .env files kept. Please remove them manually after testing.")
    
    print("\n=== Migration Summary ===")
    print(f"New configuration location: {new_location}")
    print("Update your scripts to use the new env_config module:")
    print("  from config.env_config import get_environment_config")

def update_gitignore():
    """Update .gitignore to include new .env location"""
    project_root = Path(__file__).parent.parent
    gitignore_path = project_root / ".gitignore"
    
    if not gitignore_path.exists():
        print("No .gitignore found, skipping gitignore update")
        return
    
    print("=== Updating .gitignore ===")
    
    # Read current gitignore
    with open(gitignore_path, 'r') as f:
        content = f.read()
    
    # Check if config/.env is already ignored
    if "config/.env" not in content:
        print("Adding config/.env to .gitignore")
        with open(gitignore_path, 'a') as f:
            f.write("\n# Centralized environment configuration\n")
            f.write("config/.env\n")
        print("Updated .gitignore")
    else:
        print("config/.env already in .gitignore")

def test_new_configuration():
    """Test the new configuration system"""
    print("\n=== Testing New Configuration ===")
    
    # Add config to path
    sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        from env_config import validate_environment, get_environment_config
        
        config = get_environment_config()
        validation = validate_environment()
        
        print(f"Configuration valid: {validation['valid']}")
        print(f"Available providers: {validation['available_providers']}")
        print(f"Selected provider: {validation['config']['selected_provider']}")
        
        if validation['warnings']:
            print("Warnings:")
            for warning in validation['warnings']:
                print(f"  - {warning}")
        
        if validation['errors']:
            print("Errors:")
            for error in validation['errors']:
                print(f"  - {error}")
        
        print("✅ New configuration system working correctly!")
        
    except Exception as e:
        print(f"❌ Error testing new configuration: {e}")

if __name__ == "__main__":
    print("AI-WebAgent-Extractor Configuration Migration Tool")
    print("=" * 50)
    
    migrate_env_files()
    update_gitignore()
    test_new_configuration()
    
    print("\n" + "=" * 50)
    print("Migration complete!")
    print("Next steps:")
    print("1. Update your API keys in config/.env")
    print("2. Test your scrapers with the new configuration")
    print("3. Remove any remaining old .env files")