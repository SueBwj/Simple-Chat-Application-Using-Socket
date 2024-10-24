import os

def save_files(username, message):
    path = os.path.join(os.getcwd(), "messages")
    if not os.path.exists(path):
        os.makedirs(path)
    with open(os.path.join(path, f"{username}_messages.txt"), "a") as f:
        f.write(f"{message}\n")


def read_files(username:str):
    username = f"'{username}'"
    file_path = os.path.join(os.getcwd(), "messages")
    if os.path.exists(os.path.join(file_path, f"{username}_messages.txt")):
        with open(os.path.join(file_path, f"{username}_messages.txt"), "r") as f:
            return f.read()
    return ""

def remove_files(username:str):
    username = f"'{username}'"
    file_path = os.path.join(os.getcwd(), "messages")
    if os.path.exists(os.path.join(file_path, f"{username}_messages.txt")):
        os.remove(os.path.join(file_path, f"{username}_messages.txt"))

def get_download_files() -> list:  
    file_path = os.path.join(os.getcwd(), "downloads")
    if not os.path.exists(file_path):
        os.makedirs(file_path)
        return []
    files = []
    for file in os.listdir(file_path):
        if os.path.isfile(os.path.join(file_path, file)):
            files.append(file)
    return files

