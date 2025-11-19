from enum import Enum

class UserStatus(str, Enum):
    """State of user, mapped to database enum userstatus."""
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    DEACTIVATED = "DEACTIVATED"


class PostStatus(str, Enum):
    """State of post, mapped to database enum poststatus"""
    pending = "pending"
    sent = "sent"
    failed = "failed"

