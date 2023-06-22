import sys
import aes
import os
from simp_aes import *

def old_decrypt(aes_,data:bytes):
    out = []
    for i in range(0,len(data),16):
        out.extend(aes_.dec_once([*data[i:i+16]]))
    return pkcs7unpadding(bytes(out))


if __name__ == '__main__':
    if len(sys.argv) == 3:
        username = sys.argv[1]
        if not os.path.exists(username):
            print('[+] This session doesn\'t exists!')
            sys.exit(0)
            
        password = sys.argv[2].encode()
        key = aes.aes(get_aes_session_password(password),256)
        
        filenames = ['initinf','messages','keybase','rejected','invites','rn']
        for fn in filenames:
            try:
                os.remove(username+'/'+fn+".txt")
                print(f'[+] Old formatted {fn} deleted.')
            except:
                pass

        print('[+] All old formatted files were deleted. They will be recovered after update command')
        print('[+] Session file fixing')
        new_data = old_decrypt(key,open(username+'/'+username,'rb').read())
        open(username+'/'+username,'wb').write(aes_full_encrypt(key,new_data))
        print('[+] Session file fixed!!!')
            
    else:
        print('[-] Use arguments. {session_fixer.py (username) (password)}')
            
        
