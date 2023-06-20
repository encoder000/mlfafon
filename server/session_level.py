import socket
import sectors

class session:
    def __init__(self,connection=b'',ip=''):
        if not ip:
            self.ip = '0.0.0.0'
        else:
            self.ip = ip
        self.connection = connection
        self.sock = socket.socket()
        

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
