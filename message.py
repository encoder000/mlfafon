import rsa
import time
from sectors import *
import random

class message:
    def __init__(self,message:bytes,author_key=None,op=0):
        self.author_key = author_key
        if op == 0:
            self.message = read_sectors(message)
        else:
            random.seed(int(time.time())^bytes_to_int(message))
            self.id_ = random.randbytes(32)
            self.message = [message,self.id_,rsa.sign(message+self.id_,author_key,'SHA-256')]

    def check(self):
        try:
            if rsa.verify(self.message[0]+self.message[1],self.message[2],self.author_key):
                return self.message[0]
                
        except Exception as e:
            print(e)
            return False

    def compile(self):
        return write_sectors(self.message)