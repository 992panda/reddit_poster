#!/usr/bin/env python3
"""
Quick Demo of Reddit Posting Tool
Shows basic functionality without requiring full setup
"""

import json
import os
from datetime import datetime

def create_demo_post():
    """Create a sample post for demonstration"""
    demo_post = {
        "subreddit": "test",
        "title": f"Demo Post - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "content": """This is a demonstration post created by the Reddit Posting Tool.

🚀 **Features:**
- Automated posting to multiple subreddits
- Safety features to prevent account bans
- Dry-run mode for testing
- Beautiful web interface
- Comprehensive logging
- Rate limiting and delays

⚠️ **Safety First:**
Always test with dry-run mode before live posting!

This tool includes:
✅ Random delays between posts (60-300 seconds)
✅ Rate limiting (max 50 requests/minute) 
✅ Post validation
✅ Subreddit accessibility checks
✅ Session limits
✅ Comprehensive error handling

Perfect for content creators, marketers, and community managers who need to post across multiple subreddits efficiently and safely.""",
        "flair": "Test",
        "delay": 90
    }
    
    return demo_post

def show_tool_overview():
    """Display tool overview"""
    print("🚀 Reddit Posting Tool - Complete Solution")
    print("=" * 60)
    print()
    
    print("📋 WHAT'S INCLUDED:")
    print("├── reddit_poster.py     - Main application (CLI + Web UI)")
    print("├── config.py           - Configuration management")
    print("├── utils.py            - Safety features & utilities")
    print("├── requirements.txt    - Python dependencies")
    print("├── .env               - Your Reddit API credentials")
    print("├── examples/          - Sample input files")
    print("│   ├── sample_posts.json")
    print("│   └── sample_posts.csv")
    print("├── README.md          - Complete documentation")
    print("└── test_installation.py - Installation tester")
    print()
    
    print("🛡️ SAFETY FEATURES:")
    print("✅ Dry-run mode by default (test without posting)")
    print("✅ Smart rate limiting (stays under Reddit's limits)")
    print("✅ Random delays between posts (60-300 seconds)")
    print("✅ Comprehensive post validation")
    print("✅ Session limits (max 50 posts per session)")
    print("✅ Proper user agent (follows Reddit guidelines)")
    print("✅ Subreddit accessibility checks")
    print("✅ Detailed logging and error handling")
    print()
    
    print("🖥️ USER INTERFACES:")
    print("1. 🌐 Modern Web Interface (Gradio)")
    print("   - Beautiful, intuitive design")
    print("   - Real-time progress tracking")
    print("   - File upload support")
    print("   - Interactive validation")
    print()
    print("2. 💻 Command Line Interface")
    print("   - Full automation support")
    print("   - Scriptable operations")
    print("   - Batch processing")
    print("   - Advanced options")
    print()
    
    print("📝 INPUT FORMATS:")
    print("• JSON files - Structured data with full control")
    print("• CSV files - Spreadsheet-friendly format")
    print("• Manual input - Single posts via web interface")
    print("• Command line - Direct CLI arguments")
    print()

def show_usage_examples():
    """Show usage examples"""
    print("🚀 QUICK START GUIDE:")
    print("=" * 60)
    print()
    
    print("1️⃣ LAUNCH WEB INTERFACE (Recommended for beginners):")
    print("   python3 reddit_poster.py --gui")
    print("   → Opens http://localhost:7860 in your browser")
    print("   → Beautiful interface with guided setup")
    print()
    
    print("2️⃣ CREATE SAMPLE FILES:")
    print("   python3 reddit_poster.py --create-samples")
    print("   → Creates examples/sample_posts.json and .csv")
    print()
    
    print("3️⃣ TEST WITH DRY-RUN (Always do this first!):")
    print("   python3 reddit_poster.py --file examples/sample_posts.json --dry-run")
    print("   → Simulates posting without actually submitting")
    print()
    
    print("4️⃣ LIVE POSTING (After testing):")
    print("   python3 reddit_poster.py --file examples/sample_posts.json --live")
    print("   → Actually submits posts to Reddit")
    print()
    
    print("🔧 ADVANCED COMMANDS:")
    print("• Custom delays:    python3 reddit_poster.py --file posts.json --delay 120")
    print("• Help & options:   python3 reddit_poster.py --help")
    print("• Different files:  python3 reddit_poster.py --file my_posts.csv")
    print()

def show_sample_data():
    """Show sample post data"""
    print("📋 SAMPLE POST DATA:")
    print("=" * 60)
    
    demo_post = create_demo_post()
    
    print("\n🔹 JSON Format:")
    print(json.dumps([demo_post], indent=2))
    
    print("\n🔹 CSV Format:")
    print("subreddit,title,content,flair,delay")
    print(f'"{demo_post["subreddit"]}","{demo_post["title"]}","{demo_post["content"][:50]}...","{ demo_post["flair"]}",{demo_post["delay"]}')
    print()

def show_safety_reminders():
    """Show important safety reminders"""
    print("⚠️ IMPORTANT SAFETY REMINDERS:")
    print("=" * 60)
    print()
    
    print("🛡️ ALWAYS START WITH DRY-RUN MODE:")
    print("   • Test your posts before going live")
    print("   • Verify subreddit names and accessibility")
    print("   • Check post formatting and content")
    print()
    
    print("⏱️ USE APPROPRIATE DELAYS:")
    print("   • Minimum: 60 seconds between posts")
    print("   • Recommended: 90-180 seconds")
    print("   • Random jitter is automatically added")
    print()
    
    print("📏 RESPECT LIMITS:")
    print("   • Max 50 posts per session")
    print("   • Max 50 API requests per minute")
    print("   • Take breaks between large batches")
    print()
    
    print("📜 FOLLOW REDDIT RULES:")
    print("   • Read and follow subreddit rules")
    print("   • Don't spam or post duplicate content")
    print("   • Respect community guidelines")
    print("   • Monitor your account for warnings")
    print()
    
    print("🔐 KEEP CREDENTIALS SECURE:")
    print("   • Never share your Reddit password")
    print("   • Keep your .env file private")
    print("   • Use strong, unique passwords")
    print()

def main():
    """Main demo function"""
    print("🎯 REDDIT POSTING TOOL - COMPLETE DEMO")
    print("=" * 80)
    print()
    
    show_tool_overview()
    show_usage_examples()
    show_sample_data()
    show_safety_reminders()
    
    print("🎉 YOU'RE ALL SET!")
    print("=" * 60)
    print()
    print("Your Reddit Posting Tool is ready to use!")
    print()
    print("🚀 Next Steps:")
    print("1. Run: python3 reddit_poster.py --gui")
    print("2. Enter your Reddit password in the web interface")
    print("3. Start with dry-run mode to test safely")
    print("4. Create your own posts or use the sample files")
    print("5. Monitor the logs and results")
    print()
    print("📚 Need help? Check README.md for detailed documentation!")
    print()
    print("Happy posting! 🎊")

if __name__ == "__main__":
    main()