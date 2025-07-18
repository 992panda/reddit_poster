"""
Configuration management for Reddit Posting Tool
Handles environment variables, validation, and settings
"""

import os
import sys
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for Reddit API and application settings"""
    
    def __init__(self):
        self.load_reddit_credentials()
        self.setup_logging()
        self.setup_safety_settings()
    
    def load_reddit_credentials(self):
        """Load and validate Reddit API credentials"""
        self.CLIENT_ID = os.getenv('CLIENT_ID', '').strip()
        self.CLIENT_SECRET = os.getenv('CLIENT_SECRET', '').strip()
        self.USERNAME = os.getenv('REDDIT_USERNAME', '').strip()
        self.PASSWORD = None  # Will be set if provided
        
        # Validate required credentials
        if not self.CLIENT_ID or not self.CLIENT_SECRET:
            raise ValueError("Missing Reddit API credentials. Please check your .env file.")
        
        # User agent following Reddit guidelines
        self.USER_AGENT = f"RedditPoster/1.0 (by u/{self.USERNAME})"
    
    def setup_logging(self):
        """Configure logging settings"""
        self.LOG_LEVEL = logging.INFO
        self.LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
        self.LOG_FILE = 'reddit_poster.log'
    
    def setup_safety_settings(self):
        """Configure safety and anti-ban settings"""
        # Delay settings (in seconds)
        self.MIN_DELAY = 30  # Minimum delay between posts (reduced for user control)
        self.MAX_DELAY = 300  # Maximum delay between posts
        self.DEFAULT_DELAY = 90  # Default delay if not specified
        
        # Rate limiting
        self.MAX_REQUESTS_PER_MINUTE = 50  # Stay well under Reddit's 60/min limit
        self.REQUEST_WINDOW = 60  # Time window in seconds
        
        # Safety settings
        self.DRY_RUN_DEFAULT = True  # Always start in dry-run mode for safety
        self.MAX_POSTS_PER_SESSION = 50  # Limit posts per session
        self.REQUIRE_CONFIRMATION = True  # Require confirmation for batch operations
        
        # File settings
        self.SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        self.SUPPORTED_VIDEO_FORMATS = ['.mp4', '.mov', '.avi', '.webm']
        self.MAX_FILE_SIZE_MB = 100  # Maximum file size for uploads
    
    def validate_credentials(self):
        """Validate that all required credentials are present"""
        missing = []
        if not self.CLIENT_ID:
            missing.append("CLIENT_ID")
        if not self.CLIENT_SECRET:
            missing.append("CLIENT_SECRET")
        
        if missing:
            raise ValueError(f"Missing required credentials: {', '.join(missing)}")
        
        return True
    
    def get_reddit_config(self, password=None):
        """Get Reddit configuration dictionary for PRAW"""
        config = {
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET,
            'user_agent': self.USER_AGENT,
        }
        
        if password:
            config.update({
                'username': self.USERNAME,
                'password': password
            })
        
        return config

# Global config instance
config = Config()