import socket
import sectors
import sessions
import simp_aes
import rsa
import random
import aes
from message import message
import time
import hashlib
import os

class mlaffon:
    def __init__(self, sessfile, pass_, username, ip):
        self.username = username
        self.mysess = sessions.get_session(open(f'programdata/{sessfile}.sess', 'rb').read(), pass_)
        self.ip = ip
        self.session_key = b''
        self.events = []
        self.friendsname = f'programdata/{username.decode()}fr.txt'
        self.msgsname = f'programdata/{username.decode()}msgs.txt'
        if not os.path.exists('programdata'):
            os.mkdir('programdata')
        if not os.path.exists(self.friendsname):
            open(self.friendsname, 'w').close()
        if not os.path.exists(self.msgsname):
            open(self.msgsname, 'w').close()
        self.chats = sectors.sectorstype(3)
        self.chats.load(self.friendsname)
        self.msgs = sectors.sectorstype(2)
        self.msgs.load(self.msgsname)

    def connect(self):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((self.ip, 2047))

    def recv(self):
        while True:
            dat = self.connection.recv(68157440)
            if dat and self.session_key:
                return simp_aes.aes_full_decrypt(self.session_key, dat)
            if dat:
                return dat

    def send(self, dat):
        if self.session_key:
            self.connection.send(simp_aes.aes_full_encrypt(self.session_key, dat))
        else:
            self.connection.send(dat)

    def auth(self):
        self.connection.send(sectors.write_sectors([self.username, self.mysess[0].save_pkcs1()]))
        info = self.recv()
        if info == b'\x00':
            return -1
        self.session_key = aes.aes(sectors.bytes_to_int(rsa.decrypt(info, self.mysess[1])))
        try:
            chk = self.recv()
            self.send(chk + b'1')
        except Exception as e:
            print(e)
            return -1

    def getpubkey(self, username):
        self.send(sectors.write_sectors([b'\x00', username]))
        data = self.recv()
        if data == b'\x00':
            return -1
        else:
            return rsa.PublicKey.load_pkcs1(data)

    def sndmsg(self, recver, data):
        self.send(sectors.write_sectors([b'\x01', sectors.write_sectors([recver, data])]))

    def getofflinebuf(self):
        while True:
            self.send(sectors.write_sectors([b'\x02', b'\x00']))
            info = self.recv()
            if info == b'\x00':
                break
            self.events.append(info)

    def genmsg(self, msg):
        return message(msg, author_key=self.mysess[1], op=1)

    def checkmsg(self, msg, author_key):
        return message(msg, author_key=author_key, op=0)

    def start_dialog(self, recver):
        pk = self.getpubkey(recver)
        if pk != -1:
            random.seed(int(hashlib.sha256(str(self.mysess[1].e+time.time()).encode()).hexdigest(),16))
            key = sectors.int_to_bytes(random.getrandbits(128))
            msg = rsa.encrypt(key, pk)
            msg = sectors.write_sectors([b'\x00', self.genmsg(msg).compile(), self.username])
            self.sndmsg(recver, msg)
            ind = self.chats.find(1, b'd'+recver)
            if ind == -1:
                self.chats.add([key, b'd'+recver, pk.save_pkcs1()])
                chat = sectors.sectorstype(3)
                chat.add([b'\x00', b'server', self.username + b' started chat'])
                self.msgs.add([b'd'+recver, chat.data])
                self.msgs.save(self.msgsname)
            else:
                self.chats.edit(ind, 0, key)
            return 0
        return 1

    def processevents(self):
        while len(self.events) != 0:
            try:
                event = self.events[0]
                self.events.remove(event)
                code, data, author = sectors.read_sectors(event)
                ind = self.chats.find(1, b'd'+author)
                if code == b'\x00':
                    tmppk = self.getpubkey(author)
                    if tmppk != -1:
                        msg = self.checkmsg(data, author_key=tmppk)
                        key = rsa.decrypt(msg.check(), self.mysess[1])
                        if ind == -1:
                            self.chats.add([key, b'd'+author, rsa.PublicKey.save_pkcs1(tmppk)])
                            chat = sectors.sectorstype(3)
                            chat.add([b'\x00', b'server', author + b' started chat'])
                            self.msgs.add([b'd'+author, chat.data])
                            self.msgs.save(self.msgsname)
                        else:
                            self.chats.edit(ind, 0, key)
                        self.chats.save(self.friendsname)
                if code == b'\x01':
                    if ind == -1:
                        pass
                    else:
                        key = aes.aes(sectors.bytes_to_int(self.chats.getdat(ind, 0)))
                        pk = rsa.PublicKey.load_pkcs1(self.chats.getdat(ind, 2))
                        msg = self.checkmsg(data, author_key=pk)
                        real_data = simp_aes.aes_full_decrypt(key, msg.check())
                        msid = msg.message[1]
                        msgsind = self.msgs.find(0, b'd'+author)
                        tmpdat = self.msgs.getdat(msgsind, 1)
                        readchat = sectors.sectorstype(3)
                        readchat.data = tmpdat
                        if readchat.find(0, msid) == -1:
                            chat = sectors.sectorstype(3)
                            chat.add([msid, author, real_data])
                            if msgsind == -1:
                                self.msgs.add([b'd'+author, chat.data])
                            else:
                                self.msgs.edit(msgsind, 1, tmpdat + chat.data)
                        self.msgs.save(self.msgsname)
            except Exception as e:
                print(e)

    def dialogmsg(self, recver, data):
        ind = self.chats.find(1,b'd'+recver)
        if ind != -1:
            key = aes.aes(sectors.bytes_to_int(self.chats.getdat(ind,0)))
            msg = self.genmsg(simp_aes.aes_full_encrypt(key,data))
            to_send = sectors.write_sectors([b'\x01',msg.compile(),self.username])
            self.sndmsg(recver,to_send)
            msid = msg.message[1]
            msgsind = self.msgs.find(0, b'd'+recver)
            chat = sectors.sectorstype(3)
            chat.add([msid, self.username, data])
            if msgsind == -1:
                self.msgs.add([b'd'+recver, chat.data])
            else:
                tmpdat = self.msgs.getdat(msgsind, 1)
                self.msgs.edit(msgsind, 1, tmpdat + chat.data)
            self.msgs.save(self.msgsname)
            return 0
        return 1

    def makepublicChat(self, password, username):
        chathash = hashlib.sha256(password).hexdigest().encode()
        to_send = sectors.write_sectors([chathash, username])
        self.send(sectors.write_sectors([b'\x03', to_send]))
        code = self.recv()
        if code != b'\x01':
            self.chats.add([password, b'p'+username, b''])
            self.chats.save(self.friendsname)
            return 0
        else:
            return 1

    def savepublicChat(self, password, username):
        usernum = self.chats.find(1, b'p'+username)
        if usernum == -1:
            self.chats.add([password, b'p'+username, b''])
            self.chats.save(self.friendsname)

    def pubchatmsg(self, username, data):
        usernum = self.chats.find(1, b'p'+username)
        if usernum != -1:
            password = self.chats.getdat(usernum, 0)
            chathash = hashlib.sha256(password).hexdigest().encode()
            chat_key = aes.aes(simp_aes.get_chat_key(password))
            msg = self.genmsg(simp_aes.aes_full_encrypt(chat_key, data))

            to_send = sectors.write_sectors([msg.compile(), self.username])
            self.send(sectors.write_sectors([b'\x04', sectors.write_sectors([username, to_send, chathash])]))
            return 0
        else:
            return 1

    def pubchatbuf(self,username):
        usernum = self.chats.find(1,b'p'+username)
        if usernum != -1:
            password = self.chats.getdat(usernum,0)
            chathash = hashlib.sha256(password).hexdigest().encode()
            chat_key = aes.aes(simp_aes.get_chat_key(password))
            msgs = []
            self.send(sectors.write_sectors([b'\x05',sectors.write_sectors([username,chathash])]))
            pkg = self.recv()#msg,susername
            if pkg != b'\x00':
                msgs = sectors.read_sectors(pkg)
                for uspkg in msgs:
                    msg,susername = sectors.read_sectors(uspkg)
                    ind = self.chats.find(1,b'd'+susername)
                    if ind == -1:
                        pk = self.getpubkey(susername)
                        self.chats.add([b'NOT STATED', b'd'+susername, rsa.PublicKey.save_pkcs1(pk)])
                        self.chats.save(self.friendsname)
                        if pk == b'\x00':
                            return 1
                    else:
                        pk = self.chats.getdat(ind,2)
                        pk = rsa.PublicKey.load_pkcs1(pk)
                        
                        
                    msg = self.checkmsg(msg,author_key=pk)
                    real_data = simp_aes.aes_full_decrypt(chat_key,msg.check())
                    
                    msid = msg.message[1]
                    msgsind = self.msgs.find(0,b'p'+username)
                    
                    chat = sectors.sectorstype(3)
                    chat.add([msid,susername,real_data])
                    
                    if msgsind == -1:
                        self.msgs.add([b'p'+username,chat.data])
                    else:
                        tmpdat = self.msgs.getdat(msgsind,1)
                        readchat = sectors.sectorstype(3)
                        readchat.data = tmpdat
                        if readchat.find(0,msid) == -1:
                            self.msgs.edit(msgsind,1,tmpdat+chat.data)
                    self.msgs.save(self.msgsname)
                    
                return 0
            else:
                return 1
                
        else:
            return 1

    
