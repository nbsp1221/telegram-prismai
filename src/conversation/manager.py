from typing import List, Dict, Any, Optional
from ..config import logger
from ..llm.client import llm_client
from ..chat_storage import chat_storage

class ConversationManager:
    '''Manager class for handling conversation history and context'''
    
    def __init__(self):
        '''Initialize the conversation manager'''
        # Global dictionary to store conversation chains by message_id
        # Format: {message_id: [{'is_bot': bool, 'text': str, 'message_id': int}, ...]}
        self.conversation_chains = {}
        logger.debug('ConversationManager initialized')
    
    def build_messages(self, conversation: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        '''Build LLM message format from conversation chain'''
        messages = []
        
        # Add system message to instruct formatting
        messages.append({
            'role': 'system',
            'content': '당신은 텔레그램 채팅에 특화된 AI 어시스턴트입니다.'
        })
        
        # Check if there's a message with history context
        has_history_context = False
        history_context = ""
        
        for msg in conversation:
            if msg.get('has_history_context', False) and 'history_context' in msg:
                has_history_context = True
                history_context = msg.get('history_context', '')
                # Don't break, we still need to process all messages
        
        # If there's history context, add a special context message
        if has_history_context:
            messages.append({
                'role': 'system',
                'content': f'다음은 이전 대화의 기록입니다. 이 맥락을 기반으로 사용자 질문에 답하세요: {history_context}'
            })
        
        # Convert conversation chain to LLM message format
        for msg in conversation:
            role = 'assistant' if msg.get('is_bot', False) else 'user'
            messages.append({
                'role': role,
                'content': msg.get('text', '')
            })
        
        return messages
    
    def start_conversation(self, user_message: str, user_message_id: int, 
                          bot_response: str, bot_message_id: int) -> None:
        '''Start a new conversation with initial messages'''
        conversation = [
            {'is_bot': False, 'text': user_message, 'message_id': user_message_id},
            {'is_bot': True, 'text': bot_response, 'message_id': bot_message_id}
        ]
        self.conversation_chains[bot_message_id] = conversation
        logger.debug(f'Started new conversation with ID: {bot_message_id}')
    
    def find_conversation(self, message_id: int) -> Optional[List[Dict]]:
        '''Find a conversation by message ID'''
        # Direct lookup
        if message_id in self.conversation_chains:
            logger.debug(f'Found existing conversation for message ID: {message_id}')
            return self.conversation_chains[message_id]
        
        # Lookup through message references
        for chain_id, chain in self.conversation_chains.items():
            for msg in chain:
                if msg.get('message_id') == message_id:
                    logger.debug(f'Found conversation through message lookup for ID: {message_id}')
                    return chain
        
        return None
    
    def create_conversation_from_reply(self, replied_message_id: int, replied_message_text: str) -> List[Dict]:
        '''Create a new conversation from a reply to a message'''
        conversation = [
            {'is_bot': True, 'text': replied_message_text, 'message_id': replied_message_id}
        ]
        logger.debug(f'Created new conversation for message ID: {replied_message_id}')
        return conversation
    
    def extend_conversation(self, conversation: List[Dict], 
                          user_message: str, user_message_id: int,
                          bot_response: str, bot_message_id: int) -> None:
        '''Add user message and bot response to a conversation'''
        # Add user message if not already in conversation
        conversation.append({
            'is_bot': False, 
            'text': user_message, 
            'message_id': user_message_id
        })
        
        # Add bot response
        conversation.append({
            'is_bot': True, 
            'text': bot_response, 
            'message_id': bot_message_id
        })
        
        # Store the updated conversation with the new bot message ID as the key
        self.conversation_chains[bot_message_id] = conversation
        logger.debug(f'Conversation now has {len(conversation)} messages')
    
    def generate_response(self, user_text: str, conversation: Optional[List[Dict]] = None) -> str:
        '''Generate a response using LLM with conversation context'''
        messages = []
        
        # Use conversation chain for context if available
        if conversation:
            messages = self.build_messages(conversation)
        else:
            # If no conversation, add system message and user message
            messages.append({
                'role': 'system',
                'content': '당신은 텔레그램 채팅에 특화된 AI 어시스턴트입니다.'
            })
            messages.append({'role': 'user', 'content': user_text})
            return llm_client.generate_completion(messages)
        
        # Ensure the current message is included if using an existing conversation
        current_message_exists = False
        for msg in messages:
            if msg['role'] == 'user' and msg['content'] == user_text:
                current_message_exists = True
                break
        
        if not current_message_exists:
            messages.append({'role': 'user', 'content': user_text})
        
        # Generate response
        return llm_client.generate_completion(messages)

    def start_history_conversation(self, history_text: str, user_query: str, user_message_id: int, 
                               bot_response: str, bot_message_id: int) -> None:
        '''Start a new conversation with history analysis context'''
        # Create a system message summarizing what happened
        system_summary = f"사용자가 대화 기록에 대해 질문했습니다: '{user_query}'. 대화 기록: {history_text}"
        
        conversation = [
            {'is_bot': False, 'text': f"대화 기록에 대한 질문: {user_query}", 'message_id': user_message_id, 'has_history_context': True, 'history_context': history_text},
            {'is_bot': True, 'text': bot_response, 'message_id': bot_message_id}
        ]
        self.conversation_chains[bot_message_id] = conversation
        logger.debug(f'Started new history-based conversation with ID: {bot_message_id}')

# Create a singleton instance
conversation_manager = ConversationManager() 