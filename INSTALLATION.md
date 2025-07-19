# 🚀 Reddit Posting Tool - Installation Guide

## 🎯 **Super Quick Setup for New Users**

### Option 1: Automated Setup (Recommended)
```bash
# Run the setup script
python3 setup_user.py
```
This will guide you through:
- Creating your Reddit app
- Configuring your credentials
- Setting up everything automatically

### Option 2: Manual Setup

## 📦 Quick Installation

### Step 1: Install Python Dependencies
```bash
pip3 install praw python-dotenv pandas gradio colorama
```

Or install from requirements.txt:
```bash
pip3 install -r requirements.txt
```

### Step 2: Verify Installation
```bash
python3 test_installation.py
```

### Step 3: Launch the Tool
```bash
# Launch beautiful web interface
python3 reddit_poster.py --gui

# Or create sample files first
python3 reddit_poster.py --create-samples
```

## 🔧 Configure Your .env File

Your `.env` file needs to be configured with your Reddit API credentials:
```
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here
REDDIT_USERNAME=your_reddit_username
```

⚠️ **Important:** You need to add your own Reddit API credentials to the .env file.

## 🚀 Ready to Use!

### Option 1: Web Interface (Recommended)
```bash
python3 reddit_poster.py --gui
```
- Opens http://localhost:7860
- Beautiful, user-friendly interface
- Real-time progress tracking
- File upload support

### Option 2: Command Line
```bash
# Create sample files
python3 reddit_poster.py --create-samples

# Test with dry-run (SAFE)
python3 reddit_poster.py --file examples/sample_posts.json --dry-run

# Live posting (after testing)
python3 reddit_poster.py --file examples/sample_posts.json --live
```

## 🛡️ Safety Features Built-In

✅ **Dry-run mode by default** - Test without posting
✅ **Smart rate limiting** - Stays under Reddit's API limits  
✅ **Random delays** - 60-300 seconds between posts
✅ **Post validation** - Checks before submission
✅ **Session limits** - Max 50 posts per session
✅ **Proper user agent** - Follows Reddit guidelines
✅ **Comprehensive logging** - Track everything

## 📝 What You Can Do

### Single Posts
- Submit individual posts with full control
- Real-time validation
- Custom delays and flair

### Batch Posting  
- Upload JSON or CSV files
- Process multiple posts automatically
- Progress tracking and results

### File Formats Supported
- **JSON**: Structured data with full control
- **CSV**: Spreadsheet-friendly format

## ⚠️ Important Safety Notes

1. **Always start with dry-run mode** to test safely
2. **Use appropriate delays** (60-180 seconds between posts)
3. **Respect subreddit rules** and Reddit's terms of service
4. **Monitor your account** for any warnings
5. **Keep credentials secure** - never share your password

## 🎯 Quick Start Workflow

1. **Install dependencies**: `pip3 install -r requirements.txt`
2. **Launch web interface**: `python3 reddit_poster.py --gui`
3. **Enter your Reddit password** in the authentication section
4. **Keep dry-run mode enabled** for testing
5. **Create a test post** or upload sample files
6. **Validate and submit** your posts safely

## 🔍 Troubleshooting

### If packages fail to install:
```bash
# Try with --user flag
pip3 install --user praw python-dotenv pandas gradio colorama

# Or use virtual environment
python3 -m venv reddit_env
source reddit_env/bin/activate  # On Windows: reddit_env\Scripts\activate
pip install -r requirements.txt
```

### If authentication fails:
- Verify your Reddit app is set to "script" type
- Check that your client_id and client_secret are correct
- Ensure your Reddit password is correct

## 🎉 You're All Set!

Your Reddit Posting Tool is ready to use with:
- ✅ Complete safety features
- ✅ Beautiful web interface  
- ✅ Command line support
- ✅ Comprehensive documentation
- ✅ Sample files and examples

**Happy posting! 🚀**