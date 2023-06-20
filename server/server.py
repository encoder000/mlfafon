import session_level
from simp_aes import *
import sectors
import rsa
import threading
import aes
import random
import time

global users
global polylogs

users = sectors.sectorstype('users.txt')
polylogs = sectors.sectorstype('polylogs.txt')
users.load()
polylogs.load()

class User:
    def __init__(self,conn):
        self.conn = conn
        self.session_key = 0
        self.sector_num = -1
        self.randomizer = random.SystemRandom()
        self.recved = 0
        self.user_thread()

    def recv(self):
        data = self.conn.recv()
        while not data:
            data = self.conn.recv()
        if self.session_key:
            data = aes_full_decrypt(self.session_key,data)
        self.recved += 1 
        if self.recved >= 30:
            self.recved = 0
            time.sleep(4)
            print('sleeping')
        return data

    def send(self,data,l=False):
        if l:
            data = sectors.write_sectors(data)
        if self.session_key:
            data = aes_full_encrypt(self.session_key,data)
        self.conn.send(data)
    
    def user_thread(self):
        print(self.conn.connection)
        while True:
            data = sectors.read_sectors(self.recv())
            
            if not self.session_key:
                rsa_key,username = data
                rsa_key = rsa.PublicKey.load_pkcs1(rsa_key)
                if len(bin(rsa_key.n)[2:]) == 4096 and len(username) < 64:
                    print('reg start')
                    session_key = self.randomizer.randbytes(16)
                    encrypted_session_key = rsa.encrypt(session_key,rsa_key)
                    user_secnum = users.find(0,username)
                    print('sharing session key')
                    self.send(encrypted_session_key)
                    self.session_key = sectors.bytes_to_int(session_key)
                    print(self.session_key)
                    self.session_key = aes.aes(self.session_key)

                    if user_secnum == -1:
                        users.add([username,rsa_key.save_pkcs1()])
                        users.save()
                    else:
                        if rsa_key.save_pkcs1() != users.getdat(users.find(0,username),1):
                            print("HACKER ATTACK")
                            self.send(b'\x01')
                            self.conn.connection.close()
                            break
                    self.send(b'\x00')
                    self.sector_num = users.find(0,username)
                    self.username = username
                else:
                    self.conn.connection.close()

            else:
                #0 - mkchat: username,password
                #1 - join_chat: username,password
                #2 - getpubkey: username
                #3 - invite: recver_username,encrypted_string<1024
                #4 - message: chat_username,message
                #5 - buff_lenght
                #6 - read_buff
                
                print(data[0])
                if data[0] == b'\x00':
                    username,chathash = data[1], data[2]
                    if polylogs.find(0,username) == -1:
                        polylogs.add([username,chathash])
                        self.send(b'\x00')
                    else:
                        self.send(b'\x01')
                    

                elif data[0] == b'\x01':
                    username,chathash = data[1], data[2]
                    secnum = polylogs.find(0,username)
                    if secnum != -1 and len(username) < 64:
                        if polylogs.getdat(secnum,1) == chathash:
                            if not self.username in sectors.read_sectors(polylogs.getdat(secnum,2)):
                                polylogs.add_to_field(secnum,2,sectors.write_sector(self.username))
                                self.send(b'\x00')
                            else:
                                self.send(b'\x03')
                        else:
                            self.send(b'\x01')
                    else:
                        self.send(b'\x02')

                elif data[0] == b'\x02':
                    username = data[1]
                    secnum = users.find(0,username)
                    if secnum != -1:
                        self.send(users.getdat(secnum,1))
                    else:
                        self.send(b'\x01')

                elif data[0] == b'\x03':
                    username,chathash,chat_username,enc_pass = data[1], data[2], data[3], data[4]
                    secnum = users.find(0,username)
                    chat_secnum = polylogs.find(0,chat_username)
                    if secnum != -1:
                        if polylogs.getdat(chat_secnum,1) == chathash and chat_secnum != -1 and len(enc_pass) == 512:
                            intel_field = users.intel_field_get(secnum,2)
                            if intel_field.find(1,chat_username) == -1:
                                intel_field.add([b'\x00',chat_username,enc_pass])
                                users.intel_field_set(secnum,2,intel_field)
                                self.send(b'\x00')
                            else:
                                self.send(b'\x03')
                        else:
                            self.send(b'\x01')
                    else:
                        self.send(b'\x02')

                elif data[0] == b'\x04':
                    chat_username,message = data[1],data[2]
                    secnum = polylogs.find(0,chat_username)
                    if secnum != -1:
                        chat_subs = sectors.read_sectors(polylogs.getdat(secnum,2))
                        if self.username in chat_subs:
                            for i in chat_subs:
                                user_secnum = users.find(0,i)
                                intel_field = users.intel_field_get(user_secnum,2)
                                intel_field.add([b'\x01',chat_username,message])
                                users.intel_field_set(user_secnum,2,intel_field)
                            self.send(b'\x00')
                        else:
                            self.send(b'\x01')
                    else:
                        self.send(b'\x02')

                elif data[0] == b'\x05':
                    intel_field = users.intel_field_get(self.sector_num,2)
                    self.send(sectors.int_to_bytes(len(sectors.read_sectors(intel_field.data))))

                elif data[0] == b'\x06':
                    index = sectors.bytes_to_int(data[1])
                    intel_field = users.intel_field_get(self.sector_num,2)
                    intel_field_data = sectors.read_sectors(intel_field.data)
                    if len(intel_field_data) > index:
                        self.send(intel_field_data[index])
                    else:
                        self.send(b'\x01')
                        
                elif data[0] == b'\x07':
                    username = data[1]
                    chat_usernames = sectors.read_sectors(polylogs.getdat(polylogs.find(0,username),2))
                    if self.username in chat_usernames:
                        self.send(b'\x00')
                    else:
                        self.send(b'\x01')

                polylogs.save()
                users.save()
                    

session = session_level.session()
print(session.ip)
session.bind()
while True:
    conn,addr = session.accept()
    conn = session_level.session(conn)
    threading.Thread(target=User,args=(conn,)).start()
