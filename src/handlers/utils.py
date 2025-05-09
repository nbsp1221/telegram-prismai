from telegram.constants import ParseMode
from telegram.error import BadRequest
from ..config import logger

async def send_message_with_fallback(update, text):
    '''Send message with markdown first, fallback to plain text if parsing fails'''
    try:
        # Try with markdown first
        return await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    except BadRequest as e:
        # If markdown parsing fails, send as plain text
        logger.warning(f"Markdown parsing failed: {e}. Sending as plain text.")
        return await update.message.reply_text(text) 