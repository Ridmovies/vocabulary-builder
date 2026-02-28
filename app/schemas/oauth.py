from pydantic import BaseModel


class OAuthAccountCreate(BaseModel):
    oauth_name: str
    account_id: str
    user_id: int
    account_email: str | None = None
