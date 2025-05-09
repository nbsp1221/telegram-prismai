# Telegram PrismAI Bot

A Telegram bot that integrates with LLM services through LiteLLM, providing conversational AI capabilities with persistent storage.

## Features

- AI-powered chat through LiteLLM integration
- Conversation context maintained via Telegram replies
- Chat history stored in JSON files for persistence
- Commands to interact with chat history using AI
- Automatic model availability detection
- Docker support for easy deployment

## Project Structure

```
telegram-prismai/
├── src/                             # Source code
│   ├── conversation/                # Conversation management
│   │   ├── __init__.py
│   │   └── manager.py               # Conversation flow manager
│   ├── handlers/                    # Telegram handlers
│   │   ├── __init__.py
│   │   ├── commands.py              # Command handlers
│   │   ├── messages.py              # Message handlers
│   │   ├── register.py              # Handler registration
│   │   └── utils.py                 # Utility functions
│   ├── llm/                         # LLM integration
│   │   ├── __init__.py
│   │   └── client.py                # LLM client interface
│   ├── __init__.py                  # Package initialization
│   ├── config.py                    # Configuration and settings
│   └── chat_storage.py              # Chat history storage
├── data/                            # Persistent storage for chat history
├── .env                             # Environment variables (not in repo)
├── .env.example                     # Example environment variables
├── .gitignore                       # Git ignore rules
├── Dockerfile                       # Docker image definition
├── docker-compose.yaml              # Docker compose configuration
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
└── README.md                        # Project documentation
```

## Setup

### Standard Setup

1. Create a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.example`:
   ```
   cp .env.example .env
   # Edit the .env file with your credentials
   ```

4. Run the bot:
   ```
   python main.py
   ```

### Docker Setup

1. Create a `.env` file based on `.env.example`:
   ```
   cp .env.example .env
   # Edit the .env file with your credentials
   ```

2. Build and start the Docker container:
   ```
   docker-compose up -d
   ```

3. View logs:
   ```
   docker-compose logs -f
   ```

4. Stop the container:
   ```
   docker-compose down
   ```

## Usage

- Start the bot with `/start`
- Get help with `/help`
- Ask questions about your chat history with `/history [your question]`
- Examples:
  - `/history Summarize our conversation so far`
  - `/history What were the main topics we discussed?`
- Tag the bot in a message to chat with it
- Reply to the bot's messages to continue the conversation with context

## Developer Guide

### Adding a new command

1. Add your command definition to the `COMMANDS` list in `src/config.py`
2. Create a handler function in `src/handlers/commands.py`
3. The handler will be automatically registered when the bot starts

### Adding conversation features

Conversation management is handled in `src/conversation/manager.py`, where you can:

- Modify how conversations are stored and retrieved
- Change the conversation context building logic
- Implement additional conversation features

### Customizing LLM integration

LLM interactions are centralized in `src/llm/client.py`, making it easy to:

- Change LLM parameters
- Switch to a different LLM provider
- Add additional prompt processing logic

### Data Persistence

Chat history is stored in JSON files in the `data/` directory:
- Each chat has its own file named with the chat ID (e.g., `123456789.json`)
- Files are automatically created and managed by the `ChatStorage` class
- History is limited to 500 messages per chat by default 