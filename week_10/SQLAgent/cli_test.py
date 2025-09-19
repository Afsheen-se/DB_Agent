"""
CLI Test Interface for SQL Agent Scripts
Quick testing interface for all 4 scripts
"""

import os
import sys
from dotenv import load_dotenv

def test_script_00():
    """Test Simple LLM Script"""
    print("🤖 Testing Script 00: Simple LLM")
    print("=" * 50)
    try:
        exec(open('scripts/00_simple_llm.py').read())
        print("✅ Script 00 completed successfully!")
    except Exception as e:
        print(f"❌ Script 00 failed: {e}")
    print()

def test_script_01():
    """Test Simple SQL Agent Script"""
    print("🔍 Testing Script 01: Simple SQL Agent")
    print("=" * 50)
    try:
        exec(open('scripts/01_simple_agent.py').read())
        print("✅ Script 01 completed successfully!")
    except Exception as e:
        print(f"❌ Script 01 failed: {e}")
    print()

def test_script_02():
    """Test Dangerous SQL Agent Script"""
    print("⚠️  Testing Script 02: Dangerous SQL Agent")
    print("=" * 50)
    try:
        exec(open('scripts/02_risky_delete_demo.py').read())
        print("✅ Script 02 completed successfully!")
    except Exception as e:
        print(f"❌ Script 02 failed: {e}")
    print()

def test_script_03():
    """Test Secure SQL Agent Script"""
    print("🛡️  Testing Script 03: Secure SQL Agent")
    print("=" * 50)
    try:
        exec(open('scripts/03_guardrailed_agent.py').read())
        print("✅ Script 03 completed successfully!")
    except Exception as e:
        print(f"❌ Script 03 failed: {e}")
    print()

def test_script_04():
    """Test Advanced Analytics Script"""
    print("📊 Testing Script 04: Advanced Analytics")
    print("=" * 50)
    try:
        exec(open('scripts/04_complex_queries.py').read())
        print("✅ Script 04 completed successfully!")
    except Exception as e:
        print(f"❌ Script 04 failed: {e}")
    print()

def interactive_mode():
    """Interactive CLI for testing individual scripts"""
    print("🎯 Interactive SQL Agent Testing")
    print("=" * 50)
    print("Available scripts:")
    print("0 - Simple LLM (no SQL)")
    print("1 - Simple SQL Agent")
    print("2 - Dangerous SQL Agent (⚠️  educational)")
    print("3 - Secure SQL Agent")
    print("4 - Advanced Analytics")
    print("5 - Test all scripts")
    print("q - Quit")
    print()
    
    while True:
        choice = input("Select script to test (0-5, q): ").strip().lower()
        
        if choice == 'q':
            print("👋 Goodbye!")
            break
        elif choice == '0':
            test_script_00()
        elif choice == '1':
            test_script_01()
        elif choice == '2':
            print("⚠️  WARNING: This script demonstrates dangerous patterns!")
            confirm = input("Continue? (y/N): ").strip().lower()
            if confirm == 'y':
                test_script_02()
            else:
                print("Skipped.")
        elif choice == '3':
            test_script_03()
        elif choice == '4':
            test_script_04()
        elif choice == '5':
            print("🚀 Testing all scripts...")
            test_script_00()
            test_script_01()
            test_script_02()
            test_script_03()
            test_script_04()
            print("🎉 All tests completed!")
        else:
            print("❌ Invalid choice. Please select 0-5 or q.")

def main():
    """Main CLI interface"""
    load_dotenv()
    
    print("🤖 SQL Agent CLI Test Interface")
    print("=" * 60)
    print("Testing SQL Agent scripts with Gemini API")
    print()
    
    # Check if API key is set
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ ERROR: GEMINI_API_KEY not found in environment!")
        print("Please set your Google Gemini API key in the .env file")
        return
    
    print("✅ GEMINI_API_KEY found")
    print()
    
    # Check if database exists
    if not os.path.exists('sql_agent_class.db'):
        print("❌ ERROR: Database file not found!")
        print("Please ensure sql_agent_class.db exists in the current directory")
        return
    
    print("✅ Database file found")
    print()
    
    # Start interactive mode
    interactive_mode()

if __name__ == "__main__":
    main()
