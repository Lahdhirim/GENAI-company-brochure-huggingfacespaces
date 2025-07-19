import requests
from src.utils.utils_toolbox import load_prompt
from src.web_scraper.web_scraper import WebScraper

class OpenRouterGenerator:

    def __init__(self, 
                 api_key: str, 
                 base_url: str, 
                 web_scraper: WebScraper,
                 system_prompt: str,
                 user_prompt_path: str,
                 model_mapping_dict: dict,
        ):

        self.api_key = api_key
        self.base_url = base_url
        self.web_scraper = web_scraper
        self.system_prompt = system_prompt
        self.user_prompt_path = user_prompt_path
        self.model_mapping_dict = model_mapping_dict

    
    def generate_brochure(self, 
                          company_name: str, 
                          url: str, 
                          model_name: str
        ) -> str:

        # Extract the content from the URL
        content = self.web_scraper.fetch_text(url=url)

        # Load the user prompt
        user_prompt = load_prompt(prompt_path=self.user_prompt_path,
                                  insert=True,
                                  company_name=company_name,
                                  content=content)
        
        # Select the model
        model_id = self.model_mapping_dict[model_name]

        headers = {
        "Authorization": f"Bearer {self.api_key}",
        "Content-Type": "application/json"
        }

        data = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 800,
            "temperature": 0.1
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=15)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 429:
                return (
                    "🚧 **Oops! The daily request limit for OpenRouter has been reached.**\n\n"
                    "Don't worry, it just means *a lot of people* used the service today.\n\n"
                    "Please try again tomorrow.\n\n"
                    "If you're still having trouble, feel free to reach out to us at moetez.lahdhiri@student-cs.fr. 📞\n\n"
                )
            return f"HTTP error occurred: {http_err}"
        
        except Exception as e:
            return f"Error generating brochure: {e}"