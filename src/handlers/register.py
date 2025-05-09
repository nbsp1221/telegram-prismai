import sys
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters
)

from ..config import logger, COMMANDS
from .commands import (
    start_command, help_command,
    history_command
)
from .messages import store_message, handle_mention, handle_reply

class HandlerRegistry:
    '''Class responsible for registering all handlers to the application'''
    
    def __init__(self, application: Application):
        '''Initialize with application instance'''
        self.application = application
        self.bot_name = application.bot.username
        
    def register_all(self) -> None:
        '''Register all handlers to the application'''
        self.register_commands()
        self.register_message_handlers()
        logger.info('All handlers registered')
        
    def register_commands(self) -> None:
        '''Register command handlers dynamically from config'''
        # Get command module
        current_module = sys.modules['src.handlers.commands']
        
        for cmd in COMMANDS:
            # Get the handler function by name
            if hasattr(current_module, cmd.handler):
                handler_func = getattr(current_module, cmd.handler)
                self.application.add_handler(CommandHandler(cmd.command, handler_func))
                logger.debug(f'Registered command handler for /{cmd.command}')
            else:
                logger.error(f'Handler function {cmd.handler} not found for command /{cmd.command}')
    
    def register_message_handlers(self) -> None:
        '''Register message handlers'''
        # Add mention handler to respond when the bot is mentioned
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND & filters.Mention(f'@{self.bot_name}'),
                handle_mention
            )
        )
        
        # Add reply handler to respond when users reply to bot's messages
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND & filters.REPLY,
                handle_reply
            )
        )
        
        # Store any message except commands, mentions, and replies
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND & ~filters.Mention(f'@{self.bot_name}') & ~filters.REPLY,
                store_message
            )
        )

def register_handlers(application: Application) -> None:
    '''Function to register all handlers to the application'''
    registry = HandlerRegistry(application)
    registry.register_all() 