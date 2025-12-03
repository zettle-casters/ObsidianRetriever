import hashlib

def text_hash(text : str) -> str:
    hash = hashlib.new('sha256')
    hash.update(text.encode())
    return hash.hexdigest()
