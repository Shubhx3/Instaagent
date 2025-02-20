from crewai.tools import BaseTool
from typing import Type, List, Optional
from pydantic import BaseModel, Field
import requests
import json
import os
from datetime import datetime
import time
import random

class InstagramSubscriptionInput(BaseModel):
    """Input schema for Instagram Subscription Tool."""
    hashtags: Optional[List[str]] = Field(default=None, description="List of hashtags to monitor")
    users: Optional[List[str]] = Field(default=None, description="List of usernames to monitor")
    
class InstagramSubscriptionInput(BaseModel):
    """Input schema for Instagram Subscription Tool."""
    hashtags: Optional[List[str]] = Field(default=None, description="List of hashtags to monitor")
    users: Optional[List[str]] = Field(default=None, description="List of usernames to monitor")
    
    class Config:
        arbitrary_types_allowed = True
