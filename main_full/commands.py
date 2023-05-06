import sectors
import os
import main_full.helpers

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
    
def rms(text):
    return text[1:]

def update(cli):
    cli.getofflinebuf()
    cli.processevents()

def msg_(cli,touser,msg):
    code = cli.dialogmsg(touser, ' '.join(msg).encode())
    if code == 0:
        return '[+] Sent!'
    else:
        return '[-] Not sent'

def dia(cli,dat):
    if not dat:
        return '[-] Please provide a username'
    username = dat[0].encode()
    code = cli.start_dialog(username)
    if code == 0:
        return '[+] Dialog is started. Wait until user will receive it!'
    else:
        return '[-] Not started'

def chats(cli):
    out = []
    for chat in sectors.read_sectors(cli.chats.data):
        chat_data = sectors.read_sectors(chat)
        if chat_data[0] != b'NOT STATED':
            out.append(chat_data[1])
    return out

def mkchat(cli,dat):
    if len(dat) < 2:
        return '[-] Please provide both username and password'
    username, password = dat[0], dat[1]
    code = cli.makepublicChat(password.encode(), username.encode())
    if code == 0:
        return '[+] Success!'
    else:
        return '[-] Chat wasn\'t generated'

def savechat(cli,dat):
    if len(dat) < 2:
        return '[-] Please provide both username and password'
    username, password = dat[0], dat[1]
    cli.savepublicChat(password.encode(), username.encode())
    return '[+] Saved'

def chatmsg(cli,username,message):
    message = ' '.join(message).encode()
    code = cli.pubchatmsg(username, message)
    if code == 0:
        return '[+] Success!'
    else:
        return '[-] Something went wrong'

def updatechat(cli,username):
    code = cli.pubchatbuf(username)
    if code == 1:
        return '[-] Bad request code'
    else:
        return '[+] Succsess'

def read(cli,username):
    usernum = cli.msgs.find(0, username)
    msgs1 = []
    if usernum != -1:
        msgs = sectors.read_sectors(cli.msgs.getdat(usernum, 1))
        for msg in msgs:
            msg = sectors.read_sectors(msg)
            msgs1.append(msg)
        return msgs1
    else:
        return 0#


def select(cli,username):
    while True:
        cmd,dat = main_full.helpers.get_command('[+] '+username.decode()+'@input: ')
        if cmd == 'update':
            if username.startswith(b'd'):
                update(cli)
            else:
                updatechat(cli,rms(username))
            clear()
            msgs = read(cli,username)
            if msgs == 0:
                print('[-] Error while reading chat')
            elif msgs == 1:
                print('[-] Please provide a username')
            else:
                for msg in msgs:
                    try:
                        print('[+] ' + msg[1].decode() + ': ' + msg[2].decode())
                    except:
                        pass
                    
        elif cmd == 'msg':
            if username.startswith(b'd'):
                print(msg_(cli,rms(username),dat))
            else:
                print(chatmsg(cli,rms(username),dat))

        elif cmd == 'help':
            print_selected_help()

        elif cmd == 'exit':
            break
        
def handle_command(cmd, dat, cli):

    if cmd == 'dia':
        print(dia(cli,dat))

    elif cmd == 'chats':
        for en,chat in enumerate(chats(cli)):
            if chat.startswith(b'p'):
                print(f'[{en}] ' + rms(chat.decode()) +' - polylog')
            else:
                print(f'[{en}] ' + rms(chat.decode()) +' - dialog')

    elif cmd == 'mkchat':
        print(mkchat(cli,dat))

    elif cmd == 'savechat':
        print(savechat(cli,dat))

    elif cmd == 'select':
        id_ = int(dat[0])
        username = chats(cli)[id_]
        select(cli,username)

    elif cmd == 'help':
        print_help()

def print_help():
    print('''
[!] select chat_num            * selects chat *
[!] dia username               * starts private chat *
[!] chats                      * tells your chats usernames and nums *
[!] mkchat username password   * makes public chat *
[!] savechat username password * saves public chat *
''')

def print_selected_help():
        print('''
[!] update username            * updates chat *
[!] msg message                * sends message chat *
[!] exit                       * exits selected chat *
''')
