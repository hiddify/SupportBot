from .base64 import base64url_decode, base64url_encode
import json


def encode(action, data):
    return f"{action}_{base64url_encode(json.dumps(data))}"


def decode(txt: str):
    if not txt:
        return None
    txt = txt.removeprefix("start").removeprefix("/start").strip()
    splt = txt.split("_", 2)
    action = splt[0]
    
    data = json.loads(base64url_decode(splt[1])) if len(splt)==2 else {}
    return action, data


def decode_if_action(txt: str, action: str):
    if not txt:
        return None
    txt = txt.removeprefix("start").removeprefix("/start").strip()
    if not txt.startswith(action):
        return None
    txt = txt.removeprefix(f"{action}_").strip()
    return json.loads(base64url_decode(txt))
