#!/usr/bin/env python3
"""
Example usage of the Darwin Agent Primitive Loader

This script demonstrates how to use the primitive_loader module to load
and work with agentic primitive files.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.primitive_loader import PrimitiveManager, load_primitive, PrimitiveLoaderError

def main():
    """Demonstrate primitive loader functionality."""
    
    print("🤖 Darwin Agent Primitive Loader - Usage Examples")
    print("=" * 55)
    
    # Initialize the manager
    manager = PrimitiveManager()
    
    # Example 1: Load instructions
    print("\n📋 Example 1: Loading Instructions")
    try:
        instructions = manager.load_instructions('.instructions.md')
        print(f"✅ Loaded instructions: {len(instructions):,} characters")
        
        # Extract a sample from instructions
        sample = instructions[:200] + "..." if len(instructions) > 200 else instructions
        print(f"📝 Sample: {sample}")
        
    except PrimitiveLoaderError as e:
        print(f"❌ Error loading instructions: {e}")
    
    # Example 2: Load memory with success rates
    print("\n🧠 Example 2: Loading Memory Data")
    try:
        memory = manager.load_memory('.memory.md')
        print(f"✅ Memory loaded:")
        print(f"   📊 Sessions: {memory['session_count']}")
        print(f"   📈 Success rates: {memory['success_rates']}")
        print(f"   📚 Recent learnings: {len(memory['learnings'])}")
        
        # Show best performing method
        if memory['success_rates']:
            best_method = max(memory['success_rates'].items(), key=lambda x: x[1])
            print(f"   🏆 Best method: {best_method[0]} ({best_method[1]}%)")
            
    except PrimitiveLoaderError as e:
        print(f"❌ Error loading memory: {e}")
    
    # Example 3: Load workflow prompt
    print("\n🔄 Example 3: Loading Workflow Prompt")
    try:
        prompt = manager.load_prompt('scraping-workflow.prompt.md')
        print(f"✅ Workflow loaded:")
        print(f"   📝 Title: {prompt['title']}")
        print(f"   📖 Description: {prompt['description'][:100]}..." if prompt['description'] else "   📖 No description")
        print(f"   🔗 Phases: {len(prompt['phases'])}")
        print(f"   ✅ Validation gates: {len(prompt['validation_gates'])}")
        
    except PrimitiveLoaderError as e:
        print(f"❌ Error loading prompt: {e}")
    
    # Example 4: Load chat modes
    print("\n💬 Example 4: Loading Chat Modes")
    chatmode_dir = Path('darwin-agent/modes')
    if chatmode_dir.exists():
        for chatmode_file in chatmode_dir.glob('*.chatmode.md'):
            try:
                chatmode = manager.load_chatmode(chatmode_file)
                print(f"✅ Chat mode: {chatmode['name']}")
                print(f"   📝 Description: {chatmode['description'][:80]}..." if chatmode['description'] else "   📝 No description")
                print(f"   🔧 Capabilities: {len(chatmode['capabilities'])}")
                print(f"   📄 Content: {len(chatmode['content']):,} characters")
                
            except PrimitiveLoaderError as e:
                print(f"❌ Error loading {chatmode_file.name}: {e}")
    else:
        print("❌ Chat mode directory not found")
    
    # Example 5: Auto-detection with load_primitive
    print("\n🔍 Example 5: Auto-Detection")
    files_to_test = [
        '.instructions.md',
        '.memory.md', 
        'scraping-workflow.prompt.md'
    ]
    
    for filepath in files_to_test:
        try:
            data = load_primitive(filepath)
            print(f"✅ Auto-detected {data['type']}: {Path(filepath).name}")
            
        except PrimitiveLoaderError as e:
            print(f"❌ Auto-detection failed for {filepath}: {e}")
    
    # Example 6: Cache performance
    print("\n⚡ Example 6: Cache Performance")
    import time
    
    # First load (cold cache)
    start_time = time.time()
    manager.load_instructions('.instructions.md')
    cold_time = time.time() - start_time
    
    # Second load (warm cache)
    start_time = time.time()
    manager.load_instructions('.instructions.md')
    warm_time = time.time() - start_time
    
    print(f"📊 Cache performance:")
    print(f"   🔴 Cold load: {cold_time:.4f}s")
    print(f"   🟢 Warm load: {warm_time:.4f}s")
    print(f"   ⚡ Speedup: {cold_time/warm_time:.1f}x")
    
    # Show final cache info
    cache_info = manager.get_cache_info()
    print(f"\n📈 Final Cache Stats:")
    print(f"   📁 Files cached: {cache_info['cache_size']}")
    print(f"   💾 Memory usage: {cache_info['total_memory_usage']:,} bytes")
    
    print("\n✨ All examples completed successfully!")


if __name__ == '__main__':
    main()