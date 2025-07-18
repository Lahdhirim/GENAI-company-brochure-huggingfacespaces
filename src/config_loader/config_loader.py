import json
from pydantic import Field, BaseModel
from typing import Optional

class WebScraperConfig(BaseModel):
    timeout: Optional[int] = Field(default=10, description="Timeout for HTTP requests in seconds")

class OpenRouterConfig(BaseModel):
    base_url: str = Field(..., description="OpenRouter API base URL")
    open_router_llms: str = Field(..., description="Path to the OpenRouter supported LLMs")

class PromptsConfig(BaseModel):
    system_prompt_file: str = Field(..., description="Path to the system prompt file")
    user_prompt_file: str = Field(..., description="Path to the user prompt file")

class Config(BaseModel):
    web_scraper_config: WebScraperConfig = Field(..., description="Configuration for web scraping")
    open_router_config: OpenRouterConfig = Field(..., description="Configuration for OpenRouter provider")
    prompts: PromptsConfig = Field(..., description="Configuration for prompt files")

def config_loader(config_path: str) -> Config:
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            config = json.load(file)
        return Config(**config)
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find config file: {config_path}")