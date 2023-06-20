from simp_aes import *
import rsa
import aes
import sectors
import lz4.frame

def get_session(data, key):
    aes_class = aes.aes(get_aes_session_password(key), 256)
    key_pair = sectors.read_sectors(lz4.frame.decompress(aes_full_decrypt(aes_class, data)))
    key_pair[0] = rsa.PublicKey.load_pkcs1(key_pair[0])
    key_pair[1] = rsa.PrivateKey.load_pkcs1(key_pair[1])
    key_pair = tuple(key_pair)
    return key_pair

def gen_session(key):
    aes_class = aes.aes(get_aes_session_password(key), 256)
    my_key_pair = rsa.newkeys(4096)
    acc_pubkey, acc_privkey = my_key_pair
    acc_pubkey = acc_pubkey.save_pkcs1()
    acc_privkey = acc_privkey.save_pkcs1()
    return aes_full_encrypt(aes_class, lz4.frame.compress(sectors.write_sector(acc_pubkey) + sectors.write_sector(acc_privkey)))