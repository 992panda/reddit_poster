"""
Reddit Posting Tool - Main Application
Supports both CLI and Gradio web interface
Includes comprehensive safety features and anti-ban mechanisms
"""

import argparse
import sys
import time
import json
import os
import signal
import atexit
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import logging

import praw
import gradio as gr
import pandas as pd
from colorama import init, Fore, Style

from config import config
from utils import (
    RateLimiter, PostValidator, FileHandler, SafetyManager,
    create_sample_files, format_results_for_display
)

# Initialize colorama for colored console output
init(autoreset=True)

# Setup logging
logger = logging.getLogger(__name__)

class RedditPoster:
    """Main Reddit posting class with safety features"""
    
    def __init__(self, password: Optional[str] = None, dry_run: bool = True):
        self.dry_run = dry_run
        self.safety_manager = SafetyManager()
        self.validator = PostValidator()
        self.file_handler = FileHandler()
        self.reddit = None
        self.results = []
        
        if password:
            self.initialize_reddit(password)
    
    def initialize_reddit(self, password: str) -> Tuple[bool, str]:
        """Initialize Reddit connection with authentication"""
        try:
            reddit_config = config.get_reddit_config(password)
            self.reddit = praw.Reddit(**reddit_config)
            
            # Test authentication
            user = self.reddit.user.me()
            if user is None:
                return False, "Authentication failed - unable to get user info"
            
            logger.info(f"Successfully authenticated as u/{user.name}")
            return True, f"Authenticated as u/{user.name}"
            
        except Exception as e:
            error_msg = f"Reddit authentication failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def validate_post_batch(self, posts: List[Dict[str, Any]]) -> Tuple[List[Dict], List[str]]:
        """Validate a batch of posts"""
        valid_posts = []
        errors = []
        
        for i, post in enumerate(posts):
            is_valid, message = self.validator.validate_post_data(post)
            if is_valid:
                valid_posts.append(post)
            else:
                errors.append(f"Post {i+1}: {message}")
        
        return valid_posts, errors
    
    def check_subreddit_access(self, subreddit_name: str) -> Tuple[bool, str]:
        """Check if subreddit is accessible - wrapper for validator"""
        if not self.reddit:
            return False, "Reddit not initialized"
        return self.validator.validate_subreddit_exists(self.reddit, subreddit_name)
    
    def submit_single_post(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a single post to Reddit"""
        result = {
            'subreddit': post_data.get('subreddit', ''),
            'title': post_data.get('title', ''),
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'error': None,
            'post_url': None,
            'dry_run': self.dry_run
        }
        
        try:
            logger.info(f"🚀 Attempting to post: r/{post_data.get('subreddit')} - {post_data.get('title', '')[:50]}...")
            
            # Safety checks
            can_continue, limit_msg = self.safety_manager.check_session_limits()
            if not can_continue:
                result['error'] = limit_msg
                logger.warning(f"⚠️ Session limit reached: {limit_msg}")
                return result
            
            # Validate post data
            is_valid, validation_msg = self.validator.validate_post_data(post_data)
            if not is_valid:
                result['error'] = f"Validation failed: {validation_msg}"
                logger.warning(f"⚠️ Validation failed: {validation_msg}")
                return result
            
            # Check subreddit access
            if not self.dry_run:
                logger.info(f"🔍 Checking subreddit access for r/{post_data['subreddit']}...")
                subreddit_ok, subreddit_msg = self.check_subreddit_access(post_data['subreddit'])
                if not subreddit_ok:
                    result['error'] = f"Subreddit check failed: {subreddit_msg}"
                    logger.warning(f"⚠️ Subreddit access failed: {subreddit_msg}")
                    return result
            
            if self.dry_run:
                # Simulate posting in dry-run mode
                logger.info(f"[DRY RUN] Would post to r/{post_data['subreddit']}: {post_data['title']}")
                result['success'] = True
                result['post_url'] = f"https://reddit.com/r/{post_data['subreddit']}/posts/dry_run_simulation"
            else:
                # Actually submit the post
                subreddit = self.reddit.subreddit(post_data['subreddit'])
                
                # Handle flair using centralized function
                flair_id, flair_text = self.validator.get_flair_id(subreddit, post_data.get('flair'))
                
                # Determine post type and submit with flair handling
                submit_kwargs = {
                    'title': post_data['title']
                }
                
                # Add flair parameters - try both methods for compatibility
                if flair_id:
                    submit_kwargs['flair_id'] = flair_id
                elif flair_text:
                    submit_kwargs['flair_text'] = flair_text
                
                if 'image_path' in post_data and post_data['image_path'] and os.path.exists(post_data['image_path']):
                    # Image upload post
                    submit_kwargs['image_path'] = post_data['image_path']
                    submission = subreddit.submit_image(**submit_kwargs)
                elif 'url' in post_data and post_data['url'] and post_data['url'].strip():
                    # Link post
                    submit_kwargs['url'] = post_data['url'].strip()
                    submission = subreddit.submit(**submit_kwargs)
                else:
                    # Text post
                    submit_kwargs['selftext'] = post_data.get('content', '')
                    submission = subreddit.submit(**submit_kwargs)
                
                result['success'] = True
                result['post_url'] = f"https://reddit.com{submission.permalink}"
                result['post_id'] = submission.id
                
                logger.info(f"Successfully posted to r/{post_data['subreddit']}: {submission.permalink}")
                self.safety_manager.increment_post_count()
            
        except Exception as e:
            error_msg = str(e)
            result['error'] = error_msg
            logger.error(f"Failed to post to r/{post_data.get('subreddit', 'unknown')}: {error_msg}")
        
        return result
    
    def submit_post_batch(self, posts: List[Dict[str, Any]], progress_callback=None) -> List[Dict[str, Any]]:
        """Submit a batch of posts with safety delays"""
        results = []
        total_posts = len(posts)
        
        logger.info(f"Starting batch submission of {total_posts} posts (dry_run={self.dry_run})")
        
        for i, post in enumerate(posts):
            try:
                if progress_callback:
                    progress_callback(i, total_posts, f"Processing post {i+1}/{total_posts}: r/{post.get('subreddit', 'unknown')}")
                
                logger.info(f"Processing post {i+1}/{total_posts}: r/{post.get('subreddit', 'unknown')} - {post.get('title', 'No title')[:50]}...")
                
                # Submit the post
                result = self.submit_single_post(post)
                results.append(result)
                
                # Log the result
                if result['success']:
                    logger.info(f"✅ Post {i+1} SUCCESS: {result.get('post_url', 'No URL')}")
                else:
                    logger.error(f"❌ Post {i+1} FAILED: {result.get('error', 'Unknown error')}")
                
                # Wait between posts (except for the last one)
                if i < total_posts - 1:
                    delay = post.get('delay', config.DEFAULT_DELAY)
                    logger.info(f"⏱️ Post {i+1} completed. Waiting {delay} seconds before post {i+2}...")
                    self.safety_manager.wait_between_posts(delay)
                else:
                    logger.info(f"🎉 All {total_posts} posts processed!")
                    
            except Exception as e:
                # Ensure we don't stop the batch if one post fails
                error_result = {
                    'subreddit': post.get('subreddit', 'unknown'),
                    'title': post.get('title', 'unknown'),
                    'timestamp': datetime.now().isoformat(),
                    'success': False,
                    'error': f"Unexpected error: {str(e)}",
                    'post_url': None,
                    'dry_run': self.dry_run
                }
                results.append(error_result)
                logger.error(f"💥 Post {i+1} CRASHED: {str(e)}")
                
                # Still wait before next post
                if i < total_posts - 1:
                    delay = post.get('delay', config.DEFAULT_DELAY)
                    logger.info(f"⏱️ Waiting {delay} seconds before next post despite error...")
                    self.safety_manager.wait_between_posts(delay)
        
        if progress_callback:
            progress_callback(total_posts, total_posts, "Batch submission completed")
        
        # Summary
        successful = sum(1 for r in results if r['success'])
        logger.info(f"📊 BATCH SUMMARY: {successful}/{total_posts} posts successful")
        
        self.results.extend(results)
        return results

class GradioInterface:
    """Gradio web interface for the Reddit posting tool"""
    
    def __init__(self):
        self.poster = RedditPoster(dry_run=True)
        self.authenticated = False
        self.app = None
        
        # Register cleanup handlers
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n{Fore.YELLOW}🛑 Received shutdown signal. Cleaning up...{Style.RESET_ALL}")
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Clean up resources"""
        if self.app:
            try:
                print(f"{Fore.BLUE}🧹 Closing Gradio interface...{Style.RESET_ALL}")
                self.app.close()
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️ Error during cleanup: {e}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Cleanup completed{Style.RESET_ALL}")
        
    def authenticate_reddit(self, password: str) -> Tuple[str, bool]:
        """Authenticate with Reddit"""
        if not password:
            return "Please enter your Reddit password", False
        
        success, message = self.poster.initialize_reddit(password)
        self.authenticated = success
        
        if success:
            return f"✅ {message}", True
        else:
            return f"❌ {message}", False
    
    def toggle_dry_run(self, dry_run_enabled: bool) -> str:
        """Toggle dry-run mode"""
        self.poster.dry_run = dry_run_enabled
        mode = "ENABLED" if dry_run_enabled else "DISABLED"
        safety = "🛡️ SAFE MODE" if dry_run_enabled else "⚠️ LIVE MODE"
        return f"Dry Run: {mode} {safety}"
    
    def validate_single_post(self, subreddit: str, title: str, content: str, flair: str = "") -> str:
        """Validate a single post"""
        post_data = {
            'subreddit': subreddit.strip(),
            'title': title.strip(),
            'content': content.strip(),
            'flair': flair.strip() if flair else None
        }
        
        is_valid, message = self.poster.validator.validate_post_data(post_data)
        
        if is_valid:
            return f"✅ Post validation passed: {message}"
        else:
            return f"❌ Post validation failed: {message}"
    
    def get_subreddit_flairs(self, subreddit_name: str) -> Tuple[str, str]:
        """Get available flairs for a subreddit"""
        if not subreddit_name.strip():
            return "❌ Please enter a subreddit name", {}
        
        # Use authenticated reddit if available for better flair access
        if self.authenticated and self.poster.reddit:
            reddit = self.poster.reddit
        else:
            # Try with read-only access (limited flair access)
            try:
                import praw
                from config import config
                reddit = praw.Reddit(
                    client_id=config.CLIENT_ID,
                    client_secret=config.CLIENT_SECRET,
                    user_agent=config.USER_AGENT
                )
            except Exception as e:
                return f"❌ Cannot access Reddit API: {str(e)}", {}
        
        try:
            subreddit = reddit.subreddit(subreddit_name.strip())
            flairs = []
            
            # Try to get flair templates first
            try:
                link_templates = list(subreddit.flair.link_templates)
                for template in link_templates:
                    text = template.get('text', '').strip()
                    if text:  # Only add flairs with text
                        flairs.append({
                            'text': text,
                            'id': template.get('id', ''),
                            'mod_only': template.get('mod_only', False),
                            'source': 'templates'
                        })
            except Exception as e:
                # Fallback: Get flairs from recent posts
                try:
                    seen_flairs = set()
                    for submission in subreddit.hot(limit=50):
                        if hasattr(submission, 'link_flair_text') and submission.link_flair_text:
                            flair_text = submission.link_flair_text.strip()
                            if flair_text and flair_text not in seen_flairs:
                                seen_flairs.add(flair_text)
                                flairs.append({
                                    'text': flair_text,
                                    'id': 'unknown',
                                    'mod_only': False,
                                    'source': 'recent_posts'
                                })
                except Exception:
                    pass
            
            if flairs:
                flair_text = f"🏷️ **Available Flairs ({len(flairs)}):**\n\n"
                for i, flair in enumerate(flairs[:15], 1):  # Show first 15
                    mod_indicator = " (Mod Only)" if flair.get('mod_only') else ""
                    flair_text += f"**{i}.** {flair['text']}{mod_indicator}\n"
                
                if len(flairs) > 15:
                    flair_text += f"\n*...and {len(flairs) - 15} more flairs*"
                
                return flair_text, {'flairs': flairs}
            else:
                return "🏷️ **Flairs:** No flairs found or flair access restricted", {}
                
        except Exception as e:
            return f"❌ Error fetching flairs: {str(e)}", {}
    
    def get_subreddit_info(self, subreddit_name: str) -> Tuple[str, str]:
        """Get subreddit rules and information"""
        if not subreddit_name.strip():
            return "❌ Please enter a subreddit name", {}
        
        # Always use authenticated reddit if available for better flair access
        if self.authenticated and self.poster.reddit:
            reddit = self.poster.reddit
        else:
            # Try with read-only access (limited flair access)
            try:
                import praw
                from config import config
                reddit = praw.Reddit(
                    client_id=config.CLIENT_ID,
                    client_secret=config.CLIENT_SECRET,
                    user_agent=config.USER_AGENT
                )
            except Exception as e:
                return f"❌ Cannot access Reddit API: {str(e)}", {}
        
        try:
            rules_info = self.poster.validator.get_subreddit_rules(reddit, subreddit_name.strip())
            
            if 'error' in rules_info:
                return f"❌ Error getting subreddit info: {rules_info['error']}", {}
            
            # Format the information
            info_text = f"📋 **r/{rules_info['subreddit']} Information**\n\n"
            info_text += f"**Title:** {rules_info.get('title', 'N/A')}\n"
            info_text += f"**Subscribers:** {rules_info.get('subscribers', 'N/A'):,}\n"
            info_text += f"**Submission Type:** {rules_info.get('submission_type', 'unknown')}\n"
            info_text += f"**Allows Images:** {'✅' if rules_info.get('allow_images') else '❌'}\n"
            info_text += f"**Allows Videos:** {'✅' if rules_info.get('allow_videos') else '❌'}\n"
            info_text += f"**NSFW:** {'⚠️ Yes' if rules_info.get('over18') else '✅ No'}\n"
            
            if rules_info.get('domain_whitelist'):
                info_text += f"\n**🔗 Detected Approved Domains:**\n"
                for domain in rules_info['domain_whitelist']:
                    info_text += f"• {domain}\n"
            
            if rules_info.get('posting_requirements'):
                info_text += f"\n**📋 Posting Requirements:**\n"
                reqs = rules_info['posting_requirements']
                if reqs.get('karma_required'):
                    info_text += "• Karma requirements may apply\n"
                if reqs.get('account_age_required'):
                    info_text += "• Account age requirements may apply\n"
                if reqs.get('verification_required'):
                    info_text += "• Verification may be required\n"
            
            if rules_info.get('available_flairs'):
                info_text += f"\n**🏷️ Available Flairs ({len(rules_info['available_flairs'])}):**\n"
                for flair in rules_info['available_flairs'][:10]:  # Show first 10 flairs
                    flair_text = flair.get('text', 'No text')
                    mod_only = " (Mod Only)" if flair.get('mod_only') else ""
                    info_text += f"• {flair_text}{mod_only}\n"
                
                if len(rules_info['available_flairs']) > 10:
                    info_text += f"• ... and {len(rules_info['available_flairs']) - 10} more flairs\n"
            elif rules_info.get('link_flair_enabled'):
                info_text += f"\n**🏷️ Flairs:** Enabled but couldn't fetch list\n"
            
            # Format rules as JSON for detailed view
            rules_json = rules_info  # Return the dict directly, not JSON string
            
            return info_text, rules_json
            
        except Exception as e:
            return f"❌ Error fetching subreddit information: {str(e)}", {}
    
    def submit_single_post(self, subreddit: str, title: str, content: str, flair: str = "", delay: int = 90) -> Tuple[str, str]:
        """Submit a single post"""
        if not self.authenticated and not self.poster.dry_run:
            return "❌ Please authenticate first", ""
        
        post_data = {
            'subreddit': subreddit.strip(),
            'title': title.strip(),
            'content': content.strip(),
            'flair': flair.strip() if flair else None,
            'delay': delay
        }
        
        result = self.poster.submit_single_post(post_data)
        
        if result['success']:
            status = f"✅ Post submitted successfully!\n"
            status += f"Subreddit: r/{result['subreddit']}\n"
            status += f"Title: {result['title']}\n"
            if result.get('post_url'):
                status += f"URL: {result['post_url']}\n"
            status += f"Mode: {'DRY RUN' if result['dry_run'] else 'LIVE'}"
            
            # Format result for JSON display
            result_json = json.dumps(result, indent=2, default=str)
            return status, result_json
        else:
            status = f"❌ Post submission failed!\n"
            status += f"Error: {result['error']}"
            result_json = json.dumps(result, indent=2, default=str)
            return status, result_json
    
    def process_file_upload(self, file_path: str) -> Tuple[str, str, List[List]]:
        """Process uploaded JSON or CSV file"""
        if not file_path:
            return "No file uploaded", "", []
        
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.json':
                posts = self.poster.file_handler.read_json_file(file_path)
            elif file_ext == '.csv':
                posts = self.poster.file_handler.read_csv_file(file_path)
            else:
                return "❌ Unsupported file format. Please use JSON or CSV.", "", []
            
            # Validate posts
            valid_posts, errors = self.poster.validate_post_batch(posts)
            
            status = f"✅ File processed successfully!\n"
            status += f"Total posts found: {len(posts)}\n"
            status += f"Valid posts: {len(valid_posts)}\n"
            status += f"Invalid posts: {len(errors)}\n"
            
            if errors:
                status += "\nValidation Errors:\n" + "\n".join(errors)
            
            # Convert to table format for display
            table_data = []
            for i, post in enumerate(valid_posts):
                table_data.append([
                    i + 1,
                    post.get('subreddit', ''),
                    post.get('title', '')[:50] + '...' if len(post.get('title', '')) > 50 else post.get('title', ''),
                    post.get('flair', ''),
                    post.get('delay', config.DEFAULT_DELAY)
                ])
            
            posts_json = json.dumps(valid_posts, indent=2, default=str)
            
            return status, posts_json, table_data
            
        except Exception as e:
            return f"❌ Error processing file: {str(e)}", "", []
    
    def submit_batch_posts(self, posts_json: str, progress=gr.Progress()) -> Tuple[str, str]:
        """Submit batch posts with progress tracking"""
        if not posts_json or not posts_json.strip():
            return "❌ No posts data provided", ""
        
        if not self.authenticated and not self.poster.dry_run:
            return "❌ Please authenticate first", ""
        
        try:
            posts = json.loads(posts_json)
            if not isinstance(posts, list):
                posts = [posts]
            
            # Progress callback for Gradio
            def progress_callback(current, total, message):
                progress((current, total), desc=message)
            
            # Submit posts
            results = self.poster.submit_post_batch(posts, progress_callback)
            
            # Generate summary
            successful = sum(1 for r in results if r['success'])
            total = len(results)
            
            status = f"✅ Batch submission completed!\n"
            status += f"Total posts: {total}\n"
            status += f"Successful: {successful}\n"
            status += f"Failed: {total - successful}\n"
            status += f"Success rate: {(successful/total)*100:.1f}%\n"
            status += f"Mode: {'DRY RUN' if self.poster.dry_run else 'LIVE'}"
            
            results_json = json.dumps(results, indent=2, default=str)
            
            return status, results_json
            
        except json.JSONDecodeError:
            return "❌ Invalid JSON format in posts data", ""
        except Exception as e:
            return f"❌ Error during batch submission: {str(e)}", ""
    
    def create_interface(self):
        """Create the Gradio interface"""
        
        # Custom CSS for better styling
        css = """
        .gradio-container {
            max-width: 1200px !important;
        }
        .status-success {
            color: #10b981 !important;
        }
        .status-error {
            color: #ef4444 !important;
        }
        .dry-run-warning {
            background-color: #fef3c7 !important;
            border: 1px solid #f59e0b !important;
            border-radius: 8px !important;
            padding: 12px !important;
            margin: 8px 0 !important;
        }
        """
        
        with gr.Blocks(
            title="Reddit Posting Tool",
            theme=gr.themes.Soft(primary_hue="blue", secondary_hue="slate"),
            css=css
        ) as interface:
            
            # Get username from config
            username = config.USERNAME if config.USERNAME else "Not configured"
            
            gr.Markdown(f"""
            # 🚀 Reddit Posting Tool
            
            **Professional Reddit automation tool with comprehensive safety features**
            
            **👤 Reddit Account:** u/{username}
            
            ⚠️ **IMPORTANT**: Always start in DRY RUN mode to test your posts safely!
            """)
            
            # Authentication Section
            with gr.Row():
                with gr.Column(scale=2):
                    gr.Markdown("## 🔐 Authentication")
                    # Dynamic username from config
                    username = config.USERNAME if config.USERNAME else "your Reddit account"
                    
                    password_input = gr.Textbox(
                        label=f"Reddit Password for u/{username}",
                        type="password",
                        placeholder="Enter your Reddit password"
                    )
                    auth_btn = gr.Button("🔑 Authenticate", variant="primary")
                    auth_status = gr.Textbox(
                        label="Authentication Status",
                        value="❌ Not authenticated",
                        interactive=False
                    )
                
                with gr.Column(scale=1):
                    gr.Markdown("## ⚙️ Safety Settings")
                    dry_run_toggle = gr.Checkbox(
                        label="Dry Run Mode (RECOMMENDED)",
                        value=True,
                        info="Test posts without actually submitting"
                    )
                    dry_run_status = gr.Textbox(
                        label="Current Mode",
                        value="Dry Run: ENABLED 🛡️ SAFE MODE",
                        interactive=False
                    )
            
            # Main Interface Tabs
            with gr.Tabs() as tabs:
                
                # Single Post Tab
                with gr.TabItem("📝 Single Post", id=0):
                    gr.Markdown("### Submit a single post to Reddit")
                    
                    with gr.Row():
                        with gr.Column():
                            single_subreddit = gr.Textbox(
                                label="Subreddit",
                                placeholder="test"
                            )
                            single_title = gr.Textbox(
                                label="Post Title",
                                placeholder="My awesome post title"
                            )
                            single_content = gr.Textbox(
                                label="Post Content",
                                placeholder="Write your post content here...",
                                lines=5
                            )
                            single_flair = gr.Textbox(
                                label="Flair (Optional)",
                                placeholder="Discussion"
                            )
                            single_delay = gr.Slider(
                                label="Delay (seconds)",
                                minimum=60,
                                maximum=300,
                                value=90,
                                step=10,
                                info="Delay before posting (for safety)"
                            )
                        
                        with gr.Column():
                            validate_btn = gr.Button("✅ Validate Post", variant="secondary")
                            rules_btn = gr.Button("📋 Get Subreddit Rules", variant="secondary")
                            flairs_btn = gr.Button("🏷️ Get Available Flairs", variant="secondary")
                            submit_single_btn = gr.Button("🚀 Submit Post", variant="primary")
                            
                            validation_result = gr.Textbox(
                                label="Validation Result",
                                interactive=False,
                                lines=3
                            )
                            
                            subreddit_info = gr.Markdown(
                                label="Subreddit Information",
                                value="Click 'Get Subreddit Rules' to see posting requirements",
                                visible=True
                            )
                            
                            flair_info = gr.Markdown(
                                label="Available Flairs",
                                value="Click 'Get Available Flairs' to see flair options",
                                visible=True
                            )
                            
                            single_post_result = gr.Textbox(
                                label="Submission Result",
                                interactive=False,
                                lines=5
                            )
                            
                            single_post_json = gr.JSON(
                                label="Detailed Result",
                                visible=True
                            )
                            
                            subreddit_rules_json = gr.JSON(
                                label="Detailed Subreddit Rules",
                                visible=False
                            )
                
                # Batch Upload Tab
                with gr.TabItem("📁 Batch Upload", id=1):
                    gr.Markdown("### Upload and submit multiple posts from file")
                    
                    with gr.Row():
                        with gr.Column():
                            file_upload = gr.File(
                                label="Upload Posts File",
                                file_types=[".json", ".csv"]
                            )
                            
                            process_file_btn = gr.Button("📋 Process File", variant="secondary")
                            
                            file_status = gr.Textbox(
                                label="File Processing Status",
                                interactive=False,
                                lines=5
                            )
                        
                        with gr.Column():
                            posts_preview = gr.Dataframe(
                                label="Posts Preview",
                                headers=["#", "Subreddit", "Title", "Flair", "Delay"],
                                interactive=False
                            )
                    
                    posts_data = gr.Textbox(
                        label="Posts Data (JSON)",
                        lines=10,
                        placeholder="Upload a file above to see the posts data here...",
                        visible=True
                    )
                    
                    submit_batch_btn = gr.Button("🚀 Submit Batch", variant="primary", size="lg")
                    
                    batch_result = gr.Textbox(
                        label="Batch Submission Result",
                        interactive=False,
                        lines=5
                    )
                    
                    batch_results_json = gr.JSON(
                        label="Detailed Results",
                        visible=True
                    )
                
                # Examples & Help Tab
                with gr.TabItem("📚 Examples & Help", id=2):
                    gr.Markdown("""
                    ### 📋 Sample File Formats
                    
                    #### JSON Format:
                    ```json
                    [
                        {
                            "subreddit": "test",
                            "title": "My First Post",
                            "content": "This is the post content",
                            "flair": "Discussion",
                            "delay": 90
                        },
                        {
                            "subreddit": "AskReddit",
                            "title": "What's your favorite...",
                            "content": "I'm curious about...",
                            "flair": "Question",
                            "delay": 120
                        }
                    ]
                    ```
                    
                    #### CSV Format:
                    ```
                    subreddit,title,content,flair,delay
                    test,"My First Post","This is the post content",Discussion,90
                    AskReddit,"What's your favorite...","I'm curious about...",Question,120
                    ```
                    
                    ### 🛡️ Safety Features
                    
                    - **Dry Run Mode**: Test posts without actually submitting
                    - **Rate Limiting**: Automatic delays to prevent API abuse
                    - **Validation**: Comprehensive post validation before submission
                    - **Session Limits**: Maximum posts per session for safety
                    - **Random Delays**: Natural timing to avoid detection
                    
                    ### ⚠️ Important Notes
                    
                    1. Always test with dry run mode first
                    2. Respect subreddit rules and Reddit's terms of service
                    3. Use appropriate delays between posts (60-300 seconds)
                    4. Monitor your account for any issues
                    5. Keep your credentials secure
                    
                    ### 🔧 Troubleshooting
                    
                    - **Authentication Failed**: Check your username and password
                    - **Subreddit Not Found**: Verify subreddit name and accessibility
                    - **Rate Limited**: Wait and try again with longer delays
                    - **Post Rejected**: Check subreddit rules and post format
                    - **Domain Not Allowed**: Use the "Get Subreddit Rules" button to see approved domains
                    
                    ### 📋 Subreddit Rules Checker
                    
                    Use the **"📋 Get Subreddit Rules"** button in the Single Post tab to check:
                    - Allowed domains for links
                    - Posting requirements (karma, account age)
                    - Content restrictions (images, videos, text)
                    - Subreddit-specific rules
                    - NSFW status and other important info
                    """)
                    
                    create_samples_btn = gr.Button("📁 Create Sample Files", variant="secondary")
                    samples_status = gr.Textbox(
                        label="Sample Files Status",
                        interactive=False
                    )
            
            # Event Handlers
            auth_btn.click(
                fn=self.authenticate_reddit,
                inputs=[password_input],
                outputs=[auth_status, gr.State()]
            )
            
            dry_run_toggle.change(
                fn=self.toggle_dry_run,
                inputs=[dry_run_toggle],
                outputs=[dry_run_status]
            )
            
            validate_btn.click(
                fn=self.validate_single_post,
                inputs=[single_subreddit, single_title, single_content, single_flair],
                outputs=[validation_result]
            )
            
            rules_btn.click(
                fn=self.get_subreddit_info,
                inputs=[single_subreddit],
                outputs=[subreddit_info, subreddit_rules_json]
            )
            
            flairs_btn.click(
                fn=self.get_subreddit_flairs,
                inputs=[single_subreddit],
                outputs=[flair_info, gr.State()]
            )
            
            submit_single_btn.click(
                fn=self.submit_single_post,
                inputs=[single_subreddit, single_title, single_content, single_flair, single_delay],
                outputs=[single_post_result, single_post_json]
            )
            
            process_file_btn.click(
                fn=self.process_file_upload,
                inputs=[file_upload],
                outputs=[file_status, posts_data, posts_preview]
            )
            
            submit_batch_btn.click(
                fn=self.submit_batch_posts,
                inputs=[posts_data],
                outputs=[batch_result, batch_results_json]
            )
            
            def create_sample_files_handler():
                try:
                    create_sample_files()
                    return "✅ Sample files created in 'examples/' directory"
                except Exception as e:
                    return f"❌ Error creating sample files: {str(e)}"
            
            create_samples_btn.click(
                fn=create_sample_files_handler,
                outputs=[samples_status]
            )
        
        self.app = interface
        return interface

def main():
    """Main function with CLI argument parsing"""
    parser = argparse.ArgumentParser(
        description="Reddit Posting Tool - Automated Reddit posting with safety features",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python reddit_poster.py --gui                    # Launch Gradio web interface
  python reddit_poster.py --file posts.json       # Post from JSON file
  python reddit_poster.py --file posts.csv        # Post from CSV file
  python reddit_poster.py --create-samples        # Create sample files
  python reddit_poster.py --dry-run --file posts.json  # Test without posting

Safety Features:
  - Dry run mode by default
  - Rate limiting and delays
  - Comprehensive validation
  - Session limits
  - Detailed logging
        """
    )
    
    parser.add_argument(
        '--gui', '--gradio',
        action='store_true',
        help='Launch Gradio web interface'
    )
    
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='JSON or CSV file containing posts to submit'
    )
    
    parser.add_argument(
        '--password', '-p',
        type=str,
        help='Reddit password (will prompt if not provided)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help='Test mode - validate and simulate posting without actually submitting (default: True)'
    )
    
    parser.add_argument(
        '--live',
        action='store_true',
        help='Live mode - actually submit posts (overrides --dry-run)'
    )
    
    parser.add_argument(
        '--create-samples',
        action='store_true',
        help='Create sample input files'
    )
    
    parser.add_argument(
        '--delay',
        type=int,
        default=config.DEFAULT_DELAY,
        help=f'Default delay between posts in seconds (default: {config.DEFAULT_DELAY})'
    )
    
    args = parser.parse_args()
    
    # Handle dry-run vs live mode
    if args.live:
        dry_run = False
    else:
        dry_run = args.dry_run
    
    print(f"{Fore.CYAN}🚀 Reddit Posting Tool{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Mode: {'DRY RUN (Safe)' if dry_run else 'LIVE (Actual posting)'}{Style.RESET_ALL}")
    print("=" * 60)
    
    # Create sample files
    if args.create_samples:
        try:
            create_sample_files()
            print(f"{Fore.GREEN}✅ Sample files created in 'examples/' directory{Style.RESET_ALL}")
            return
        except Exception as e:
            print(f"{Fore.RED}❌ Error creating sample files: {e}{Style.RESET_ALL}")
            return
    
    # Launch Gradio interface
    if args.gui:
        print(f"{Fore.BLUE}🌐 Launching Gradio web interface...{Style.RESET_ALL}")
        interface = GradioInterface()
        app = interface.create_interface()
        try:
            # Try multiple ports if 7860 is busy
            ports_to_try = [7860, 7861, 7862, 7863, 7864]
            launched = False
            
            for port in ports_to_try:
                try:
                    print(f"{Fore.BLUE}🌐 Trying port {port}...{Style.RESET_ALL}")
                    app.launch(
                        server_name="127.0.0.1",
                        server_port=port,
                        share=False,
                        show_error=True,
                        quiet=False,
                        inbrowser=True
                    )
                    launched = True
                    break
                except OSError as e:
                    if "Cannot find empty port" in str(e):
                        print(f"{Fore.YELLOW}⚠️ Port {port} busy, trying next...{Style.RESET_ALL}")
                        continue
                    else:
                        raise e
            
            if not launched:
                print(f"{Fore.RED}❌ All ports busy. Please kill existing processes or restart your terminal.{Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}🛑 Interrupted by user{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Error launching interface: {e}{Style.RESET_ALL}")
        finally:
            interface.cleanup()
        return
    
    # CLI mode
    if args.file:
        # File-based posting
        if not os.path.exists(args.file):
            print(f"{Fore.RED}❌ File not found: {args.file}{Style.RESET_ALL}")
            return
        
        # Get password if needed and not in dry-run mode
        password = args.password
        if not dry_run and not password:
            import getpass
            password = getpass.getpass("Enter Reddit password: ")
        
        # Initialize poster
        poster = RedditPoster(password=password, dry_run=dry_run)
        
        if not dry_run and not poster.reddit:
            print(f"{Fore.RED}❌ Authentication required for live posting{Style.RESET_ALL}")
            return
        
        try:
            # Load posts from file
            file_ext = os.path.splitext(args.file)[1].lower()
            if file_ext == '.json':
                posts = poster.file_handler.read_json_file(args.file)
            elif file_ext == '.csv':
                posts = poster.file_handler.read_csv_file(args.file)
            else:
                print(f"{Fore.RED}❌ Unsupported file format. Use JSON or CSV.{Style.RESET_ALL}")
                return
            
            # Validate posts
            valid_posts, errors = poster.validate_post_batch(posts)
            
            if errors:
                print(f"{Fore.YELLOW}⚠️ Validation errors found:{Style.RESET_ALL}")
                for error in errors:
                    print(f"  {error}")
                print()
            
            if not valid_posts:
                print(f"{Fore.RED}❌ No valid posts found{Style.RESET_ALL}")
                return
            
            print(f"{Fore.GREEN}✅ Found {len(valid_posts)} valid posts{Style.RESET_ALL}")
            
            # Confirm submission
            if not dry_run:
                response = input(f"\n{Fore.YELLOW}⚠️ LIVE MODE: Actually submit {len(valid_posts)} posts? (y/N): {Style.RESET_ALL}")
                if response.lower() != 'y':
                    print("Submission cancelled.")
                    return
            
            # Submit posts
            print(f"\n{Fore.BLUE}🚀 Starting submission...{Style.RESET_ALL}")
            results = poster.submit_post_batch(valid_posts)
            
            # Display results
            print(format_results_for_display(results))
            
            # Save results
            output_file = poster.file_handler.save_results_to_file(results, "")
            print(f"\n{Fore.GREEN}📁 Results saved to: {output_file}{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
            logger.error(f"CLI error: {e}")
    
    else:
        # Show help if no arguments provided
        parser.print_help()

if __name__ == "__main__":
    main()