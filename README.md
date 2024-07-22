# todo-bot

This project is a Telegram bot that manages a to-do list stored in a GitHub repository. The bot allows users to fetch, add, and mark tasks as done via Telegram commands.

It's the perfect companion project to [todo-cli](https://github.com/sahbic/todo-cli).

## Features

- Fetch the current to-do list from a GitHub repository.
- Add new tasks with a specified priority.
- Mark tasks as done.

## Requirements

- Python 3.8+
- [Telegram bot token](https://core.telegram.org/bots/tutorial#obtain-your-bot-token)
- [Github personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token)
- A GitHub repository to store the to-do list and logs

## Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/sahbic/todo-bot.git
   cd todo-bot
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the root directory of the project and add the following variables:

```env
GITHUB_REPO=your_github_username/your_repository_name
TODO_FILE_PATH=todo_default.md
LOG_FILE_NAME=todo.log  # Default is 'todo.log'
GITHUB_TOKEN=your_github_personal_access_token
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
WHITELIST_CHAT_ID=comma,separated,list,of,telegram,user,ids
```

## Usage

1. **Run the bot**

   ```bash
   python bot.py
   ```

2. **Available Commands**

   - `/start` - Start interacting with the bot.
   - `/help` - Get help on how to use the bot.
   - `/list` - Fetch the current to-do list.
   - `/add <priority> <task>` - Add a new task with a given priority.
   - `/mark <task number>` - Mark a task as done.

## Create service

Copy `todobot.service` to `/etc/systemd/system/`

```
sudo cp todobot.service /etc/systemd/system/
```

## Start service

```
sudo systemctl start todobot.service
```

## Stop service

```
sudo systemctl stop todobot.service
```

## Project Structure

```
todo-bot/
│
├── config.py                # Configuration file for environment variables
├── github_interaction.py    # Functions to interact with GitHub API
├── bot.py          # Telegram bot implementation
├── requirements.txt         # List of Python dependencies
└── .env                     # Environment variables file (not included in version control)
```

## Buy me a coffee

If you find this tool helpful, you can buy me a coffee [here](https://buymeacoffee.com/sahbic) ☕.

## License

This project is licensed under the [MIT License](LICENSE).
