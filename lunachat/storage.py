import json
import streamlit as st
from st_files_connection import FilesConnection

conn = st.connection("s3", protocol="s3", type=FilesConnection)

test_file = "lunaskye-lunachat/test.txt"
system_prompts_file = "lunaskye-lunachat/system_prompts.json"

try:
    _ = conn.read(test_file, input_format="text")
except FileNotFoundError:
    with conn.open(test_file, "wt") as f:
        f.write("This is a test")


def save(path: str, data: dict) -> bool:
    with conn.open(path, "wt") as f:
        json.dump(data, f)


def load(path: str) -> dict:
    json_data = conn.read(path, input_format="text")
    return json.loads(json_data)
