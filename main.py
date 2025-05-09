from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder

from src.config import TELEGRAM_TOKEN, logger, COMMANDS, DEFAULT_MODEL
from src.handlers import register_handlers
from src.llm.client import llm_client
import logging
import asyncio

# Set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger('httpx').setLevel(logging.WARNING)

def main():
    '''Function to start the bot'''
    # Create application
    logger.info('Starting the bot...')
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Convert the centralized command definitions to BotCommand objects
    bot_commands = [
        BotCommand(cmd.command, cmd.description) for cmd in COMMANDS
    ]

    # Post-initialization callback to set commands and register handlers
    async def post_init(app):
        # First check model availability
        logger.info(f'Checking LLM model availability...')
        # Models should have been checked during LLMClient initialization
        
        if llm_client.available_models:
            if DEFAULT_MODEL in llm_client.available_models:
                logger.info(f'Default model {DEFAULT_MODEL} is available')
            else:
                model_suggestions = ', '.join(llm_client.available_models[:3]) if llm_client.available_models else 'none'
                logger.warning(f'Default model {DEFAULT_MODEL} is not available. Available models: {model_suggestions}')
        else:
            logger.warning('Could not retrieve available models. The LLM functionality might not work correctly.')
        
        # Set up commands
        await app.bot.set_my_commands(bot_commands)
        logger.info(f'Bot commands have been set up for @{app.bot.username}')

        # Now register handlers with proper bot information
        register_handlers(application)
        logger.info(f'Handlers registered for @{app.bot.username}')

    # Set up post-init callback
    application.post_init = post_init

    # Start polling (non-blocking, built-in event loop management)
    # Use allowed_updates to specify which updates to receive
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info('Bot stopped by user')
    except Exception as e:
        logger.error(f'Error during bot execution: {e}', exc_info=True)
