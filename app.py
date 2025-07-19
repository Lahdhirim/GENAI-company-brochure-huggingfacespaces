import gradio as gr
import logging
import os
from dotenv import load_dotenv, find_dotenv
from src.config_loader.config_loader import config_loader
from src.utils.schema import LLMSchema
from src.openrouter_api.openrouter_generator import OpenRouterGenerator
from src.utils.utils_toolbox import load_models, load_prompt
from src.web_scraper.web_scraper import WebScraper

# [MEDIUM]: add number of trials for each user

# Set up logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename="logs/app.log",
                    level=logging.INFO,
                    filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s"
                )
logging.info("Logging setup complete")

# load API keys from .env file
load_dotenv(find_dotenv(), override=True)
api_key = os.getenv("OPENROUTER_API_KEY")
logging.info("API key loaded")

# load configuration file
config = config_loader(config_path="config/config.json")
logging.info(f"Configuration loaded from: {config}")

# Initialize the web scraper
web_scraper = WebScraper(config=config.web_scraper_config)
logging.info(f"Web scraper initialized")

# Get the system prompt
system_prompt = load_prompt(prompt_path=config.prompts.system_prompt_file,
                            insert=False)

# Load OpenRouter LLM list
open_router_models = load_models(llm_list_path=config.open_router_config.open_router_llms)
model_mapping_dict = {llm[LLMSchema.MODEL_NAME]: llm[LLMSchema.MODEL_ID] for llm in open_router_models}

# Initialize OpenRouterGenerator
openrouter_generator = OpenRouterGenerator(api_key=api_key,
                                       base_url=config.open_router_config.base_url,
                                       web_scraper=web_scraper,
                                       system_prompt=system_prompt,
                                       user_prompt_path=config.prompts.user_prompt_file,
                                       model_mapping_dict=model_mapping_dict)

# Gradio Interface
view = gr.Interface(
    fn=openrouter_generator.generate_brochure,
    inputs=[
        gr.Textbox(label="Company Name"),
        gr.Textbox(label="URL"),
        gr.Dropdown(model_mapping_dict.keys(), label="Available LLMs:")
    ],
    outputs=[gr.Markdown(label="Brochure")],
    title="AI Brochure Generator",
    description="This tool allows you to generate a brochure using Large Language Models (LLMs) from OpenRouter. Simply provide the company name, URL of the content you want to include in the brochure, and select an available LLM from the dropdown menu."
)

view.launch()