from pydantic import BaseModel, Field
import os

class Settings(BaseModel):
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = Field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o"))
    knowledge_dir: str = Field(default="knowledge")
    db_path: str = Field(default="db/memory.db")

settings = Settings()