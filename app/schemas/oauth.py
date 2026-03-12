from pydantic import BaseModel, Field


class OAuthAccountCreate(BaseModel):
    oauth_name: str
    account_id: str
    user_id: int
    account_email: str | None = None

class VKAuthLink(BaseModel):
  auth_url: str = Field(
      description="VK Authorization URL",
      examples=["https://id.vk.com/authorize?response_type=code&client_id=53718410&redirect_uri=http%3A%2F%2Flocalhost%2Fapi%2Fauth%2Fcallback%2Fvkontakte&code_challenge=BwnNW2waF7Dy-sRj4X1-x3LYgbABrLBr96hgFz9_mn4&code_challenge_method=S256&state=qry-Wv9r5w1fiGOlCl8sDg&scope=vkid.personal_info%2Cemail"])
