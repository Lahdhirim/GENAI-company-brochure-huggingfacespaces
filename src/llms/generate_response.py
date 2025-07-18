import requests
from src.utils.utils_toolbox import load_prompt
from src.web_scraper.web_scraper import WebScraper


def generate_brochure(
        company_name: str, 
        url: str, 
        base_url: str,
        model_id: str, 
        api_key: str, 
        system_prompt: str,
        user_prompt_path: str,
        web_scraper: WebScraper
    ):

    # Extract the content from the URL
    content = web_scraper.fetch_text(url=url)

    # Load the user prompt
    user_prompt = load_prompt(prompt_path=user_prompt_path,
                              insert=True,
                              company_name=company_name,
                              content=content)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 800,
        "temperature": 0.1
    }

    try:
        response = requests.post(base_url, headers=headers, json=data, timeout=15)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    
    except Exception as e:
        return f"Erreur lors de la génération : {str(e)}"