import os
import json
import datetime
from collections import deque
from typing import Dict, List, Any, Optional
from .config import logger, MAX_HISTORY_LENGTH

class ChatStorage:
    '''Class to manage storage and retrieval of chat history in JSON files'''
    
    def __init__(self, max_history_per_chat: int = None):
        '''Initialize the storage with limit settings'''
        self.max_history_per_chat = max_history_per_chat or MAX_HISTORY_LENGTH
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Cache to avoid frequent file operations
        self.memory_cache = {}
        
        logger.info(f'Initialized chat storage with {self.max_history_per_chat} messages limit per chat')
        logger.info(f'Using data directory: {self.data_dir}')
    
    def _get_file_path(self, chat_id: int) -> str:
        '''Get the file path for a specific chat'''
        return os.path.join(self.data_dir, f"{chat_id}.json")
    
    def _load_chat_history(self, chat_id: int) -> deque:
        '''Load chat history from file'''
        file_path = self._get_file_path(chat_id)
        
        if chat_id in self.memory_cache:
            return self.memory_cache[chat_id]
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Create a deque with max length from the loaded data
                chat_history = deque(data, maxlen=self.max_history_per_chat)
                self.memory_cache[chat_id] = chat_history
                return chat_history
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f'Error loading chat history for {chat_id}: {e}')
                # Return empty deque if there's an error
                empty_history = deque(maxlen=self.max_history_per_chat)
                self.memory_cache[chat_id] = empty_history
                return empty_history
        else:
            # If file doesn't exist, create a new empty deque
            empty_history = deque(maxlen=self.max_history_per_chat)
            self.memory_cache[chat_id] = empty_history
            return empty_history
    
    def _save_chat_history(self, chat_id: int) -> None:
        '''Save chat history to file'''
        if chat_id not in self.memory_cache:
            return
        
        file_path = self._get_file_path(chat_id)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(list(self.memory_cache[chat_id]), f, ensure_ascii=False, indent=2)
            logger.debug(f'Saved chat history for chat {chat_id}')
        except IOError as e:
            logger.error(f'Error saving chat history for {chat_id}: {e}')
    
    def add_message(self, chat_id: int, user_id: int, user_name: str, message_text: str) -> None:
        '''Add a new message to the chat history'''
        # Format timestamp for better readability
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Truncate extremely long messages to prevent memory issues
        max_message_length = 1000  # Reasonable limit for storage
        if len(message_text) > max_message_length:
            truncated_text = message_text[:max_message_length] + "... [truncated]"
            logger.warning(f'Message from {user_name} in chat {chat_id} was truncated from {len(message_text)} to {max_message_length} characters')
            message_text = truncated_text
        
        message_data = {
            'timestamp': timestamp,
            'user_id': user_id,
            'user_name': user_name,
            'text': message_text
        }
        
        # Load chat history from file (or cache)
        chat_history = self._load_chat_history(chat_id)
        
        # Add message to history
        chat_history.append(message_data)
        
        # Save updated history
        self._save_chat_history(chat_id)
        
        logger.debug(f'Added message from {user_name} in chat {chat_id}')
    
    def get_chat_history(self, chat_id: int) -> List[Dict[str, Any]]:
        '''Get the history for a specific chat'''
        # Load chat history from file (or cache)
        chat_history = self._load_chat_history(chat_id)
        
        # Convert deque to list for easier handling
        return list(chat_history)
    
    def get_recent_messages(self, chat_id: int, count: int = 5) -> List[Dict[str, Any]]:
        '''Get the most recent N messages for a specific chat'''
        history = self.get_chat_history(chat_id)
        return history[-count:] if history and len(history) > 0 else []
    
    def clear_chat_history(self, chat_id: int) -> None:
        '''Clear history for a specific chat'''
        file_path = self._get_file_path(chat_id)
        
        # Clear memory cache
        if chat_id in self.memory_cache:
            self.memory_cache[chat_id].clear()
        
        # Remove file if it exists
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f'Cleared history file for chat {chat_id}')
            except IOError as e:
                logger.error(f'Error removing history file for {chat_id}: {e}')
    
    def get_all_chat_ids(self) -> List[int]:
        '''Get a list of all chat IDs with history files'''
        chat_ids = []
        
        # Get all JSON files in the data directory
        if os.path.exists(self.data_dir):
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json'):
                    try:
                        chat_id = int(filename.split('.')[0])
                        chat_ids.append(chat_id)
                    except ValueError:
                        # Skip files that don't have an integer filename
                        continue
        
        return chat_ids

# Create a singleton instance
chat_storage = ChatStorage() 