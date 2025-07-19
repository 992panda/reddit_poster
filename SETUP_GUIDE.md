# 🚀 Reddit Posting Tool - Setup Guide for Any User

## 📋 **Quick Setup for New Users**

### **Step 1: Create Your Reddit App**

1. **Go to Reddit App Preferences:**
   - Visit: https://www.reddit.com/prefs/apps
   - Log in with your Reddit account

2. **Create New App:**
   - Click "Create App" or "Create Another App"
   - **Choose "script" as the app type** ⚠️ **IMPORTANT**
   - Fill in the form:
     - **Name:** `My Reddit Posting Tool`
     - **App type:** `script` ✅
     - **Description:** `Automated posting tool`
     - **About URL:** (leave blank)
     - **Redirect URI:** (leave blank for script apps)

3. **Get Your Credentials:**
   - After creating, you'll see your app
   - **Client ID:** The string under your app name (14 character string)
   - **Client Secret:** The "secret" field (longer string of characters)

### **Step 2: Configure Your .env File**

Edit the `.env` file with YOUR credentials:

```bash
CLIENT_ID=YOUR_CLIENT_ID_HERE
CLIENT_SECRET=YOUR_CLIENT_SECRET_HERE
REDDIT_USERNAME=YOUR_REDDIT_USERNAME
```

**Example:**
```bash
CLIENT_ID=your_actual_client_id
CLIENT_SECRET=your_actual_client_secret
REDDIT_USERNAME=YourRedditUsername
```

### **Step 3: Install Dependencies**

```bash
# Create virtual environment
python3 -m venv reddit_env

# Activate virtual environment
source reddit_env/bin/activate  # On Windows: reddit_env\Scripts\activate

# Install packages
pip install praw python-dotenv pandas gradio colorama
```

### **Step 4: Launch the Tool**

```bash
# Make sure virtual environment is activated
source reddit_env/bin/activate

# Launch web interface
python3 reddit_poster.py --gui
```

### **Step 5: Use the Tool**

1. **Open your browser:** http://localhost:7860
2. **Enter your Reddit password** (the same one you use to log into reddit.com)
3. **Keep "Dry Run Mode" enabled** for testing
4. **Create your first post** safely!

## 🔧 **For Different Users**

### **User A Setup:**
```bash
# .env file for User A
CLIENT_ID=user_a_client_id
CLIENT_SECRET=user_a_client_secret
REDDIT_USERNAME=UserA_RedditName
```

### **User B Setup:**
```bash
# .env file for User B  
CLIENT_ID=user_b_client_id
CLIENT_SECRET=user_b_client_secret
REDDIT_USERNAME=UserB_RedditName
```

## 🛡️ **Security Notes**

- ✅ **Each user needs their own Reddit app** (takes 2 minutes to create)
- ✅ **Never share your .env file** - it contains your API credentials
- ✅ **Password is never stored** - only used for authentication
- ✅ **Always test with dry-run mode first**

## 🚨 **Important Reddit App Settings**

**❌ WRONG App Type:**
- Web Application
- Installed App

**✅ CORRECT App Type:**
- **Script** ← This is what you need!

## 📞 **Need Help?**

1. **Can't create Reddit app?** Make sure you're logged into Reddit
2. **Authentication fails?** Double-check your CLIENT_ID and CLIENT_SECRET
3. **Username not showing?** Check your REDDIT_USERNAME in .env
4. **Tool won't start?** Make sure virtual environment is activated

## 🎯 **Quick Test**

After setup, test with this simple post:

```json
{
  "subreddit": "test",
  "title": "Testing My Reddit Posting Tool",
  "content": "This is a test post. Please ignore!",
  "delay": 90
}
```

**Remember:** Always start with dry-run mode! 🛡️

---

**Happy Posting! 🚀**