from pydantic import BaseModel

class Token(BaseModel):
    """Model for JWT token."""
    access_token: str
    refresh_token: str | None = None
    token_type: str