from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram.error import BadRequest

from ..config import logger
from ..chat_storage import chat_storage
from ..conversation.manager import conversation_manager
from .utils import send_message_with_fallback

async def store_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''Store messages in chat history without responding'''
    if update.message and update.message.text:
        chat_id = update.effective_chat.id
        user = update.effective_user
        text = update.message.text
        
        # Store message in persistent storage
        chat_storage.add_message(
            chat_id=chat_id,
            user_id=user.id,
            user_name=user.first_name,
            message_text=text
        )
        
        logger.info(f'Stored message from {user.first_name} in chat {chat_id}')

async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''Handler for when the bot is mentioned in a message - uses LLM to generate response'''
    if update.message and update.message.text:
        chat_id = update.effective_chat.id
        user = update.effective_user
        text = update.message.text
        bot_username = context.bot.username
        
        # Store message in persistent storage (for history command)
        chat_storage.add_message(
            chat_id=chat_id,
            user_id=user.id,
            user_name=user.first_name,
            message_text=text
        )
        
        # Extract the text without the mention
        mention = f'@{bot_username}'
        message_text = text.replace(mention, '', 1).strip()
        
        if message_text:
            # Send "typing..." action while generating response
            await context.bot.send_chat_action(chat_id=chat_id, action='typing')
            
            # Start of a new conversation - no reply chain
            llm_response = conversation_manager.generate_response(message_text)
            
            # Send response with fallback to plain text if markdown fails
            sent_message = await send_message_with_fallback(update, llm_response)
            
            # Start a new conversation chain
            conversation_manager.start_conversation(
                message_text, update.message.message_id,
                llm_response, sent_message.message_id
            )
            
            # Store bot's response in history (for history command)
            chat_storage.add_message(
                chat_id=chat_id,
                user_id=context.bot.id,
                user_name=context.bot.username,
                message_text=llm_response
            )
            
            logger.info(f'Bot was mentioned by {user.first_name}, responded with LLM')
        else:
            await update.message.reply_text('You mentioned me, but didn\'t say anything. How can I help you?')
            logger.info(f'Bot was mentioned by {user.first_name}, but no content provided')

async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''Handler for when a user replies to the bot's message'''
    if update.message and update.message.reply_to_message and update.message.text:
        # When user replies to bot's message
        if update.message.reply_to_message.from_user.id == context.bot.id:
            chat_id = update.effective_chat.id
            user = update.effective_user
            text = update.message.text
            replied_message_id = update.message.reply_to_message.message_id
            
            # Store message in persistent storage (for history command)
            chat_storage.add_message(
                chat_id=chat_id,
                user_id=user.id,
                user_name=user.first_name,
                message_text=text
            )
            
            # Get or create conversation chain
            conversation = conversation_manager.find_conversation(replied_message_id)
            
            if not conversation:
                # Start a new conversation with just the message being replied to
                bot_message = update.message.reply_to_message.text
                conversation = conversation_manager.create_conversation_from_reply(replied_message_id, bot_message)
            
            # Send "typing..." action while generating response
            await context.bot.send_chat_action(chat_id=chat_id, action='typing')
            
            # Generate response including full conversation chain for context
            llm_response = conversation_manager.generate_response(text, conversation)
            
            # Send response with fallback to plain text if markdown fails
            sent_message = await send_message_with_fallback(update, llm_response)
            
            # Extend the conversation with new messages
            conversation_manager.extend_conversation(
                conversation, 
                text, update.message.message_id,
                llm_response, sent_message.message_id
            )
            
            # Store bot's response in history (for history command)
            chat_storage.add_message(
                chat_id=chat_id,
                user_id=context.bot.id,
                user_name=context.bot.username,
                message_text=llm_response
            )
            
            logger.info(f'Bot replied to {user.first_name}\'s reply using LLM') 