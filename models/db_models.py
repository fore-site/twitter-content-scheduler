from datetime import datetime
from pydantic import BaseModel
from enum import Enum

class Status(str, Enum):
    """state of user, mapped to database enum status."""
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    DEACTIVATED = "DEACTIVATED"

class User(BaseModel):
    """Table users."""
    id: int
    username: str
    display_name: str
    profile_img: str | None = None
    registered_at: datetime
    is_premium: bool
    total_posts: int | None = None
    scheduled_posts: int | None = None
    sent_posts: int | None = None

class Post(BaseModel):
    """Table posts."""
    id: int
    content: str
    post_img: str | None = None
    created_at: datetime
    scheduled_for: datetime