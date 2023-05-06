import hashlib

def pkcs7padding(data:bytes,block_length:int):
    to_add = (len(data)+block_length-1)//block_length*block_length-len(data)
    if to_add == 0:
        to_add = block_length
        
    for i in range(to_add):
        data += bytes([to_add])
    
    return data

def pkcs7unpadding(data:bytes):
    padding_length = data[len(data)-1]
    return data[0:len(data)-padding_length]
                 
def aes_full_encrypt(aes_,data:bytes):
    out = []
    data = pkcs7padding(data,16)
    for i in range(0,len(data),16):
        out.extend(aes_.enc_once([*data[i:i+16]]))
    return bytes(out)

def aes_full_decrypt(aes_,data:bytes):
    out = []
    for i in range(0,len(data),16):
        out.extend(aes_.dec_once([*data[i:i+16]]))
    return pkcs7unpadding(bytes(out))


def get_aes_session_password(key):
    return int(hashlib.sha256(key+b'salt').hexdigest(),16)

def bit_padding(data:bytes,block_length:int):
    to_add = (len(data)+block_length-1)//block_length*block_length-len(data)
    if to_add == 0:
        to_add = block_length
    to_add -= 1
    data += b'\x01'
    data += b'\x00'*to_add
    return data


def bit_unpadding(data:bytes):
    return data[0:data.rfind(b'\x01')]

def get_chat_key(pass_):
    return int(hashlib.sha256(hashlib.md5(pass_*2+b'salt').hexdigest().encode()).hexdigest(),16)%340282366920938463463374607431768211456