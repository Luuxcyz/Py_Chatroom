import socket
import threading
from datetime import datetime


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 5553))
server.listen()

clients = []
nicknames = []
private_messages = {}
sensitive_words = ['sb', '傻逼', '你妈']


def broadcast(message):
    for client in clients:
        client.send(message)


def private_message(sender, receiver, message):
    sender_client = None
    receiver_client = None
    for client in clients:
        if nicknames[clients.index(client)] == sender:
            sender_client = client
        if nicknames[clients.index(client)] == receiver:
            receiver_client = client

    if sender_client and receiver_client:
        sender_client.send(f'{sender} -> {receiver}: {message}'.encode('utf-8'))
        receiver_client.send(f'{sender} -> {receiver}: {message}'.encode('utf-8'))
    else:
        print(f"私聊失败:{sender} -> {receiver}")


def broadcast_message(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    broadcast(f'系统公告 {timestamp}: {message}\n'.encode('utf-8'))


def send_user_list(client):
    message = "在线用户列表:\n" + "\n".join(nicknames)
    client.send(message.encode('utf-8'))


def handle(client):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')

            if message.startswith('/pm'):
                receiver, content = message[4:].split(' ', 1)
                private_message(nicknames[clients.index(client)], receiver, content)
                continue

            if any(word in message for word in sensitive_words):
                client.send('敏感词被过滤,请勿发送敏感词\n'.encode('utf-8'))
            elif message.endswith('bye'):
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                nicknames.remove(nickname)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                broadcast(f'{timestamp} 用户 {nickname} 退出聊天室!\n'.encode('utf-8'))
                break
            elif message.endswith('/list'):
                send_user_list(client)
            else:
                broadcast(message.encode('utf-8'))
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            broadcast(f'{timestamp} 用户 {nickname} 退出聊天室!\n'.encode('utf-8'))
            break


def receive():
    while True:
        client, address = server.accept()
        print(f"连接成功:{str(address)}")
        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)
        print(f"昵称是:{nickname}!")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        broadcast(f"{timestamp} {nickname} 加入了聊天室!\n".encode('utf-8'))
        client.send('连接到服务器!\n'.encode('utf-8'))
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


thread_receive = threading.Thread(target=receive)
thread_receive.start()

while True:
    message = input("请输入系统公告:")
    broadcast_message(message)
