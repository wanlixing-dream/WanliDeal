from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_model: str = "deepseek/deepseek-chat"
    llm_api_key: str = ""
    llm_base_url: str = ""
    database_url: str = "sqlite:///./wanlideal.db"
    debug: bool = True

    model_config = {"env_prefix": "WANLI_", "env_file": ".env"}


settings = Settings()
