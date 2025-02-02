import json
import sys
import runAM.tools.find

def read(json_file_name):
    try:
        with open(runAM.tools.find.file_full_path(json_file_name)[0], mode='r') as json_file:
            return json.load(json_file)
    except Exception as e:
        sys.exit(f'ERROR: Can not load the JSON file {json_file_name} due to following error:\n{e}')
