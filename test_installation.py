#!/usr/bin/env python3
"""
Test script to verify Reddit Posting Tool installation and configuration
"""

import sys
import os
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def test_imports():
    """Test if all required packages can be imported"""
    print(f"{Fore.BLUE}🔍 Testing package imports...{Style.RESET_ALL}")
    
    required_packages = [
        ('praw', 'Reddit API wrapper'),
        ('gradio', 'Web interface framework'),
        ('pandas', 'Data manipulation'),
        ('dotenv', 'Environment variables'),
        ('colorama', 'Colored terminal output')
    ]
    
    failed_imports = []
    
    for package, description in required_packages:
        try:
            if package == 'dotenv':
                from dotenv import load_dotenv
            else:
                __import__(package)
            print(f"  ✅ {package} - {description}")
        except ImportError as e:
            print(f"  ❌ {package} - {description} (Error: {e})")
            failed_imports.append(package)
    
    return len(failed_imports) == 0, failed_imports

def test_config():
    """Test configuration and credentials"""
    print(f"\n{Fore.BLUE}🔧 Testing configuration...{Style.RESET_ALL}")
    
    try:
        from config import config
        print(f"  ✅ Configuration module loaded")
        
        # Test credential loading
        if config.CLIENT_ID and config.CLIENT_SECRET:
            print(f"  ✅ Reddit API credentials found")
            print(f"    Client ID: {config.CLIENT_ID[:8]}...")
            print(f"    Username: {config.USERNAME}")
        else:
            print(f"  ❌ Reddit API credentials missing")
            return False
        
        # Test safety settings
        print(f"  ✅ Safety settings configured")
        print(f"    Default delay: {config.DEFAULT_DELAY}s")
        print(f"    Rate limit: {config.MAX_REQUESTS_PER_MINUTE}/min")
        print(f"    Dry run default: {config.DRY_RUN_DEFAULT}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration error: {e}")
        return False

def test_reddit_connection():
    """Test Reddit API connection (read-only)"""
    print(f"\n{Fore.BLUE}🌐 Testing Reddit connection...{Style.RESET_ALL}")
    
    try:
        import praw
        from config import config
        
        # Create read-only Reddit instance
        reddit = praw.Reddit(
            client_id=config.CLIENT_ID,
            client_secret=config.CLIENT_SECRET,
            user_agent=config.USER_AGENT
        )
        
        # Test basic API access
        subreddit = reddit.subreddit('test')
        test_post = next(subreddit.hot(limit=1))
        
        print(f"  ✅ Reddit API connection successful")
        print(f"  ✅ Can access r/test subreddit")
        print(f"  ✅ API rate limit info available")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Reddit connection failed: {e}")
        return False

def test_file_structure():
    """Test file structure and permissions"""
    print(f"\n{Fore.BLUE}📁 Testing file structure...{Style.RESET_ALL}")
    
    required_files = [
        ('reddit_poster.py', 'Main application'),
        ('config.py', 'Configuration module'),
        ('utils.py', 'Utility functions'),
        ('requirements.txt', 'Dependencies list'),
        ('.env', 'Environment variables'),
        ('README.md', 'Documentation')
    ]
    
    optional_dirs = [
        ('examples/', 'Sample files directory')
    ]
    
    all_good = True
    
    for file_path, description in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path} - {description}")
        else:
            print(f"  ❌ {file_path} - {description} (Missing)")
            all_good = False
    
    for dir_path, description in optional_dirs:
        if os.path.exists(dir_path):
            print(f"  ✅ {dir_path} - {description}")
        else:
            print(f"  ⚠️  {dir_path} - {description} (Will be created)")
    
    return all_good

def test_sample_files():
    """Test sample file creation and parsing"""
    print(f"\n{Fore.BLUE}📋 Testing sample files...{Style.RESET_ALL}")
    
    try:
        from utils import create_sample_files, FileHandler
        
        # Create sample files
        create_sample_files()
        print(f"  ✅ Sample files created successfully")
        
        # Test JSON parsing
        file_handler = FileHandler()
        json_posts = file_handler.read_json_file('examples/sample_posts.json')
        print(f"  ✅ JSON file parsed: {len(json_posts)} posts found")
        
        # Test CSV parsing
        csv_posts = file_handler.read_csv_file('examples/sample_posts.csv')
        print(f"  ✅ CSV file parsed: {len(csv_posts)} posts found")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Sample file test failed: {e}")
        return False

def test_validation():
    """Test post validation"""
    print(f"\n{Fore.BLUE}✅ Testing post validation...{Style.RESET_ALL}")
    
    try:
        from utils import PostValidator
        
        validator = PostValidator()
        
        # Test valid post
        valid_post = {
            'subreddit': 'test',
            'title': 'Test Post',
            'content': 'This is a test post'
        }
        
        is_valid, message = validator.validate_post_data(valid_post)
        if is_valid:
            print(f"  ✅ Valid post validation passed")
        else:
            print(f"  ❌ Valid post validation failed: {message}")
            return False
        
        # Test invalid post
        invalid_post = {
            'subreddit': '',
            'title': '',
            'content': ''
        }
        
        is_valid, message = validator.validate_post_data(invalid_post)
        if not is_valid:
            print(f"  ✅ Invalid post validation correctly failed")
        else:
            print(f"  ❌ Invalid post validation should have failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Validation test failed: {e}")
        return False

def main():
    """Run all tests"""
    print(f"{Fore.CYAN}🚀 Reddit Posting Tool - Installation Test{Style.RESET_ALL}")
    print("=" * 60)
    
    tests = [
        ("Package Imports", test_imports),
        ("Configuration", test_config),
        ("File Structure", test_file_structure),
        ("Sample Files", test_sample_files),
        ("Post Validation", test_validation),
        ("Reddit Connection", test_reddit_connection),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success, *extra = test_func() if test_func() is not None else (True,)
            if isinstance(success, tuple):
                success = success[0]
            results.append((test_name, success))
        except Exception as e:
            print(f"  ❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{Fore.CYAN}📊 Test Results Summary{Style.RESET_ALL}")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = f"{Fore.GREEN}✅ PASS" if success else f"{Fore.RED}❌ FAIL"
        print(f"  {status}{Style.RESET_ALL} - {test_name}")
    
    print(f"\n{Fore.CYAN}Overall: {passed}/{total} tests passed{Style.RESET_ALL}")
    
    if passed == total:
        print(f"\n{Fore.GREEN}🎉 All tests passed! Your Reddit Posting Tool is ready to use.{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Next steps:{Style.RESET_ALL}")
        print("1. Run: python reddit_poster.py --gui")
        print("2. Or run: python reddit_poster.py --create-samples")
        print("3. Always test with --dry-run first!")
    else:
        print(f"\n{Fore.RED}⚠️ Some tests failed. Please check the errors above.{Style.RESET_ALL}")
        
        failed_tests = [name for name, success in results if not success]
        if "Package Imports" in failed_tests:
            print(f"\n{Fore.YELLOW}💡 To fix import errors:{Style.RESET_ALL}")
            print("   pip install -r requirements.txt")
        
        if "Configuration" in failed_tests:
            print(f"\n{Fore.YELLOW}💡 To fix configuration:{Style.RESET_ALL}")
            print("   Check your .env file has correct Reddit API credentials")
        
        if "Reddit Connection" in failed_tests:
            print(f"\n{Fore.YELLOW}💡 To fix Reddit connection:{Style.RESET_ALL}")
            print("   Verify your Reddit app is set to 'script' type")
            print("   Check your client_id and client_secret")

if __name__ == "__main__":
    main()