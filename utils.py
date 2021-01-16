import base64

def encode_to_base64_string(msg: str) -> str:
    msg_bytes = msg.encode('utf-8')
    base64_bytes = base64.b64encode(msg_bytes)
    return base64_bytes.decode('utf-8')

def decode_to_base64_string(msg: str) -> str:
    msg_bytes = msg.encode('utf-8')
    base64_bytes = base64.b64decode(msg_bytes)
    return base64_bytes.decode('utf-8')
