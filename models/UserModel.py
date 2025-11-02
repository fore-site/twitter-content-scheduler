from pydantic import BaseModel
from datetime import datetime
from models.TypeModel import UserStatus

class BaseUser(BaseModel):
    """Table users. Model for create or update user. PUT/PATCH responses validate against this model. """
    id: int
    username: str
    display_name: str
    profile_img: str | None = None
    is_premium: bool

class UserOut(BaseUser):
    """Table users. Model for output user."""
    user_status: UserStatus 
    registered_at: datetime
    pending_posts: int | None = None
    sent_posts: int | None = None
    failed_posts: int | None = None