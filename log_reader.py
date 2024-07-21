import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the folder to search 
base_folder = r"Z:\EFT\Logs"

# Define the target log file suffix
target_file_suffix = "notifications.log"

# Define the list of target tpl IDs to search for
target_tpl_ids = [
    "5c94bbff86f7747ee735c08f",
    "5c05300686f7746dce784e5d",
    "57347ca924597744596b4e71",
    "56dff216d2720bbd668b4568"
]

# Function to extract JSON objects from a string using a stack
def extract_json_objects(text):
    json_objects = []
    stack = []
    json_buffer = ""
    inside_string = False

    for char in text:
        if char == '"' and (len(stack) == 0 or stack[-1] != '\\'):
            inside_string = not inside_string
        if not inside_string:
            if char == '{':
                stack.append(char)
            elif char == '}':
                if stack:
                    stack.pop()
        json_buffer += char
        if not stack and json_buffer.strip():
            if json_buffer.strip().startswith('{') and json_buffer.strip().endswith('}'):
                try:
                    json_obj = json.loads(json_buffer)
                    json_objects.append(json_obj)
                except json.JSONDecodeError as e:
                    logging.debug(f"Error parsing JSON: {e} - JSON string: {json_buffer}")
            json_buffer = ""

    return json_objects

# Function to get the most recent file or folder
def get_most_recent_folder(base_folder):
    folders = [os.path.join(base_folder, d) for d in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, d))]
    if not folders:
        return None
    most_recent_folder = max(folders, key=os.path.getmtime)
    return most_recent_folder

# Function to recursively search for the log files and parse them
def search_and_parse_logs(base_folder, target_file_suffix, target_tpl_ids):
    most_recent_folder = get_most_recent_folder(base_folder)
    if not most_recent_folder:
        logging.error("No folders found in the specified base directory.")
        return

    logging.info(f"Processing most recent folder: {most_recent_folder}")
    for root, dirs, files in os.walk(most_recent_folder):
        for file in files:
            if file.endswith(target_file_suffix):
                log_file_path = os.path.join(root, file)
                logging.info(f"Processing file: {log_file_path}")
                with open(log_file_path, 'r', encoding='utf-8') as log_file:
                    content = log_file.read()
                    json_objects = extract_json_objects(content)
                    for log_entry in json_objects:
                        if log_entry is not None and isinstance(log_entry, dict):
                            player_visual = log_entry.get('PlayerVisualRepresentation', {})
                            if isinstance(player_visual, dict):
                                equipment = player_visual.get('Equipment', {})
                                if isinstance(equipment, dict):
                                    items = equipment.get('Items', [])
                                    if isinstance(items, list):
                                        for item in items:
                                            if item.get('_tpl') in target_tpl_ids:
                                                logging.info(f"ID {item['_tpl']} found in file {log_file_path}")

# Run the search and parse function
search_and_parse_logs(base_folder, target_file_suffix, target_tpl_ids)
