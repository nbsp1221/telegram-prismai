import requests
import openai
from typing import Dict, List, Any, Optional

from ..config import (
    logger, OPENAI_API_KEY, OPENAI_API_BASE,
    DEFAULT_MODEL
)

class LLMClient:
    '''Client for handling AI completions with LiteLLM'''
    
    def __init__(self):
        '''Initialize the LLM client with API configuration'''
        # Configure OpenAI/LiteLLM client
        openai.api_key = OPENAI_API_KEY
        openai.base_url = OPENAI_API_BASE
        
        # Variable to store available models
        self.available_models = []
        
        # Fetch available models on initialization
        self.check_model_availability()
    
    def check_model_availability(self) -> List[str]:
        '''Check which models are available on the LiteLLM server'''
        try:
            # Use synchronous requests library
            models_url = f"{OPENAI_API_BASE}/models"
            headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
            
            response = requests.get(models_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.available_models = [model['id'] for model in data.get('data', [])]
                logger.info(f"Available models: {', '.join(self.available_models)}")
                return self.available_models
            else:
                logger.warning(f"Failed to get available models: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error checking model availability: {e}")
            return []

    def get_best_model(self) -> str:
        '''Get the best available model, falling back to alternatives if needed'''
        model_to_use = DEFAULT_MODEL
        if self.available_models and DEFAULT_MODEL not in self.available_models:
            # Try to use the first available model
            if self.available_models:
                model_to_use = self.available_models[0]
                logger.info(f'Using alternative model: {model_to_use} instead of {DEFAULT_MODEL}')
        return model_to_use

    def generate_completion(self, messages: List[Dict[str, str]]) -> str:
        '''Generate a completion using the AI model'''
        try:
            # Log the messages being sent to the LLM
            logger.info(f'Sending messages to LLM: {messages}')
            
            # Get the best available model
            model_to_use = self.get_best_model()
            
            # Log the model and API endpoint being used
            logger.debug(f'Using model: {model_to_use}, API endpoint: {openai.base_url}')
            
            # Create chat completion
            response = openai.chat.completions.create(
                model=model_to_use,
                messages=messages,
                # max_tokens=MAX_TOKENS,
                # temperature=TEMPERATURE,
                # top_p=0.9,
                # frequency_penalty=1.1
            )
            
            if not hasattr(response, 'choices') or not response.choices:
                logger.error(f'Invalid response structure: {response}')
                return 'Sorry, I received an invalid response format from the AI service.'
                
            return response.choices[0].message.content
            
        except openai.APIError as api_err:
            logger.error(f'OpenAI API error: {api_err}')
            # Check if we need to list available models
            if '404' in str(api_err):
                model_info = f"Available models: {', '.join(self.available_models)}" if self.available_models else "No models available"
                return f'Sorry, the AI model "{model_to_use}" seems to be unavailable. {model_info}'
            return f'Sorry, there was an AI service error: {str(api_err)}'
            
        except Exception as e:
            logger.error(f'Error generating completion: {e}', exc_info=True)
            return f'Sorry, I encountered an error: {str(e)}'

# Create a singleton instance
llm_client = LLMClient() 