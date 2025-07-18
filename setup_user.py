#!/usr/bin/env python3
"""
User Setup Script for Reddit Posting Tool
Helps new users configure their credentials easily
"""

import os
import sys
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def create_env_file():
    """Interactive setup for .env file"""
    print(f"{Fore.CYAN}🚀 Reddit Posting Tool - User Setup{Style.RESET_ALL}")
    print("=" * 60)
    print()
    
    print(f"{Fore.YELLOW}📋 First, you need to create a Reddit app:{Style.RESET_ALL}")
    print("1. Go to: https://www.reddit.com/prefs/apps")
    print("2. Click 'Create App' or 'Create Another App'")
    print("3. Choose 'script' as the app type")
    print("4. Fill in any name and description")
    print("5. Leave redirect URI blank")
    print()
    
    input(f"{Fore.GREEN}Press Enter when you've created your Reddit app...{Style.RESET_ALL}")
    print()
    
    # Get user inputs
    print(f"{Fore.BLUE}🔧 Now let's configure your credentials:{Style.RESET_ALL}")
    print()
    
    client_id = input("Enter your CLIENT_ID (from Reddit app): ").strip()
    while not client_id:
        print(f"{Fore.RED}❌ CLIENT_ID cannot be empty!{Style.RESET_ALL}")
        client_id = input("Enter your CLIENT_ID: ").strip()
    
    client_secret = input("Enter your CLIENT_SECRET (from Reddit app): ").strip()
    while not client_secret:
        print(f"{Fore.RED}❌ CLIENT_SECRET cannot be empty!{Style.RESET_ALL}")
        client_secret = input("Enter your CLIENT_SECRET: ").strip()
    
    username = input("Enter your Reddit USERNAME (without u/): ").strip()
    while not username:
        print(f"{Fore.RED}❌ USERNAME cannot be empty!{Style.RESET_ALL}")
        username = input("Enter your Reddit USERNAME: ").strip()
    
    # Remove u/ prefix if user added it
    if username.startswith('u/'):
        username = username[2:]
    
    # Create .env file
    env_content = f"""CLIENT_ID={client_id}
CLIENT_SECRET={client_secret}
REDDIT_USERNAME={username}
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print()
        print(f"{Fore.GREEN}✅ Configuration saved successfully!{Style.RESET_ALL}")
        print()
        print(f"{Fore.CYAN}📁 Your .env file contains:{Style.RESET_ALL}")
        print(f"   CLIENT_ID={client_id}")
        print(f"   CLIENT_SECRET={client_secret[:8]}...")
        print(f"   REDDIT_USERNAME={username}")
        print()
        
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error saving configuration: {e}{Style.RESET_ALL}")
        return False

def check_existing_config():
    """Check if .env file already exists"""
    if os.path.exists('.env'):
        print(f"{Fore.YELLOW}⚠️ .env file already exists!{Style.RESET_ALL}")
        print()
        
        # Try to read existing config
        try:
            with open('.env', 'r') as f:
                content = f.read()
            
            print("Current configuration:")
            for line in content.strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    if 'SECRET' in key:
                        print(f"   {key}={value[:8]}...")
                    else:
                        print(f"   {line}")
            print()
            
            response = input("Do you want to overwrite it? (y/N): ").strip().lower()
            return response == 'y'
            
        except Exception as e:
            print(f"Error reading existing .env: {e}")
            response = input("Do you want to create a new one? (y/N): ").strip().lower()
            return response == 'y'
    
    return True

def show_next_steps():
    """Show what to do next"""
    print(f"{Fore.CYAN}🚀 Next Steps:{Style.RESET_ALL}")
    print("1. Install dependencies:")
    print("   pip install praw python-dotenv pandas gradio colorama")
    print()
    print("2. Launch the tool:")
    print("   python3 reddit_poster.py --gui")
    print()
    print("3. Open your browser:")
    print("   http://localhost:7860")
    print()
    print("4. Enter your Reddit password in the web interface")
    print("5. Keep 'Dry Run Mode' enabled for testing")
    print()
    print(f"{Fore.GREEN}🎉 You're all set! Happy posting!{Style.RESET_ALL}")

def main():
    """Main setup function"""
    try:
        if check_existing_config():
            if create_env_file():
                print()
                show_next_steps()
            else:
                print(f"{Fore.RED}❌ Setup failed. Please try again.{Style.RESET_ALL}")
        else:
            print(f"{Fore.BLUE}ℹ️ Setup cancelled. Using existing configuration.{Style.RESET_ALL}")
            print()
            show_next_steps()
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️ Setup cancelled by user.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()