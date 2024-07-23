import base64

def base64url_encode(input_string):
    # Convert string to bytes
    byte_string = input_string.encode('utf-8')
    
    # Encode bytes to Base64
    base64_bytes = base64.b64encode(byte_string)
    
    # Convert Base64 bytes to string and replace characters for Base64url
    base64_string = base64_bytes.decode('utf-8')
    base64url_string = base64_string.replace('+', '-').replace('/', '_').rstrip('=')
    
    return base64url_string


import base64

def base64url_decode(base64url_string):
    # Replace Base64url characters with Base64 characters
    base64_string = base64url_string.replace('-', '+').replace('_', '/')
    
    # Add padding if necessary
    padding = '=' * (4 - len(base64_string) % 4)
    base64_string += padding
    
    # Decode Base64 string to bytes
    base64_bytes = base64_string.encode('utf-8')
    byte_string = base64.b64decode(base64_bytes)
    
    # Convert bytes back to string
    decoded_string = byte_string.decode('utf-8')
    
    return decoded_string

