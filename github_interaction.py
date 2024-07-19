import os
import base64
import requests
from config import GITHUB_REPO, GITHUB_TOKEN, TODO_FILE_PATH, LOG_FILE_NAME
import datetime

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}


def read_github_file(file_path):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        response_json = response.json()
        sha = response_json["sha"]
        content = base64.b64decode(response_json["content"]).decode("utf-8")
        return sha, content
    else:
        raise Exception(f"Error fetching the file {file_path} from GitHub.")


def write_github_file(file_path, sha, content, message):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    data = {
        "message": message,
        "content": encoded_content,
        "sha": sha,
    }
    response = requests.put(url, headers=HEADERS, json=data)
    if response.status_code != 200:
        raise Exception(f"Error writing to the file {file_path} on GitHub.")


def log_action(action, file_path):
    try:
        sha, log_content = read_github_file(LOG_FILE_NAME)
    except Exception:
        sha, log_content = None, ""  # File may not exist initially

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_name = os.path.basename(TODO_FILE_PATH)
    new_log_entry = f"{timestamp} - {file_name}  - {action} (from bot)\n"
    updated_log_content = log_content + new_log_entry

    if sha:
        write_github_file(
            LOG_FILE_NAME, sha, updated_log_content, f"Log action: {action}"
        )
    else:
        write_github_file(
            LOG_FILE_NAME, "", updated_log_content, f"Log action: {action}"
        )


def get_todo_list():
    try:
        _, content = read_github_file(TODO_FILE_PATH)
        tasks = content.strip().split("\n")
        sorted_tasks = sorted(tasks, key=lambda x: int(x.split(":")[0]))
        formatted_tasks = [f"{i+1}: {task}" for i, task in enumerate(sorted_tasks)]
        # log_action("Fetched to-do list", TODO_FILE_PATH)
        return "\n".join(formatted_tasks)
    except Exception as e:
        # log_action(f"Error fetching to-do list: {e}")
        return str(e)


def add_task_to_github(priority, task):
    try:
        sha, content = read_github_file(TODO_FILE_PATH)
        new_content = content + f"{priority}:{task}\n"
        write_github_file(TODO_FILE_PATH, sha, new_content, f"Add task: {task}")
        log_action(f"Added task: {task} with priority {priority}", TODO_FILE_PATH)
        return "Task added successfully."
    except Exception as e:
        log_action(f"Error adding task: {e}")
        return str(e)


def mark_task_as_done(task_index):
    try:
        sha, content = read_github_file(TODO_FILE_PATH)
        tasks = content.split("\n")
        tasks = [task for task in tasks if task != ""]
        tasks = sorted(tasks, key=lambda x: int(x.split(":")[0]))

        if 1 <= task_index <= len(tasks):
            completed_task = tasks.pop(task_index - 1).strip()
            new_content = "\n".join(tasks) + "\n"
            write_github_file(
                TODO_FILE_PATH, sha, new_content, f"Mark task as done: {completed_task}"
            )
            log_action(f"Marked task as done: {completed_task}", TODO_FILE_PATH)
            return f"Task marked as done: {completed_task}"
        else:
            log_action("Invalid task number")
            return "Invalid task number."
    except Exception as e:
        log_action(f"Error marking task as done: {e}")
        return str(e)
