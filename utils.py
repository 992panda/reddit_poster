"""
Utility functions for Reddit Posting Tool
Includes safety features, validation, and helper functions
"""

import time
import random
import logging
import json
import csv
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import os
import praw
from config import config

# Setup logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter to prevent API abuse"""
    
    def __init__(self, max_requests=50, window=60):
        self.max_requests = max_requests
        self.window = window
        self.requests = []
    
    def can_make_request(self):
        """Check if we can make a request without exceeding rate limits"""
        now = time.time()
        # Remove old requests outside the window
        self.requests = [req_time for req_time in self.requests if now - req_time < self.window]
        
        return len(self.requests) < self.max_requests
    
    def add_request(self):
        """Record a new request"""
        self.requests.append(time.time())
    
    def wait_if_needed(self):
        """Wait if necessary to respect rate limits"""
        if not self.can_make_request():
            wait_time = self.window - (time.time() - self.requests[0])
            logger.warning(f"Rate limit reached. Waiting {wait_time:.1f} seconds...")
            time.sleep(wait_time + 1)  # Add 1 second buffer

class PostValidator:
    """Validates posts before submission"""
    
    @staticmethod
    def validate_post_data(post_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate a single post's data"""
        # Check required fields
        if 'subreddit' not in post_data or not post_data['subreddit']:
            return False, "Missing required field: subreddit"
        
        if 'title' not in post_data or not post_data['title']:
            return False, "Missing required field: title"
        
        # For content, either 'content', 'url', or 'image_path' must be present
        has_content = post_data.get('content') and post_data['content'].strip()
        has_url = post_data.get('url') and post_data['url'].strip()
        has_image = post_data.get('image_path') and post_data['image_path'].strip()
        
        if not has_content and not has_url and not has_image:
            return False, "Missing required field: either 'content', 'url', or 'image_path' must be provided"
        
        # Validate image file if provided
        if has_image:
            image_path = post_data['image_path'].strip()
            if not os.path.exists(image_path):
                return False, f"Image file not found: {image_path}"
            
            # Check file extension
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            file_ext = os.path.splitext(image_path)[1].lower()
            if file_ext not in valid_extensions:
                return False, f"Invalid image format. Supported: {', '.join(valid_extensions)}"
        
        # Validate title length (Reddit limit is 300 characters)
        if len(post_data['title']) > 300:
            return False, "Title too long (max 300 characters)"
        
        # Validate content length (Reddit limit is 40,000 characters for text posts)
        if len(post_data['content']) > 40000:
            return False, "Content too long (max 40,000 characters)"
        
        # Validate subreddit name format
        subreddit = post_data['subreddit'].strip()
        if not subreddit.replace('_', '').replace('-', '').isalnum():
            return False, "Invalid subreddit name format"
        
        return True, "Valid"
    
    @staticmethod
    def validate_subreddit_exists(reddit: praw.Reddit, subreddit_name: str) -> Tuple[bool, str]:
        """Check if subreddit exists and is accessible"""
        try:
            subreddit = reddit.subreddit(subreddit_name)
            # Try to access subreddit info to check if it exists
            _ = subreddit.display_name
            _ = subreddit.subscribers  # This will fail if subreddit doesn't exist or is private
            return True, "Subreddit accessible"
        except Exception as e:
            return False, f"Subreddit not accessible: {str(e)}"
    
    @staticmethod
    def get_flair_id(subreddit, flair_text: str) -> Tuple[str, str]:
        """Get flair ID for given flair text - centralized flair handling"""
        if not flair_text or not flair_text.strip():
            return None, None
            
        flair_text = flair_text.strip()
        try:
            # Method 1: Try exact match
            for flair_template in subreddit.flair.link_templates:
                template_text = flair_template.get('flair_text', '')
                if template_text.lower() == flair_text.lower():
                    flair_id = flair_template.get('flair_template_id')
                    logger.info(f"Found exact flair template ID for '{flair_text}': {flair_id}")
                    return flair_id, None
            
            # Method 2: Try partial match
            for flair_template in subreddit.flair.link_templates:
                template_text = flair_template.get('flair_text', '')
                if flair_text.lower() in template_text.lower() or template_text.lower() in flair_text.lower():
                    flair_id = flair_template.get('flair_template_id')
                    logger.info(f"Found partial flair template match for '{flair_text}': {template_text} (ID: {flair_id})")
                    return flair_id, None
                    
        except Exception as e:
            logger.warning(f"Could not fetch flair templates: {e}")
        
        # Fallback to text
        logger.info(f"Using flair_text directly: '{flair_text}'")
        return None, flair_text
    
    @staticmethod
    def get_subreddit_rules(reddit: praw.Reddit, subreddit_name: str) -> Dict[str, Any]:
        """Get subreddit rules and posting requirements"""
        try:
            subreddit = reddit.subreddit(subreddit_name)
            
            rules_info = {
                'subreddit': subreddit_name,
                'display_name': subreddit.display_name,
                'title': subreddit.title,
                'description': subreddit.public_description,
                'subscribers': subreddit.subscribers,
                'rules': [],
                'submission_type': subreddit.submission_type,  # 'any', 'link', 'self'
                'allow_images': getattr(subreddit, 'allow_images', None),
                'allow_videos': getattr(subreddit, 'allow_videos', None),
                'allow_polls': getattr(subreddit, 'allow_polls', None),
                'allow_galleries': getattr(subreddit, 'allow_galleries', None),
                'link_flair_enabled': getattr(subreddit, 'link_flair_enabled', None),
                'spoilers_enabled': getattr(subreddit, 'spoilers_enabled', None),
                'over18': subreddit.over18,
                'quarantine': getattr(subreddit, 'quarantine', False),
                'domain_whitelist': [],
                'posting_requirements': {},
                'available_flairs': []
            }
            
            # Get rules
            try:
                for rule in subreddit.rules:
                    rule_data = {
                        'short_name': rule.short_name,
                        'description': rule.description,
                        'kind': rule.kind,  # 'comment', 'submission', 'all'
                        'violation_reason': rule.violation_reason,
                        'created_utc': rule.created_utc,
                        'priority': rule.priority
                    }
                    rules_info['rules'].append(rule_data)
            except Exception as e:
                logger.warning(f"Could not fetch rules for r/{subreddit_name}: {e}")
            
            # Try to get domain whitelist from rules or description
            description_text = (subreddit.description or '').lower()
            public_desc = (subreddit.public_description or '').lower()
            
            # Common domain patterns
            approved_domains = []
            domain_keywords = [
                'youtube.com', 'youtu.be', 'imgur.com', 'gfycat.com', 
                'streamable.com', 'vimeo.com', 'flickr.com', 'flic.kr',
                'pinimg.com', '500px.org', 'staticflickr.com', 'twimg.com',
                'reddit.com', 'redd.it', 'v.redd.it', 'i.redd.it'
            ]
            
            for domain in domain_keywords:
                if domain in description_text or domain in public_desc:
                    approved_domains.append(domain)
            
            rules_info['domain_whitelist'] = approved_domains
            
            # Posting requirements analysis
            requirements = {}
            
            # Check for karma requirements
            if 'karma' in description_text or 'karma' in public_desc:
                requirements['karma_required'] = True
            
            # Check for account age requirements
            if 'account age' in description_text or 'days old' in description_text:
                requirements['account_age_required'] = True
            
            # Check for verification requirements
            if 'verified' in description_text or 'verification' in description_text:
                requirements['verification_required'] = True
            
            rules_info['posting_requirements'] = requirements
            
            # Get available flairs - try multiple methods
            flair_list = []
            try:
                # Method 1: Try link templates
                for flair in subreddit.flair.link_templates:
                    flair_info = {
                        'text': flair.get('flair_text', ''),
                        'id': flair.get('flair_template_id', ''),
                        'css_class': flair.get('flair_css_class', ''),
                        'mod_only': flair.get('flair_mod_only', False),
                        'allowable_content': flair.get('allowable_content', 'all')
                    }
                    if flair_info['text']:  # Only add if has text
                        flair_list.append(flair_info)
            except Exception as e:
                logger.warning(f"Method 1 - Could not fetch link templates for r/{subreddit_name}: {e}")
                
                # Method 2: Try getting flairs from recent posts
                try:
                    logger.info(f"Trying method 2 for r/{subreddit_name} flairs...")
                    seen_flairs = set()
                    for submission in subreddit.hot(limit=50):
                        if hasattr(submission, 'link_flair_text') and submission.link_flair_text:
                            flair_text = submission.link_flair_text.strip()
                            if flair_text and flair_text not in seen_flairs:
                                seen_flairs.add(flair_text)
                                flair_list.append({
                                    'text': flair_text,
                                    'id': 'unknown',
                                    'css_class': getattr(submission, 'link_flair_css_class', ''),
                                    'mod_only': False,
                                    'allowable_content': 'all',
                                    'source': 'recent_posts'
                                })
                    logger.info(f"Found {len(flair_list)} flairs from recent posts")
                except Exception as e2:
                    logger.warning(f"Method 2 - Could not fetch flairs from posts for r/{subreddit_name}: {e2}")
            
            rules_info['available_flairs'] = flair_list
            
            return rules_info
            
        except Exception as e:
            logger.error(f"Error fetching subreddit rules for r/{subreddit_name}: {e}")
            return {
                'subreddit': subreddit_name,
                'error': str(e),
                'rules': [],
                'submission_type': 'unknown'
            }

class FileHandler:
    """Handles file operations for input data"""
    
    @staticmethod
    def read_json_file(file_path: str) -> List[Dict[str, Any]]:
        """Read posts from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Ensure data is a list
            if isinstance(data, dict):
                data = [data]
            
            return data
        except Exception as e:
            logger.error(f"Error reading JSON file {file_path}: {str(e)}")
            raise
    
    @staticmethod
    def read_csv_file(file_path: str) -> List[Dict[str, Any]]:
        """Read posts from CSV file"""
        try:
            df = pd.read_csv(file_path)
            posts = df.to_dict('records')
            
            # Process each post to handle URLs in content field
            for post in posts:
                content = post.get('content', '')
                
                # Check if content looks like a URL (only check strings)
                if content and isinstance(content, str) and (content.startswith('http://') or content.startswith('https://')):
                    # Move URL from content to url field
                    post['url'] = content
                    post['content'] = ''  # Clear content for link posts
                
                # Handle NaN values and convert delay to int
                for key, value in post.items():
                    if pd.isna(value):
                        post[key] = ''
                    elif key == 'delay' and value:
                        try:
                            post[key] = int(float(value))  # Convert delay to integer
                        except (ValueError, TypeError):
                            post[key] = config.DEFAULT_DELAY  # Use default if conversion fails
            
            return posts
        except Exception as e:
            logger.error(f"Error reading CSV file {file_path}: {str(e)}")
            raise
    
    @staticmethod
    def save_results_to_file(results: List[Dict[str, Any]], file_path: str):
        """Save posting results to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"posting_results_{timestamp}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"Results saved to {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
            raise

class SafetyManager:
    """Manages safety features and anti-ban mechanisms"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter(config.MAX_REQUESTS_PER_MINUTE, config.REQUEST_WINDOW)
        self.post_count = 0
        self.session_start = datetime.now()
    
    def get_random_delay(self, base_delay: Optional[int] = None) -> int:
        """Get a randomized delay to appear more natural"""
        if base_delay is None:
            base_delay = config.DEFAULT_DELAY
        
        # Add random jitter (±25% of base delay)
        jitter = random.uniform(-0.25, 0.25) * base_delay
        delay = int(base_delay + jitter)
        
        # Ensure delay is within acceptable bounds
        delay = max(config.MIN_DELAY, min(config.MAX_DELAY, delay))
        
        return delay
    
    def wait_between_posts(self, delay: Optional[int] = None):
        """Wait between posts with safety checks"""
        self.rate_limiter.wait_if_needed()
        
        # Use the exact delay provided, give users full control
        if delay is not None:
            actual_delay = max(1, delay)  # Only ensure it's at least 1 second
            logger.info(f"Using user-specified delay: {actual_delay} seconds")
        else:
            actual_delay = self.get_random_delay(delay)
            logger.info(f"Using default delay: {actual_delay} seconds")
        
        logger.info(f"Waiting {actual_delay} seconds before next action...")
        
        # Show countdown for user feedback
        for remaining in range(actual_delay, 0, -10):
            if remaining <= 10:
                time.sleep(remaining)
                break
            time.sleep(10)
            logger.info(f"  {remaining} seconds remaining...")
    
    def check_session_limits(self) -> Tuple[bool, str]:
        """Check if session limits are exceeded"""
        if self.post_count >= config.MAX_POSTS_PER_SESSION:
            return False, f"Session limit reached ({config.MAX_POSTS_PER_SESSION} posts)"
        
        session_duration = datetime.now() - self.session_start
        if session_duration > timedelta(hours=2):  # 2-hour session limit
            return False, "Session duration limit reached (2 hours)"
        
        return True, "Within limits"
    
    def increment_post_count(self):
        """Increment the post counter"""
        self.post_count += 1
        self.rate_limiter.add_request()

def create_sample_files():
    """Create sample input files for users"""
    
    # Create examples directory
    os.makedirs('examples', exist_ok=True)
    
    # Sample JSON file
    sample_json = [
        {
            "subreddit": "test",
            "title": "My First Automated Post",
            "content": "This is a test post created using the Reddit Posting Tool. Please ignore.",
            "flair": "Test",
            "delay": 90
        },
        {
            "subreddit": "test",
            "title": "Another Test Post",
            "content": "This is another test post. The tool supports multiple posts with different delays.",
            "delay": 120
        }
    ]
    
    with open('examples/sample_posts.json', 'w', encoding='utf-8') as f:
        json.dump(sample_json, f, indent=2)
    
    # Sample CSV file
    sample_csv_data = [
        ["subreddit", "title", "content", "flair", "delay"],
        ["test", "CSV Test Post 1", "This post was created from a CSV file.", "Test", "90"],
        ["test", "CSV Test Post 2", "Another CSV post with different timing.", "Discussion", "120"]
    ]
    
    with open('examples/sample_posts.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(sample_csv_data)
    
    logger.info("Sample files created in 'examples/' directory")

def format_results_for_display(results: List[Dict[str, Any]]) -> str:
    """Format results for console display"""
    if not results:
        return "No results to display."
    
    output = []
    output.append("=" * 80)
    output.append("POSTING RESULTS SUMMARY")
    output.append("=" * 80)
    
    successful = sum(1 for r in results if r.get('success', False))
    total = len(results)
    
    output.append(f"Total Posts: {total}")
    output.append(f"Successful: {successful}")
    output.append(f"Failed: {total - successful}")
    output.append(f"Success Rate: {(successful/total)*100:.1f}%")
    output.append("")
    
    for i, result in enumerate(results, 1):
        status = "✓ SUCCESS" if result.get('success', False) else "✗ FAILED"
        output.append(f"{i}. {status} - r/{result.get('subreddit', 'unknown')}")
        output.append(f"   Title: {result.get('title', 'N/A')[:60]}...")
        if not result.get('success', False):
            output.append(f"   Error: {result.get('error', 'Unknown error')}")
        output.append("")
    
    return "\n".join(output)

# Initialize sample files on import
if __name__ == "__main__":
    create_sample_files()