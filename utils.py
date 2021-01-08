import base64

def encode_to_base64_string(msg: str) -> str:
    msg_bytes = msg.encode('ascii')
    base64_bytes = base64.b64encode(msg_bytes)
    return base64_bytes.decode('ascii')

def decode_to_base64_string(msg: str) -> str:
    msg_bytes = msg.encode('ascii')
    base64_bytes = base64.b64decode(msg_bytes)
    return base64_bytes.decode('ascii')
