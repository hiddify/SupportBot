from urllib.parse import parse_qs
from .base64 import base64url_decode, base64url_encode
import json


def encode(action, data):
    code="&".join([f'{k}={v}' for k,v in data.items()])
        
    return f"{action}_{base64url_encode(code)}"


def decode(txt: str):
    if not txt:
        return None
    txt = txt.removeprefix("start").removeprefix("/start").strip()
    splt = txt.split("_", 2)
    action = splt[0]
    if len(splt)!=2: return action, {}
    items=base64url_decode(splt[1]).split("&")
    
    
    return action, {e.split("=")[0]:e.split("=")[1] for e in items}

