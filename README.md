# 🚀 Reddit Posting Tool

**Professional Reddit automation with enterprise-grade safety features**

A comprehensive, secure Reddit posting tool designed for content creators, marketers, and community managers. Features both a beautiful web interface and powerful CLI, with advanced anti-ban mechanisms and intelligent flair handling.

![Reddit Posting Tool](https://img.shields.io/badge/Reddit-API-orange?style=for-the-badge&logo=reddit)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Gradio](https://img.shields.io/badge/Gradio-Web%20UI-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-Educational-yellow?style=for-the-badge)

---

## ✨ Advanced Features

### 🛡️ Enterprise-Grade Safety & Anti-Ban System
- **🔒 Dry-run mode by default** - Test everything safely before going live
- **⚡ Smart rate limiting** - Stays under Reddit's 60 req/min limit automatically
- **🎲 Dynamic delays** - User-controlled timing (1-300+ seconds) with intelligent spacing
- **✅ Comprehensive validation** - Multi-layer post validation before submission
- **📊 Session limits** - Prevents account flagging with built-in posting limits
- **🤖 Proper user agent** - Follows Reddit API guidelines to avoid detection
- **🔍 Subreddit verification** - Checks accessibility and rules before posting

### 📝 Advanced Posting Capabilities
- **📄 Multiple post types** - Text posts, link posts, and direct image uploads
- **📁 Batch processing** - Upload CSV/JSON files for automated posting
- **🏷️ Intelligent flair handling** - Automatic flair ID resolution and fallback
- **🖼️ Direct image uploads** - Bypass domain restrictions with Reddit-hosted images
- **⏱️ Custom scheduling** - Individual delays per post for optimal timing
- **🎯 Multi-subreddit support** - Post to different subreddits with different settings

### 🖥️ Dual Interface System
- **🌐 Modern Web UI** - Beautiful Gradio interface with real-time feedback
- **💻 Powerful CLI** - Full command-line support for automation and scripting
- **📋 Subreddit rules checker** - Built-in tool to check posting requirements
- **🔧 Interactive configuration** - Easy setup for any user

### 📊 Enterprise-Grade Monitoring
- **📈 Real-time progress tracking** - Live updates during batch operations
- **📝 Detailed logging system** - Comprehensive logs with timestamps and status
- **📊 Success analytics** - Monitor success/failure rates with detailed reporting
- **💾 Export capabilities** - Save results to JSON/CSV for analysis
- **🚨 Error handling** - Graceful error recovery with detailed error messages

---

## 🚀 Quick Start

### 1. Automated Setup (Recommended)

```bash
# Run the interactive setup script
python3 setup_user.py
```

This will guide you through:
- Creating your Reddit app
- Configuring your credentials  
- Setting up everything automatically

### 2. Manual Installation

```bash
# Install dependencies
pip3 install praw python-dotenv pandas gradio colorama

# Or use requirements file
pip3 install -r requirements.txt
```

### 3. Setup Reddit API Credentials

#### **Option A: Use Setup Script (Easy)**
```bash
python3 setup_user.py
```

#### **Option B: Manual Setup**

1. **Create Reddit App**:
   - Go to https://www.reddit.com/prefs/apps
   - Click "Create App" or "Create Another App"  
   - **⚠️ IMPORTANT: Choose "script" as the app type**
   - Note down your `client_id` and `client_secret`

2. **Configure Environment**:
   Create/edit your `.env` file:
   ```bash
   CLIENT_ID=YOUR_CLIENT_ID_HERE
   CLIENT_SECRET=YOUR_CLIENT_SECRET_HERE
   REDDIT_USERNAME=YOUR_REDDIT_USERNAME
   ```

   **Example:**
   ```bash
   CLIENT_ID=your_client_id
   CLIENT_SECRET=your_client_secret
   REDDIT_USERNAME=YourUsername
   ```

### 4. Launch the Tool

#### 🌐 Web Interface (Recommended)
```bash
python3 reddit_poster.py --gui
```
- **Auto-opens browser** at http://localhost:7860
- **Beautiful interface** with guided setup
- **Real-time feedback** and progress tracking
- **Built-in rules checker** for subreddits

#### 💻 Command Line Interface
```bash
# Create sample files
python3 reddit_poster.py --create-samples

# Test safely with dry-run
python3 reddit_poster.py --file examples/sample_posts.json --dry-run

# Live posting (after testing)
python3 reddit_poster.py --file examples/sample_posts.json --live

# Custom delays
python3 reddit_poster.py --file posts.csv --delay 120

# Get help
python3 reddit_poster.py --help
```

---

## 📋 Advanced Input Formats

### 🎯 Smart CSV Format (Recommended)
```csv
subreddit,title,content,flair,delay,image_path
test,"Text Post","This is a text post","Discussion",60,
cats,"Link Post","https://youtube.com/watch?v=abc","Video",90,
aww,"Image Post","","Photo",120,/path/to/cute_cat.jpg
```

### 📄 JSON Format
```json
[
  {
    "subreddit": "cats",
    "title": "Cute Cat Video", 
    "content": "https://youtube.com/watch?v=abc123",
    "flair": "Video - Not OC",
    "delay": 90
  },
  {
    "subreddit": "aww",
    "title": "My Cat Photo",
    "content": "",
    "flair": "Photo - OC", 
    "delay": 120,
    "image_path": "/home/user/cat.jpg"
  }
]
```

### 🖼️ Image Upload Support
```csv
subreddit,title,content,flair,delay,image_path
cats,"Direct Upload","","Photo - OC",90,/path/to/image.jpg
aww,"Cute Kitten","","",120,/home/user/kitten.png
```

**Supported formats:** `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`

---

## 🛡️ Advanced Safety System

### 🔒 Always Start with Dry-Run
```bash
# Test everything safely first
python3 reddit_poster.py --file your_posts.csv --dry-run
```

### ⚙️ Intelligent Safety Settings
- **🎯 Dynamic delays**: 1-300+ seconds (user-controlled)
- **📊 Smart batching**: Automatic session limits
- **⏰ Optimal timing**: Avoid Reddit's peak detection hours
- **✅ Content validation**: Multi-layer checks before posting

### 🚫 Anti-Ban Best Practices

#### **Timing Strategy:**
- ✅ **Minimum 30-60 seconds** between posts
- ✅ **Vary delays** per subreddit (strict subs = longer delays)
- ✅ **Random jitter** for natural patterns
- ✅ **Respect rate limits** (auto-managed)

#### **Content Strategy:**
- ✅ **Unique content** per post
- ✅ **Subreddit-appropriate** material
- ✅ **Proper flairs** (auto-detected)
- ✅ **Domain compliance** (whitelist checking)

#### **Account Safety:**
- ✅ **Start small** (5-10 posts max initially)
- ✅ **Monitor results** (check for shadowbans)
- ✅ **Use approved domains** (imgur, youtube, etc.)
- ✅ **Follow community rules** (built-in checker)

---

## 🌐 Web Interface Guide

### 🔐 Authentication & Setup
1. **Enter Reddit password** in the authentication section
2. **Click "🔑 Authenticate"** to connect securely
3. **Keep "Dry Run Mode" enabled** for safe testing
4. **See your username** displayed in the interface

### 📝 Single Post Tab
1. **Enter subreddit name** (without r/)
2. **Click "📋 Get Subreddit Rules"** to check requirements
3. **Fill in title and content** (or image path)
4. **Select appropriate flair** from the rules checker
5. **Click "✅ Validate Post"** to check for errors
6. **Click "🚀 Submit Post"** to post safely

### 📁 Batch Upload Tab
1. **Upload CSV/JSON file** with your posts
2. **Click "📋 Process File"** to validate data
3. **Review posts preview** table
4. **Edit JSON data** if needed
5. **Click "🚀 Submit Batch"** with progress tracking

### 📚 Built-in Tools
- **📋 Subreddit Rules Checker** - See posting requirements
- **🏷️ Flair Detection** - Find available flairs
- **🔗 Domain Whitelist** - Check approved domains
- **📊 Real-time Results** - Monitor success/failure rates

---

## 💻 Command Line Usage

### Basic Commands
```bash
# Launch web interface
python3 reddit_poster.py --gui

# Post from file (dry-run)
python3 reddit_poster.py --file posts.json

# Post from file (live)
python3 reddit_poster.py --file posts.json --live

# Create sample files
python3 reddit_poster.py --create-samples

# Custom delay
python3 reddit_poster.py --file posts.json --delay 120
```

### Advanced Options
```bash
# Full help
python3 reddit_poster.py --help

# Different file formats
python3 reddit_poster.py --file posts.csv
python3 reddit_poster.py --file posts.json

# Test installation
python3 test_installation.py

# Interactive setup
python3 setup_user.py
```

---

## 🚨 Advanced Troubleshooting

### 🔧 Common Issues & Solutions

#### **Authentication Problems**
```bash
❌ Error: "invalid_grant" 
✅ Solution: Check Reddit password and app type (must be "script")

❌ Error: "Authentication failed"
✅ Solution: Verify CLIENT_ID and CLIENT_SECRET in .env file
```

#### **Posting Failures**
```bash
❌ Error: "SUBMIT_VALIDATION_FLAIR_REQUIRED"
✅ Solution: Use "📋 Get Subreddit Rules" to find required flairs

❌ Error: "SUBMIT_VALIDATION_LINK_WHITELIST" 
✅ Solution: Use approved domains (imgur, youtube) or direct image upload

❌ Error: "received 404 HTTP response"
✅ Solution: Check subreddit name spelling and accessibility
```

#### **Performance Issues**
```bash
❌ Issue: Posts too slow
✅ Solution: Reduce delays in CSV (minimum 30 seconds recommended)

❌ Issue: Rate limited
✅ Solution: Increase delays, reduce batch size, or wait before retrying

❌ Issue: Port already in use
✅ Solution: Tool auto-tries ports 7860-7864, or kill existing processes
```

### 🔍 Error Messages Explained

#### **Reddit's Filters**
```
"Sorry, this post was removed by Reddit's filters"
```
- **Cause**: Site-wide spam detection
- **Solution**: Change URL domain or use direct image upload

#### **Domain Whitelist**
```
"The link must be from one of the approved domains"
```
- **Cause**: Subreddit only allows specific domains
- **Solution**: Use approved domains or direct image upload

#### **Flair Required**
```
"Your post must contain post flair"
```
- **Cause**: Subreddit requires flair selection
- **Solution**: Use rules checker to find available flairs

---

## 🎯 Advanced Features

### 🏷️ Intelligent Flair System
- **Auto-detection** of subreddit flairs
- **Exact and partial matching** for flair names
- **Fallback handling** for unsupported flairs
- **URL-encoded flair support** (e.g., "Video - Not OC")

### 📊 Comprehensive Analytics
- **Success/failure tracking** per subreddit
- **Detailed error reporting** with specific Reddit error codes
- **Performance metrics** and timing analysis
- **Export capabilities** for further analysis

### 🔧 Developer Features
- **Modular architecture** with clean separation of concerns
- **Comprehensive logging** with multiple log levels
- **Error recovery** and graceful degradation
- **Extensible design** for custom integrations

---

## 📁 Project Structure

```
reddit-posting-tool/
├── reddit_poster.py      # Main application (CLI + Web UI)
├── config.py            # Configuration management
├── utils.py             # Utility functions and safety features
├── setup_user.py        # Interactive user setup
├── test_installation.py # Installation verification
├── demo.py              # Feature demonstration
├── requirements.txt     # Python dependencies
├── .env                # Reddit API credentials (user-created)
├── examples/           # Sample input files
│   ├── sample_posts.json
│   ├── sample_posts.csv
│   └── sample_posts_with_images.csv
├── README.md           # This documentation
├── SETUP_GUIDE.md      # Detailed setup instructions
├── INSTALLATION.md     # Installation guide
└── reddit_poster.log   # Application logs (auto-generated)
```

---

## 🔧 Configuration

### Environment Variables (.env)
```bash
CLIENT_ID=YOUR_REDDIT_CLIENT_ID
CLIENT_SECRET=YOUR_REDDIT_CLIENT_SECRET
REDDIT_USERNAME=YOUR_REDDIT_USERNAME
```

### Safety Settings (config.py)
```python
MIN_DELAY = 30          # Minimum delay between posts
MAX_DELAY = 300         # Maximum delay between posts
DEFAULT_DELAY = 90      # Default delay
MAX_REQUESTS_PER_MINUTE = 50  # Rate limit
MAX_POSTS_PER_SESSION = 50    # Session limit
```

---

## 🤝 Contributing

This tool is designed for educational purposes and legitimate Reddit automation. Contributions that improve safety, usability, or documentation are welcome.

### 🛡️ Safety First
- All contributions must maintain or improve anti-ban features
- New features should include appropriate safety checks
- Documentation updates should emphasize responsible usage

---

## 📄 License & Disclaimer

**Educational Use Only** - This tool is provided for educational and legitimate automation purposes. 

### ⚠️ Important Disclaimers:
1. **Use Responsibly** - Don't spam or violate Reddit's terms of service
2. **Test First** - Always use dry-run mode before live posting  
3. **Follow Rules** - Respect subreddit rules and Reddit's content policy
4. **Monitor Account** - Watch for warnings or restrictions
5. **No Guarantees** - Use at your own risk

### 🎯 Legitimate Use Cases:
- ✅ Content creators managing multiple communities
- ✅ Businesses with approved promotional content
- ✅ Community managers with proper permissions
- ✅ Educational research and automation learning

---

## 🚀 **Ready to Start?**

```bash
# Quick start in 3 commands:
python3 setup_user.py          # Configure credentials
python3 reddit_poster.py --gui # Launch web interface  
# Start posting safely! 🎉
```

**Happy Posting! 🚀**

*Remember: Always test with dry-run mode first, and use this tool responsibly to maintain a healthy Reddit community.*