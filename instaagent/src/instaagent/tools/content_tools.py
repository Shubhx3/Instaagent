from crewai.tools import BaseTool
from typing import Type, List, Optional
from pydantic import BaseModel, Field
import requests
import json
import os
from datetime import datetime
import time
import random


class InstagramPostInput(BaseModel):
    """Input schema for Instagram Post Scheduling Tool."""
    caption: str = Field(..., description="Caption for the post")
    image_path: str = Field(..., description="Path to image file to be posted")
    scheduled_time: Optional[datetime] = Field(None, description="Time to schedule post (ISO format, e.g. '2023-10-15T14:30:00')")

class InstagramPostTool(BaseTool):
    name: str = "Instagram Post Scheduling Tool"
    description: str = (
        "Schedules Instagram posts at optimal times. If no time is specified, "
        "it will determine the best posting time based on audience engagement analytics."
    )
    args_schema: Type[BaseModel] = InstagramPostInput
    
    def _run(self, caption: str, image_path: str, scheduled_time: Optional[str] = None) -> str:
        """
        Schedule an Instagram post.
        
        In a real implementation, this would use Instagram's Content Publishing API.
        This POC version simulates the functionality.
        """
        try:
            # Load tokens
            with open("credentials/instagram_tokens.json", "r") as f:
                tokens = json.load(f)
            
            # Verify image exists
            if not os.path.exists(image_path):
                return f"Error: Image file not found at {image_path}"
            
            # Determine posting time
            if not scheduled_time:
                # If no time specified, determine optimal time (simulated)
                optimal_hours = [8, 12, 17, 20]  # Example optimal hours
                current_hour = datetime.now().hour
                
                # Find the next optimal hour
                next_hour = next((h for h in optimal_hours if h > current_hour), optimal_hours[0])
                
                # Create a datetime for today at the next optimal hour
                optimal_time = datetime.now().replace(hour=next_hour, minute=0, second=0)
                
                if optimal_time < datetime.now():
                    # If the optimal time is in the past, schedule for tomorrow
                    optimal_time = optimal_time.replace(day=optimal_time.day + 1)
                
                scheduled_time = optimal_time.isoformat()
            
            # In a real implementation, you would:
            # 1. Upload the image to Instagram's servers
            # 2. Create a media container
            # 3. Schedule the post using the container ID
            
            # Save scheduled post information
            post_info = {
                "caption": caption,
                "image_path": image_path,
                "scheduled_time": scheduled_time,
                "status": "scheduled",
                "created_at": datetime.now().isoformat()
            }
            
            self._save_scheduled_post(post_info)
            
            return f"Post successfully scheduled for {scheduled_time}"
            
        except FileNotFoundError:
            return "No authentication token found. Please authenticate first."
        except Exception as e:
            return f"Post scheduling failed: {str(e)}"
    
    def _save_scheduled_post(self, post_info: dict) -> None:
        """Save scheduled post information."""
        os.makedirs("data", exist_ok=True)
        
        try:
            # Load existing data if any
            with open("data/scheduled_posts.json", "r") as f:
                existing_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []
        
        # Add new post info
        existing_data.append(post_info)
        
        with open("data/scheduled_posts.json", "w") as f:
            json.dump(existing_data, f)


class InstagramCaptionInput(BaseModel):
    """Input schema for Instagram Caption Generator Tool."""
    topic: str = Field(..., description="Main topic or theme of the post")
    image_description: Optional[str] = Field(None, description="Description of the image being posted")
    tone: Optional[str] = Field("engaging", description="Desired tone of the caption (e.g., professional, casual, funny)")
    hashtags_count: Optional[int] = Field(5, description="Number of hashtags to include")

class InstagramCaptionTool(BaseTool):
    name: str = "Instagram Caption Generator Tool"
    description: str = (
        "Generates engaging Instagram captions based on the post topic, "
        "image content, and current trends. Can adjust tone and include relevant hashtags."
    )
    args_schema: Type[BaseModel] = InstagramCaptionInput
    
    def _run(self, topic: str, image_description: Optional[str] = None, 
             tone: Optional[str] = "engaging", hashtags_count: Optional[int] = 5) -> str:
        """
        Generate an Instagram caption.
        
        In a real implementation, this would likely use an LLM API.
        This POC version provides predefined templates and hashtags.
        """
        # Caption templates by tone
        templates = {
            "professional": [
                "Elevating {topic} to new heights. {hashtags}",
                "Exploring the nuances of {topic} in today's landscape. {hashtags}",
                "Sharing insights on {topic} that might change your perspective. {hashtags}"
            ],
            "casual": [
                "Just vibing with some {topic} today! {hashtags}",
                "That {topic} feeling... you know what I'm talking about 😉 {hashtags}",
                "Taking a moment to appreciate {topic} in our daily lives. {hashtags}"
            ],
            "funny": [
                "When {topic} is life but also hilarious 😂 {hashtags}",
                "Tell me you're obsessed with {topic} without telling me... I'll go first! {hashtags}",
                "If {topic} was a person, it would definitely be the life of the party! {hashtags}"
            ],
            "engaging": [
                "What's your take on {topic}? Share in the comments! {hashtags}",
                "Double tap if {topic} makes your day better! {hashtags}",
                "Question for you: How has {topic} impacted your journey? {hashtags}"
            ]
        }
        
        # Default to engaging if specified tone not found
        selected_tone = tone.lower() if tone.lower() in templates else "engaging"
        
        # Select a random template from the specified tone
        template = random.choice(templates[selected_tone])
        
        # Get relevant hashtags
        hashtags = self._generate_hashtags(topic, hashtags_count)
        
        # Format the caption
        caption = template.format(topic=topic, hashtags=hashtags)
        
        # Add image description if provided
        if image_description:
            caption = f"{caption}\n\n📸 {image_description}"
        
        return caption
    
    def _generate_hashtags(self, topic: str, count: int) -> str:
        """Generate relevant hashtags based on the topic."""
        # Common Instagram hashtags by category (simplified for POC)
        hashtag_categories = {
            "AI": ["artificialintelligence", "machinelearning", "deeplearning", "aitech", "futuretech"],
            "technology": ["tech", "innovation", "digital", "geek", "programming", "coding", "developer"],
            "social media": ["socialmedia", "digitalmarketing", "marketing", "contentcreation", "influencer"],
            "business": ["entrepreneur", "startup", "success", "motivation", "business", "hustle"],
            "lifestyle": ["lifestyle", "life", "instagood", "happy", "love", "beautiful", "photooftheday"],
            "travel": ["travel", "wanderlust", "adventure", "explore", "vacation", "travelgram", "nature"],
            "food": ["food", "foodie", "delicious", "yummy", "instafood", "foodporn", "healthyfood"],
            "fitness": ["fitness", "workout", "gym", "fit", "health", "training", "motivation", "exercise"],
            "fashion": ["fashion", "style", "outfit", "ootd", "streetstyle", "fashionista", "clothing"]
        }
        
        # Determine most relevant category (simple matching for POC)
        topic_lower = topic.lower()
        relevant_categories = []
        
        for category, _ in hashtag_categories.items():
            if category.lower() in topic_lower:
                relevant_categories.append(category)
        
        # If no categories match, use a default one
        if not relevant_categories:
            # Choose a default category based on partial matches
            for category in hashtag_categories.keys():
                for word in category.split():
                    if word.lower() in topic_lower:
                        relevant_categories.append(category)
                        break
        
        # Still no match? Use general hashtags
        if not relevant_categories:
            relevant_categories = ["lifestyle"]  # Default category
        
        # Collect hashtags from all relevant categories
        all_hashtags = []
        for category in relevant_categories:
            all_hashtags.extend(hashtag_categories[category])
        
        # Add topic-specific hashtags
        topic_words = topic.lower().split()
        for word in topic_words:
            if len(word) > 3:  # Only use words longer than 3 characters
                all_hashtags.append(word.strip(".,!?"))
        
        # Remove duplicates and ensure we have at least count hashtags
        unique_hashtags = list(set(all_hashtags))
        
        # If we don't have enough unique hashtags, add some general ones
        general_hashtags = ["instagood", "photooftheday", "instagram", "follow", "instadaily", "picoftheday", "art", "photography"]
        while len(unique_hashtags) < count and general_hashtags:
            hashtag = general_hashtags.pop(0)
            if hashtag not in unique_hashtags:
                unique_hashtags.append(hashtag)
        
        # Ensure we don't exceed the requested count
        selected_hashtags = unique_hashtags[:count]
        
        # Format hashtags
        formatted_hashtags = " ".join([f"#{tag}" for tag in selected_hashtags])
        
        return formatted_hashtags