import gradio as gr
import os
from dotenv import load_dotenv, find_dotenv
from src.config_loader.config_loader import config_loader
from src.utils.schema import LLMSchema
from src.openrouter_api.openrouter_generator import OpenRouterGenerator
from src.utils.utils_toolbox import load_models, load_prompt
from src.web_scraper.web_scraper import WebScraper
from src.utils.logging_config import logger

# [MEDIUM]: add number of trials for each user

# Set up logging
with open("logs/app.log", "w") as log_file:
    pass
logger.info("Logging setup complete")

# load API keys from .env file
load_dotenv(find_dotenv(), override=True)
api_key = os.getenv("OPENROUTER_API_KEY")
logger.info("API key loaded")

# load configuration file
config = config_loader(config_path="config/config.json")
logger.info(f"Configuration loaded from: {config}")

# Initialize the web scraper
web_scraper = WebScraper(config=config.web_scraper_config)
logger.info(f"Web scraper initialized")

# Get the system prompt
system_prompt = load_prompt(prompt_path=config.prompts.system_prompt_file,
                            insert=False)
logger.info(f"System prompt loaded: {system_prompt}")

# Load OpenRouter LLM list
open_router_models = load_models(llm_list_path=config.open_router_config.open_router_llms)
model_mapping_dict = {llm[LLMSchema.MODEL_NAME]: llm[LLMSchema.MODEL_ID] for llm in open_router_models}
logger.info(f"OpenRouter models loaded: {open_router_models}")

# Initialize OpenRouterGenerator
openrouter_generator = OpenRouterGenerator(api_key=api_key,
                                       base_url=config.open_router_config.base_url,
                                       web_scraper=web_scraper,
                                       system_prompt=system_prompt,
                                       user_prompt_path=config.prompts.user_prompt_file,
                                       model_mapping_dict=model_mapping_dict)
logger.info(f"OpenRouterGenerator initialized")

# Gradio Interface
with gr.Blocks(title="AI Brochure Generator") as view:
    gr.Markdown("# 🧾 AI Brochure Generator")

    gr.Markdown(
        "This tool allows you to generate a brochure using Large Language Models (LLMs) from OpenRouter. "
        "Simply provide the company name, URL of the content you want to include in the brochure, and select an available LLM from the dropdown menu."
    )

    company = gr.Textbox(label="Company Name", placeholder="Example: OpenAI")
    url = gr.Textbox(label="URL", placeholder="https://example.com")
    model = gr.Dropdown(choices=list(model_mapping_dict.keys()), label="Available LLMs:")
    submit = gr.Button("Generate Brochure", interactive=False, variant="primary")
    output = gr.Markdown(label="Brochure")

    # Submit action
    submit.click(
        fn=openrouter_generator.generate_brochure,
        inputs=[company, url, model],
        outputs=output
    )

    # Enable the button only if URL is not empty
    def toggle_button(url_value):
        return gr.update(interactive=bool(url_value.strip()))

    url.change(fn=toggle_button, inputs=url, outputs=submit)

if __name__ == "__main__":
    view.launch()