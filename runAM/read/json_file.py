import json
import sys
from runAM.tools.find import file_full_path

def json_file(json_file_name):
    try:
        with open(file_full_path(json_file_name)[0]) as f:
            return json.load(f)
    except Exception as e:
        sys.exit(f'ERROR: Can not load the JSON file {json_file_name} due to following error:\n{e}')
