from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    woolworths_cookie: str
    coles_cookie: str
    iga_cookie: str = ""
    receiver_email: str
    sender_email: str
    sender_password: str

    class Config:
        env_file = ".env"


settings = Settings()
