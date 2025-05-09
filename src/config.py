import os
import logging
import requests
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List, Dict, Callable, Awaitable

# Load environment variables from .env file
load_dotenv()

# Bot token
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_TOKEN:
    raise ValueError('TELEGRAM_BOT_TOKEN environment variable is not set.')

# OpenAI/LiteLLM settings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError('OPENAI_API_KEY environment variable is not set.')
OPENAI_API_BASE = os.getenv('OPENAI_API_BASE', 'https://your-litellm-server.example.com/v1')

# LLM model configuration
DEFAULT_MODEL = os.getenv('LLM_MODEL', 'your_model_name_here')  # Default model

# Message history settings
MAX_HISTORY_LENGTH = 500  # Maximum number of messages to store per chat

# Bot command definitions
@dataclass
class CommandDefinition:
    '''Definition of a bot command'''
    command: str
    description: str
    handler: str  # Name of the handler function

# Centralized command definitions
COMMANDS: List[CommandDefinition] = [
    CommandDefinition('start', 'Start the bot', 'start_command'),
    CommandDefinition('help', 'Show help information', 'help_command'),
    CommandDefinition('history', 'Ask questions about past conversations', 'history_command'),
]

# Helper method to get a formatted list of commands for help text
def get_commands_help_text() -> str:
    '''Generate help text from command definitions'''
    return '\n'.join(f'/{cmd.command} - {cmd.description}' for cmd in COMMANDS)

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL)
)
logger = logging.getLogger(__name__)
