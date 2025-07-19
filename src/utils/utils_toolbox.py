from pathlib import Path
import json


def load_prompt(prompt_path: str, insert: bool = False, **kwargs) -> str:
    """
    Load a prompt from a file.
    
    Args:
        prompt_path (str): Path to the prompt file.
        
    Returns:
        str: The content of the prompt file.
    """
    if not Path(prompt_path).exists():
        raise FileNotFoundError(f"Prompt file {prompt_path} does not exist.")
    
    prompt_path = Path(prompt_path)
    prompt_template = prompt_path.read_text(encoding="utf-8")

    if insert:
        return prompt_template.format(**kwargs)
    else:
        return prompt_template

def load_models(llm_list_path: str) -> list:
    try:
        with open(llm_list_path, "r", encoding="utf-8") as open_router_llms:
            open_router_models = json.load(open_router_llms)

            if len(open_router_models) > 0:
                return open_router_models
            else:
                raise ValueError("No models found in the LLM list file.")

    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find the LLM list file: {llm_list_path}")
