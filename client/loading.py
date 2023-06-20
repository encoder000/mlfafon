import threading
import sys
import time

class load:
    def __init__(self,full,str_):
        self.full = full
        self.str_ = str_
        self.num = 0
        
    def write(self):
        sys.stdout.write("\r"+f'[+] {self.num}/{self.full}'+self.str_)
        sys.stdout.flush()
