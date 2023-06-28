import socks
import sectors
import requests
import platform
import time
import sys

def tor_port():
    if 'wind' in platform.system().lower():
        tor_port = '9150'
    else:
        tor_port = '9050'

    return tor_port

def check_tor():
    try:
        s = socks.socksocket()
        s.bind(('127.0.0.1',int(tor_port())))
        return False
    except Exception as e:
        return True
        
def tor_ip():
    prxy = {'http':'socks5://127.0.0.1:'+tor_port()
            ,'https':'socks5://127.0.0.1:'+tor_port()}
    return requests.get('https://icanhazip.com',proxies=prxy).text[:-1]

def getproxy():
    import proxyconf
    if proxyconf.use_tor:
        if not check_tor():
            print('''[-] TOR is turned off. Plz run:
[!] Orbot if you use android;
[!] Tor browser if you use windows;
[!] Tor service if you use linux.''')
            time.sleep(5)
            sys.exit()
        return ('127.0.0.1',int(tor_port()))
    elif proxyconf.use_socks5:
        return proxyconf.socks5_prox
    
    return None
    
class session:
    def __init__(self,connection=b'',ip='',proxy=None):
        if not ip:
            self.ip = '0.0.0.0'
        else:
            self.ip = ip
        self.connection = connection
        self.sock = socks.socksocket()
        if proxy:
            self.sock.setproxy(socks.PROXY_TYPE_SOCKS5,*proxy)
        

    def recv(self):
        magic_num = self.connection.recv(1)[0]
        dat_len = sectors.bytes_to_int(self.connection.recv(magic_num))
        pkg_max = 536870912
        if dat_len > pkg_max or not dat_len:
            return b''
        full_pkg = self.connection.recv(dat_len)
        return full_pkg

    def send(self,pkg):
        self.connection.send(sectors.write_sector(pkg))
            
    def connect(self,ip,port):
        self.sock.connect((ip,port))
        self.connection = self.sock

    def bind(self):
        self.sock.bind((self.ip,2025))
        self.sock.listen()

    def accept(self):
        self.connection,addr = self.sock.accept()
        return self.connection,addr
