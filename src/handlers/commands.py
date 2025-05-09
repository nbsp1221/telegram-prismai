from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram.error import BadRequest

from ..config import logger, get_commands_help_text
from ..chat_storage import chat_storage
from ..llm.client import llm_client
from ..conversation.manager import conversation_manager
from .utils import send_message_with_fallback

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''Handler for when the bot receives the /start command'''
    user = update.effective_user
    text = (
        f'Hello {user.first_name}! I am PrismAI bot.\n'
        'I can keep track of your chat history and respond using AI.\n'
        'Try /history [question] to ask questions about your past conversations.\n\n'
        'You can also tag me in a message to chat with me using Gemma 3 AI!'
    )
    await send_message_with_fallback(update, text)
    logger.info(f'User {user.id} started the bot')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''Handler for when the bot receives the /help command'''
    help_text = (
        'PrismAI Bot Help:\n\n'
        f'{get_commands_help_text()}\n\n'
        'Examples for /history command:\n'
        '/history Summarize our conversation so far\n'
        '/history Group our discussion by topics\n'
        '/history What were the main points I mentioned?\n\n'
        'You can tag me in a message (e.g., @botname hello) and I\'ll respond using the Gemma 3 AI model.\n\n'
        'Your conversations are stored in chat history for context.'
    )
    await send_message_with_fallback(update, help_text)
    logger.info(f'User {update.effective_user.id} requested help')

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''Handler to analyze chat history with AI'''
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    # Get the command arguments (everything after /history)
    query = update.message.text.strip()
    command_parts = query.split(' ', 1)
    
    if len(command_parts) < 2 or not command_parts[1].strip():
        # No query provided
        await send_message_with_fallback(update, 'Please provide a question after /history command. For example:\n/history Summarize our conversation')
        return
    
    user_query = command_parts[1].strip()
    
    # Get history from persistent storage
    chat_history = chat_storage.get_chat_history(chat_id)
    
    if not chat_history:
        await send_message_with_fallback(update, 'No chat history found. Start chatting to build history!')
        return
    
    # Format chat history for the AI
    history_text = ""
    for msg in chat_history:
        speaker = "Bot" if msg["user_id"] == context.bot.id else msg["user_name"]
        history_text += f"{speaker}: {msg['text']}\n"
    
    # Prepare the message for the LLM
    messages = [
        {
            'role': 'system',
            'content': '당신은 텔레그램 채팅 대화 분석을 돕는 AI 어시스턴트입니다. 제공된 대화 기록을 바탕으로 사용자의 질문에 답변해주세요.'
        },
        {
            'role': 'user',
            'content': f"다음은 대화 기록입니다:\n\n{history_text}\n\n이 대화 기록에 대한 질문: {user_query}"
        }
    ]
    
    # Send "typing..." action
    await context.bot.send_chat_action(chat_id=chat_id, action='typing')
    
    # Get AI response
    logger.info(f'User {user.id} asked about chat history: "{user_query}"')
    try:
        ai_response = llm_client.generate_completion(messages)
        sent_message = await send_message_with_fallback(update, ai_response)
        
        # Store the history query and response in conversation manager to maintain context
        # Create a new conversation chain from this interaction with history context
        conversation_manager.start_history_conversation(
            history_text, user_query, update.message.message_id,
            ai_response, sent_message.message_id
        )
        
        # Also store in chat history for future reference
        chat_storage.add_message(
            chat_id=chat_id,
            user_id=user.id,
            user_name=user.first_name,
            message_text=user_query
        )
        
        chat_storage.add_message(
            chat_id=chat_id,
            user_id=context.bot.id,
            user_name=context.bot.username,
            message_text=ai_response
        )
        
    except Exception as e:
        logger.error(f'Error analyzing chat history: {e}')
        await send_message_with_fallback(update, f'Sorry, I encountered an error while analyzing the chat history: {str(e)}')
    
    logger.info(f'Analyzed chat history for chat {chat_id} based on query: "{user_query}"') 