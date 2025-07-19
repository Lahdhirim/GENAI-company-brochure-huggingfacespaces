import gradio as gr
import json
import os
from dotenv import load_dotenv, find_dotenv
from src.config_loader.config_loader import config_loader
from src.llms.filter_llms import get_available_models
from src.utils.schema import LLMSchema
from src.llms.generate_response import generate_brochure
from src.utils.utils_toolbox import load_prompt
from src.web_scraper.web_scraper import WebScraper

# load API keys from .env file
load_dotenv(find_dotenv(), override=True)
api_key = os.getenv("OPENROUTER_API_KEY")

# load configuration file
config = config_loader(config_path="config/config.json")

# Get the list of available LLMs
try:
    with open(config.open_router_config.open_router_llms, "r", encoding="utf-8") as open_router_llms:
        open_router_models = json.load(open_router_llms)
except FileNotFoundError:
    raise FileNotFoundError(f"Could not find the LLM list file: {config.open_router_config.open_router_llms}")

available_models = get_available_models(url=config.open_router_config.base_url, 
                                        api_key=api_key,
                                        models=open_router_models)
available_models_names = [llm[LLMSchema.MODEL_NAME] for llm in available_models]


if len(available_models_names) > 0:
    model_mapping_dict = {llm[LLMSchema.MODEL_NAME]: llm[LLMSchema.MODEL_ID] for llm in available_models}

    # Get the system prompt
    system_prompt = load_prompt(prompt_path=config.prompts.system_prompt_file,
                                insert=False)

    # Initialize the web scraper
    web_scraper = WebScraper(config=config.web_scraper_config)

    # Gradio Interface    
    # view = gr.Interface(
    #     fn=lambda company_name, url, model_name: generate_brochure(
    #         company_name=company_name,
    #         url=url,
    #         base_url=config.open_router_config.base_url,
    #         model_id=model_mapping_dict[model_name],
    #         api_key=api_key,
    #         system_prompt=system_prompt,
    #         user_prompt_path=config.prompts.user_prompt_file,
    #         web_scraper=web_scraper
    #     ),
    #     inputs=[
    #         gr.Textbox(label="Compnay Name:"),
    #         gr.Textbox(label="URL page:"),
    #         gr.Dropdown(available_models_names, label="Available LLMs:")
    #     ],
    #     outputs=gr.Markdown(label="Brochure"),
    #     title="LLM Brochure Generator",
    #     description="This application generates a brochure for a company based on its website, using a selected LLM via OpenRouter."
    # )

    with gr.Blocks() as view:
        company = gr.Textbox(label="Company Name")
        url = gr.Textbox(label="URL")
        model = gr.Dropdown(available_models_names, label="Available LLMs:")
        output = gr.Markdown(label="Brochure")
        btn = gr.Button("Generate Brochure")

        def generate_and_display(c, u, m):
            output.update("⌛ Generating brochure...")
            result = generate_brochure(
                company_name=c,
                url=u,
                base_url=config.open_router_config.base_url,
                model_id=model_mapping_dict[m],
                api_key=api_key,
                system_prompt=system_prompt,
                user_prompt_path=config.prompts.user_prompt_file,
                web_scraper=web_scraper
            )
            return result

        btn.click(fn=generate_and_display, inputs=[company, url, model], outputs=output)
    
    view.launch()

# [HIGH]: Enhance the error handling by printing the error message and providing more context (e.g., API Key reaches limit).
else:
    print("No available models found. Please check your API Key limitations.")
    