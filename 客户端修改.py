import socket
import threading
from tkinter import *
from datetime import datetime

nickname = ""
private_windows = {}

def receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == 'NICK':
                client.send(nickname.encode('utf-8'))
            elif message.startswith('PRIVATE'):
                _, sender, receiver, content = message.split(' ', 3)
                if receiver == nickname:
                    if sender in private_windows:
                        private_windows[sender].insert(END, f'{sender}: {content}\n')
                    else:
                        create_private_window(sender)
            else:
                text_area.insert(END, message + '\n')
        except:
            text_area.insert(END, "连接断开！\n")
            client.close()
            break

def send_message(event=None):
    global nickname
    message = message_entry.get()
    message_entry.delete(0, END)
    if message == 'bye':
        client.send(f'{nickname}: {message}'.encode('utf-8'))
        text_area.insert(END, "你已退出聊天室！\n")
        client.close()
    elif message.startswith('/pm'):
        _, receiver, content = message.split(' ', 2)
        if receiver == nickname:
            text_area.insert(END, "不能与自己私聊！\n")
        else:
            client.send(f'PRIVATE {nickname} {receiver} {content}'.encode('utf-8'))
            if receiver in private_windows:
                private_windows[receiver].insert(END, f'{nickname}: {content}\n')
            else:
                create_private_window(receiver)
    else:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        client.send(f'{nickname} {timestamp}: {message}'.encode('utf-8'))

def create_private_window(receiver):
    private_window = Toplevel(root)
    private_window.title(f'Private Chat - {receiver}')

    private_text_area = Text(private_window)
    private_text_area.pack()

    private_message_entry = Entry(private_window)
    private_message_entry.pack()

    def send_private_message(event=None):
        message = private_message_entry.get()
        private_message_entry.delete(0, END)
        client.send(f'PRIVATE {nickname} {receiver} {message}'.encode('utf-8'))
        private_text_area.insert(END, f'{nickname}: {message}\n')

    private_message_entry.bind("<Return>", send_private_message)
    private_windows[receiver] = private_text_area

def login():
    global nickname
    ip = ip_entry.get()
    port = int(port_entry.get())
    nickname = id_entry.get()

    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip, port))
    client.send(nickname.encode('utf-8'))

    login_frame.pack_forget()
    chat_frame.pack()

    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    message_entry.bind("<Return>", send_message)

root = Tk()
login_frame = Frame(root)
login_frame.pack()

Label(login_frame, text="IP:").grid(row=0, column=0)
ip_entry = Entry(login_frame)
ip_entry.grid(row=0, column=1)

Label(login_frame, text="端口:").grid(row=1, column=0)
port_entry = Entry(login_frame)
port_entry.grid(row=1, column=1)

Label(login_frame, text="ID:").grid(row=2, column=0)
id_entry = Entry(login_frame)
id_entry.grid(row=2, column=1)

login_button = Button(login_frame, text="登录", command=login)
login_button.grid(row=3, columnspan=2)

chat_frame = Frame(root)

text_area = Text(chat_frame)
text_area.pack()

message_entry = Entry(chat_frame)
message_entry.pack()

send_button = Button(chat_frame, text="发送", command=send_message)
send_button.pack()

root.mainloop()