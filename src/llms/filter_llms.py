import requests
from src.utils.schema import LLMSchema

def is_model_available(url: str, model_id: str, api_key: str) -> bool:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_id,
        "messages": [{"role": "user", "content": "Hi"}],
        "max_tokens": 5
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        return response.status_code == 200
    except:
        return False

# [HIGH]: add logging during testing
def get_available_models(url: str, api_key: str, models: dict) -> list:
    available = []
    for model in models:
        if is_model_available(url=url, model_id=model[LLMSchema.MODEL_ID], api_key=api_key):
            available.append(model)
    return available
