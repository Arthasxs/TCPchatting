import socket
import select

HEADER_LENGTH = 10
IP = "127.0.0.1"  # 监听所有可用的接口
PORT = 1234

# 创建一个socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 设置选项，以便可以立即重新连接
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# 绑定IP和端口
server_socket.bind((IP, PORT))

# 监听新的连接
server_socket.listen()

# 用来存储socket对象的列表
sockets_list = [server_socket]
clients = {}

print(f'监听 {IP}:{PORT}...')

# 处理消息的函数
def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            return False

        message_length = int(message_header.decode().strip())
        return {"header": message_header, "data": client_socket.recv(message_length)}

    except:
        return False

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()

            user = receive_message(client_socket)
            if user is False:
                continue

            sockets_list.append(client_socket)
            clients[client_socket] = user

            print('接受新连接来自 {}:{}, 用户名: {}'.format(*client_address, user['data'].decode()))

        else:
            message = receive_message(notified_socket)

            if message is False:
                print('关闭连接来自: {}'.format(clients[notified_socket]['data'].decode()))
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            user = clients[notified_socket]
            print(f'收到消息来自 {user["data"].decode()}: {message["data"].decode()}')

            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]

