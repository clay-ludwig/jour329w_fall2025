#!/usr/bin/env python3
"""
Test script to verify setup and demonstrate tool functionality
"""

import json
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_setup():
    """Verify the environment is set up correctly"""
    print("="*60)
    print("Beat Book Agent - Setup Verification")
    print("="*60)
    print()
    
    # Check Python version
    print("✓ Checking Python version...")
    if sys.version_info < (3, 8):
        print("  ❌ Python 3.8+ required")
        return False
    print(f"  ✓ Python {sys.version.split()[0]}")
    print()
    
    # Check dependencies
    print("✓ Checking dependencies...")
    deps = {
        'anthropic': 'Anthropic API client',
        'flask': 'Flask web framework',
        'flask_socketio': 'Flask-SocketIO for web monitor'
    }
    
    missing = []
    for module, desc in deps.items():
        try:
            __import__(module)
            print(f"  ✓ {module}: {desc}")
        except ImportError:
            print(f"  ❌ {module}: NOT INSTALLED")
            missing.append(module)
    
    if missing:
        print()
        print("  Install missing dependencies:")
        print("  pip install -r requirements.txt")
        return False
    print()
    
    # Check API key
    print("✓ Checking API key...")
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("  ❌ ANTHROPIC_API_KEY environment variable not set")
        print()
        print("  Set your API key:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        return False
    print(f"  ✓ API key found ({api_key[:10]}...)")
    print()
    
    # Check data files
    print("✓ Checking data files...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(os.path.dirname(script_dir), "enhanced_beat_stories.json")
    prompt_path = os.path.join(os.path.dirname(script_dir), "prompt.txt")
    
    if not os.path.exists(json_path):
        print(f"  ❌ Story data not found: {json_path}")
        return False
    print(f"  ✓ Story data found")
    
    if not os.path.exists(prompt_path):
        print(f"  ❌ Prompt not found: {prompt_path}")
        return False
    print(f"  ✓ Prompt file found")
    print()
    
    # Load and test database
    print("✓ Testing story database...")
    try:
        from beat_book_agent import StoryDatabase
        db = StoryDatabase(json_path)
        stats = db.get_stats()
        
        print(f"  ✓ Loaded {stats['total_stories']} stories")
        print(f"  ✓ Topics: {', '.join(list(stats['topics'].keys())[:5])}...")
        print(f"  ✓ {stats['total_unique_tags']} unique tags")
        print()
        
        # Test a search
        print("✓ Testing search functionality...")
        results = db.search_by_keyword("education", limit=5)
        print(f"  ✓ Found {len(results)} stories about 'education'")
        if results:
            print(f"  ✓ Example: {results[0]['title'][:60]}...")
        print()
        
        # Test filtering
        print("✓ Testing filter functionality...")
        edu_stories = db.filter_by_topic("Education", limit=10)
        print(f"  ✓ Found {len(edu_stories)} Education stories")
        print()
        
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
        return False
    
    # Success!
    print("="*60)
    print("✅ ALL CHECKS PASSED!")
    print("="*60)
    print()
    print("Ready to run:")
    print("  • CLI mode: python3 beat_book_agent.py")
    print("  • Web mode: python3 web_monitor.py")
    print("  • Launcher:  ./run.sh")
    print()
    
    return True


def demo_tools():
    """Demonstrate tool capabilities"""
    print("="*60)
    print("Tool Demonstration - NEW Consolidated Tools")
    print("="*60)
    print()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(os.path.dirname(script_dir), "enhanced_beat_stories.json")
    
    from beat_book_agent import StoryDatabase
    db = StoryDatabase(json_path)
    
    # Demo 1: Dataset overview (NEW)
    print("🔧 Tool: get_dataset_overview()")
    print("-" * 60)
    overview = db.get_dataset_overview()
    print(f"Total Stories: {overview['total_stories']}")
    print(f"Topics: {json.dumps(overview['topics_breakdown'], indent=2)}")
    print(f"Top 5 Locations:")
    for loc, count in list(overview['top_locations'].items())[:5]:
        print(f"  • {loc}: {count} stories")
    print(f"High Potential Stories: {overview['follow_up_metrics']['high_potential_stories']}")
    print()
    
    # Demo 2: Unified query (NEW - replaces 6 old tools)
    print("🔧 Tool: query_stories(topic='Education', min_follow_up_rating=7)")
    print("-" * 60)
    results = db.query_stories(topic="Education", min_follow_up_rating=7, limit=3)
    print(f"Found {len(results)} high-value education stories")
    for i, story in enumerate(results, 1):
        print(f"\n{i}. {story['title'][:70]}...")
        print(f"   Rating: {story['metadata_follow_up_rating']}")
    print()
    
    # Demo 3: Coverage patterns analysis (NEW)
    print("🔧 Tool: analyze_coverage_patterns('Education')")
    print("-" * 60)
    patterns = db.analyze_coverage_patterns("Education")
    print(f"Total Education Stories: {patterns['total_stories']}")
    print(f"Top 5 Themes:")
    for theme, count in list(patterns['dominant_themes'].items())[:5]:
        print(f"  • {theme}: {count} mentions")
    print(f"Top 3 Locations:")
    for loc, count in list(patterns['geographic_coverage'].items())[:3]:
        print(f"  • {loc}: {count} stories")
    print()
    
    # Demo 4: Coverage gaps (NEW)
    print("🔧 Tool: find_coverage_gaps('Education')")
    print("-" * 60)
    gaps = db.find_coverage_gaps("Education")
    print(f"Locations Covered: {gaps['locations_covered']}")
    print(f"Underreported Locations: {', '.join(gaps['underreported_locations'][:5])}")
    print(f"Stories Needing Follow-up: {len(gaps['stories_needing_followup'])}")
    print(f"\nSuggestion: {gaps['suggestions']['geographic']}")
    print()
    
    # Demo 5: Institutional analysis (NEW)
    print("🔧 Tool: get_institutional_analysis('Education')")
    print("-" * 60)
    inst_analysis = db.get_institutional_analysis(topic="Education")
    print(f"Total Institutions Mentioned: {inst_analysis['total_institutions_mentioned']}")
    print(f"Top 3 Institutions:")
    for inst, data in list(inst_analysis['top_institutions'].items())[:3]:
        print(f"  • {inst}: {data['mention_count']} mentions")
    print()
    
    print("="*60)
    print("NEW TOOLS provide:")
    print("  ✓ Consolidated queries (no confusion)")
    print("  ✓ Pattern analysis (understand themes)")
    print("  ✓ Gap identification (find story ideas)")
    print("  ✓ Strategic insights (key players, locations)")
    print("="*60)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # Run demo
        demo_tools()
    else:
        # Run setup verification
        success = test_setup()
        sys.exit(0 if success else 1)
