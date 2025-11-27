#!/usr/bin/env python3
"""
Quick test script to verify research functionality
Run this to test if research agents work before testing the full Gradio app
"""

import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("=" * 60)
print("Testing ContentFlow AI Research Components")
print("=" * 60)

# Test imports
print("\n1. Testing imports...")
try:
    from research_agent import ResearchAgent
    from database_manager import DatabaseManager
    print("   ✅ All imports successful")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    exit(1)

# Test ResearchAgent initialization
print("\n2. Testing ResearchAgent initialization...")
try:
    agent = ResearchAgent()
    print("   ✅ ResearchAgent initialized")
    print(f"   Using model: {agent.model}")
except Exception as e:
    print(f"   ❌ Initialization failed: {e}")
    exit(1)

# Test ArXiv search
print("\n3. Testing ArXiv search...")
try:
    results = agent.search_arxiv("machine learning", max_results=2)
    print(f"   ✅ ArXiv search returned {len(results)} results")
    if results:
        print(f"   Sample: {results[0]['title'][:60]}...")
except Exception as e:
    print(f"   ⚠️  ArXiv search failed: {e}")

# Test Web search
print("\n4. Testing Web search...")
try:
    results = agent.search_web("artificial intelligence", max_results=2)
    print(f"   ✅ Web search returned {len(results)} results")
    if results:
        print(f"   Sample: {results[0]['title'][:60]}...")
except Exception as e:
    print(f"   ⚠️  Web search failed: {e}")

# Test insights extraction
print("\n5. Testing AI insight extraction...")
try:
    test_sources = {
        "web": [
            {"title": "AI Trends 2024", "snippet": "Artificial intelligence is evolving rapidly with new breakthroughs in deep learning and neural networks."}
        ]
    }
    insights = agent.extract_insights(test_sources)
    print(f"   ✅ Extracted {len(insights)} insights")
    if insights:
        print(f"   Sample: {insights[0][:80]}...")
except Exception as e:
    print(f"   ⚠️  Insight extraction failed: {e}")

# Test Database
print("\n6. Testing Database...")
try:
    db = DatabaseManager("test_contentflow.db")
    print("   ✅ Database initialized")
    
    # Clean up test db
    import os
    if os.path.exists("test_contentflow.db"):
        os.remove("test_contentflow.db")
        print("   ✅ Test database cleaned up")
except Exception as e:
    print(f"   ⚠️  Database test failed: {e}")

print("\n" + "=" * 60)
print("✅ All tests completed!")
print("=" * 60)
print("\nYou can now run: python app.py")
print("Then open: http://localhost:7860")
