import logging
import base64
import requests
import os
from dotenv import load_dotenv
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, CallbackContext, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Import environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
TODO_FILE_PATH = os.getenv("TODO_FILE_PATH")
WHITELIST_CHAT_ID = os.getenv("WHITELIST_CHAT_ID")


def get_todo_list():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{TODO_FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    response_json = response.json()
    if response.status_code == 200:
        content = base64.b64decode(response_json["content"]).decode("utf-8")
        tasks = content.strip().split("\n")
        sorted_tasks = sorted(tasks, key=lambda x: int(x.split(":")[0]))
        formatted_tasks = [f"{i+1}: {task}" for i, task in enumerate(sorted_tasks)]
        return "\n".join(formatted_tasks)
    else:
        return "Error fetching the to-do list."


def add_task_to_github(priority, task):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{TODO_FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    # Get the current file content
    response = requests.get(url, headers=headers)
    response_json = response.json()

    if response.status_code == 200:
        sha = response_json["sha"]
        content = base64.b64decode(response_json["content"]).decode("utf-8")
        new_content = content + f"{priority}:{task}\n"

        # Update the file content on GitHub
        encoded_content = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")
        update_data = {
            "message": "Add task: {task}",
            "content": encoded_content,
            "sha": sha,
        }

        update_response = requests.put(url, headers=headers, json=update_data)
        if update_response.status_code == 200:
            return "Task added successfully."
        else:
            return "Error adding task to the to-do list."
    else:
        return "Error fetching the to-do list."


def mark_task_as_done(task_index):
    """
    Mark a task as done by removing it from the GitHub file content.
    """
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{TODO_FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    # Get the current file content
    response = requests.get(url, headers=headers)
    response_json = response.json()

    if response.status_code == 200:
        sha = response_json["sha"]
        content = base64.b64decode(response_json["content"]).decode("utf-8")
        tasks = content.split("\n")
        # Remove empty strings
        tasks = [task for task in tasks if task != ""]

        # Sort tasks by priority
        tasks = sorted(tasks, key=lambda x: int(x.split(":")[0]))

        if 1 <= task_index <= len(tasks):
            completed_task = tasks[task_index - 1].strip()

            # Remove the task from the list
            tasks.remove(tasks[task_index - 1])

            # Join the remaining tasks back into a string
            new_content = "\n".join(tasks)

            # Update the file content on GitHub
            encoded_content = base64.b64encode(new_content.encode("utf-8")).decode(
                "utf-8"
            )
            update_data = {
                "message": f"Mark task as done: {completed_task}",
                "content": encoded_content,
                "sha": sha,
            }

            update_response = requests.put(url, headers=headers, json=update_data)
            if update_response.status_code == 200:
                print(f"Task marked as done: {completed_task}")
            else:
                print("Failed to update the task list.")
        else:
            print("Invalid task number.")


async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    await update.message.reply_markdown_v2(
        rf"Hi {user.mention_markdown_v2()}\!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Use /list to see the to-do list.\n"
        "Use /add <priority> <task> to add a new task with a given priority."
        "Use /mark <task number> to mark a task as done."
    )


async def list_command(update: Update, context: CallbackContext) -> None:
    todo_list = get_todo_list()
    await update.message.reply_text(todo_list)


async def add_command(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /add <priority> <task>")
        return

    try:
        priority = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Priority must be a number.")
        return

    task = " ".join(context.args[1:])
    result = add_task_to_github(priority, task)
    await update.message.reply_text(result)


async def mark_command(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /mark <task number>")
        return

    try:
        task_index = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Task number must be a number.")
        return

    mark_task_as_done(task_index)
    await update.message.reply_text(f"Task {task_index} marked as done.")


def main() -> None:
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # get comma separated list of user ids from env
    user_ids = [int(user_id) for user_id in WHITELIST_CHAT_ID.split(",")]
    user_filter = filters.User(user_id=user_ids)

    # Add command handlers with user filtering
    application.add_handler(CommandHandler("start", start, filters=user_filter))
    application.add_handler(CommandHandler("help", help_command, filters=user_filter))
    application.add_handler(CommandHandler("list", list_command, filters=user_filter))
    application.add_handler(CommandHandler("add", add_command, filters=user_filter))
    application.add_handler(CommandHandler("mark", mark_command, filters=user_filter))

    # Start the Bot
    application.run_polling()


if __name__ == "__main__":
    main()
