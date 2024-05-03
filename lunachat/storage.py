import json, pprint
import streamlit as st
from st_files_connection import FilesConnection

conn = st.connection("s3", protocol="s3", type=FilesConnection)

system_prompts_file = "lunaskye-lunachat/system_prompts.json"
saved_chats_folder = "lunaskye-lunachat/saved_chats/"


def save(path: str, data: dict) -> None:
    with conn.open(path, "wt") as f:
        json_data = json.dumps(data)
        f.write(json_data)


def save_system_prompts(data: dict) -> None:
    save(system_prompts_file, data)


def load(path: str) -> dict:
    json_data = conn.read(path, input_format="text")
    return json.loads(json_data)


def load_system_prompts() -> dict:
    return load(system_prompts_file)


# Verify file
default_json_data = {"default": "You are a helpful assistant."}
try:
    file_data = conn.read(system_prompts_file, input_format="text")
    if not file_data:
        print("File has no content, writing default.")
        save(system_prompts_file, default_json_data)
except FileNotFoundError:
    print("File not found, writing default.")
    save(system_prompts_file, default_json_data)

if __name__ == "__main__":
    data = load(system_prompts_file)
    print(type(data))
    print(data)
