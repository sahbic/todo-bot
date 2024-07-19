import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
TODO_FILE_PATH = os.getenv("TODO_FILE_PATH")
LOG_FILE_NAME = os.getenv("LOG_FILE_NAME")
WHITELIST_CHAT_ID = os.getenv("WHITELIST_CHAT_ID")
