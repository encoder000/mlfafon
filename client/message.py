import rsa
import time
from sectors import *
import random

class message:
    def __init__(self,message:bytes,username:bytes=None,author_key=None,op=0):
        self.author_key = author_key
        if op == 0:
            self.message = read_sectors(message)
        else:
            random.seed(int(time.time())+random.randint(0,500))
            self.id_ = random.randbytes(32)
            self.message = [message,self.id_,rsa.sign(message+self.id_+username,author_key,'SHA-256'),username]

    def check(self):
        try:
            if rsa.verify(self.message[0]+self.message[1]+self.message[3],self.message[2],self.author_key):
                return [self.message[3],self.message[0],self.message[1]]
                
        except Exception as e:
            return False

    def compile(self):
        return write_sectors(self.message)
