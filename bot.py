import logging
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, CallbackContext, filters
from config import TELEGRAM_BOT_TOKEN, WHITELIST_CHAT_ID
from github_interaction import get_todo_list, add_task_to_github, mark_task_as_done

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    await update.message.reply_markdown_v2(
        rf"Hi {user.mention_markdown_v2()}\!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Use /list to see the to-do list.\n"
        "Use /add <priority> <task> to add a new task with a given priority.\n"
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

    result = mark_task_as_done(task_index)
    await update.message.reply_text(result)


def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    user_ids = [int(user_id) for user_id in WHITELIST_CHAT_ID.split(",")]
    user_filter = filters.User(user_id=user_ids)

    application.add_handler(CommandHandler("start", start, filters=user_filter))
    application.add_handler(CommandHandler("help", help_command, filters=user_filter))
    application.add_handler(CommandHandler("list", list_command, filters=user_filter))
    application.add_handler(CommandHandler("add", add_command, filters=user_filter))
    application.add_handler(CommandHandler("mark", mark_command, filters=user_filter))

    application.run_polling()


if __name__ == "__main__":
    main()
