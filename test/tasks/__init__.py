import json
import os
from typing import Dict, Any


def get_mocker_response(path: str, file_name: str, extension: str = 'json') -> Dict[str, Any]:
    dir_path = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(dir_path, f'mocker/{path}/{file_name}.{extension}')) as f:
        return json.load(f)
