import json, pprint
import streamlit as st
from st_files_connection import FilesConnection

conn = st.connection("s3", protocol="s3", type=FilesConnection)

system_prompts_file = "lunaskye-lunachat/system_prompts.json"


def save(path: str, data: dict) -> bool:
    with conn.open(path, "wt") as f:
        json.dump(data, f)


def load(path: str) -> dict:
    json_data = conn.read(path, input_format="text")
    return json.loads(json_data)


# Verify file
default_json_data = json.dumps({"default": "You are a helpful assistant."})
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
    print(data)
