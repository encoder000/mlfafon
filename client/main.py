import colorama
import updater
import client
import os
import platform
import keygen

colorama.init()
WHITE = colorama.Fore.WHITE
RED = colorama.Fore.LIGHTRED_EX
GREEN  = colorama.Fore.LIGHTGREEN_EX

def clear():
    if 'wind' in platform.system().lower():
        os.system('cls')
    else:
        os.system('clear')

def ascer(byte):
    try:
        return byte.decode()
    except:
        return str(byte)[2:-1]

def check_args(args,l):
    if len(args) < l:
        print(RED+'[-] Not enoght args. Should be'+WHITE,l)
        return 1
    return 0

ip = input('[?] Ip(default 185.117.155.43): ')

if not ip:
    ip = '185.117.155.43'

dirs = ['datadir','datadir/'+ip]
for i in dirs:
    if not os.path.exists(i):
        os.mkdir(i)
        
accounts = os.listdir('datadir/'+ip+'/')

seed = None

v0='[0] Make new account'
v1='[1] Recover by seed phrase'
    
print(GREEN+v0+'\n'+v1+'\n'+'\n'.join([f'[{e+2}] Log in as '+i for e,i in enumerate(accounts)])+WHITE)
variant = int(input('[?] Select variant : '))
    
if variant == 0:
    username = input('[?] Username: ')
        
elif variant == 1:
    seed = input('[?] Seed: ')
    username = input('[?] Username: ')
    print('[+] Run update after recovering an account!')
        
else:
    username = accounts[variant-2]
    
usr = client.User(ip,username,input('[?] Password: ').encode(),'datadir/'+ip+'/',seed)
if usr.seed:
    print('[+] Your seed phrase is "'+usr.seed+'". You can recover your session using it!')
code = usr.auth()


if not usr.checkcode(code):
    print(RED+'[-] '+usr.deccode(usr.auth,code)+WHITE)
    
while True:
    cmd = input('[?] Cmd: ').split()
    if len(cmd) > 0:
        cmd,args = cmd[0],cmd[1:]
        if cmd == 'help':
            print(GREEN+'''
[!] help   -   *shows help*                         - no arguments
[!] chats  -   *shows all your chats and indexes*   - no arguments
[!] join   -   *joins chat*                         - username password
[!] select -   *selects chat*                       - chat index
[!] mkchat -   *makes chat*                         - username password
[!] exit   -   *exits select mode*                  - no arguments
[!] invite -   *invites user*                       - user & chat usernames
[!] update -   *loads all info from server*         - no arguments 
[!] invites-   *shows your invites to reject|accept*- no arguments
[!] accept -   *accepts invite to some chat*        - index in invites
[!] reject -   *rejects invite to some chat*        - index in invites
    
    '''+WHITE)
        elif cmd == 'chats':
            print(GREEN+'\n'.join([f'[{e}] {ascer(i)}' for e,i in enumerate(usr.initinf.fields(0))])+WHITE)
            
        elif cmd == 'join':
            if check_args(args,2):
                continue
            username,password = args[0],args[1]
            code = usr.join_chat(username.encode(),password.encode())
            if not usr.checkcode(code):
                print(RED+'[-] '+usr.deccode(usr.join_chat,code)+WHITE)
                
        elif cmd == 'mkchat':
            if check_args(args,2):
                continue
            username,password = args[0],args[1]
            code = usr.mkchat(username.encode(),password.encode())
            if not usr.checkcode(code):
                print(RED+'[-] '+usr.deccode(usr.mkchat,code)+WHITE)
               
                
        elif cmd == 'invite':
            if check_args(args,2):
                continue
            u0,u1 = args[0],args[1]
            code = usr.send_invite(u0.encode(),u1.encode())
            if not usr.checkcode(code):
                print(RED+'[-] '+usr.deccode(usr.send_invite,code)+WHITE)
               

        elif cmd == 'update':
            usr.read_buffer()
            print(GREEN+'[+] updated'+WHITE)
            
        elif cmd == 'select':
            if check_args(args,1):
                continue
            
            chat_username = usr.initinf.fields(0)[int(args[0])]
            while True:
                clear()
                usr.read_buffer()
                print(GREEN+'\n'.join([f'{ascer(a)}: {ascer(m)}' for a,m in usr.get_messages(chat_username)])+WHITE)
                cmd = input(GREEN+'[+] Message: ')
                if len(cmd) > 0:
                    if cmd == 'exit':
                        ___ = input('[?] Are you shure to exit?(y/n): ')
                        if ___ == 'y':
                            break
                        else:
                            code = usr.send_message(chat_username,b'exit')
                            if not usr.checkcode(code):
                                print(RED+'[-] '+usr.deccode(usr.send_message,code)+WHITE)
               
                    else:
                        code = usr.send_message(chat_username,cmd.encode())
                        if not usr.checkcode(code):
                            print(RED+'[-] '+usr.deccode(usr.send_message,code)+WHITE)
               

        elif cmd == 'invites':
            print(GREEN+'\n'.join([f'[{e}] {ascer(i)}' for e,i in enumerate(usr.invites.fields(0))])+WHITE)

        elif cmd == 'accept':
            if check_args(args,1):
                continue
            sector_num = int(args[0])
            usr.join_chat(usr.invites.getdat(sector_num,0),usr.invites.getdat(sector_num,1))
            usr.invites.rem(sector_num)
            usr.invites.save()
            

        elif cmd == 'reject':
            if check_args(args,1):
                continue
            sector_num = int(args[0])
            username = usr.invites.getdat(sector_num,0)
            usr.invites.rem(sector_num)
            usr.rejected.add([username])
            usr.rejected.save()
            usr.invites.save()
                    

                    
                        
