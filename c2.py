# 导入所需的模块
import socket
import tkinter as tk

# 设置常量
HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234

# 输入用户名
my_username = input("用户名: ")

# 创建客户端套接字并连接到服务器
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

# 编码用户名并发送到服务器
username = my_username.encode("utf-8")
username_header = f"{len(username):<{HEADER_LENGTH}}".encode("utf-8")
client_socket.send(username_header + username)

# 创建Tkinter根窗口
root = tk.Tk()
root.title("Chat Room")

# 创建消息显示框
messages_frame = tk.Frame(root)
my_msg = tk.StringVar()  # 用于输入消息
my_msg.set("在这里输入消息.")
scrollbar = tk.Scrollbar(messages_frame)  # 用于浏览消息

msg_list = tk.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
msg_list.pack(side=tk.LEFT, fill=tk.BOTH)
msg_list.pack()
messages_frame.pack()

# 创建消息输入框
entry_field = tk.Entry(root, textvariable=my_msg)
entry_field.pack()

# 定义发送消息的函数
def send_message(event=None):
    message = my_msg.get()
    my_msg.set("")  # 清空输入框
    if message:
        message = message.encode("utf-8")
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")
        client_socket.send(message_header + message)
        msg_list.insert(tk.END, f'{my_username} > {message.decode("utf-8")}')

# 创建发送按钮并绑定发送消息函数
send_button = tk.Button(root, text="发送", command=send_message)
send_button.pack()
root.bind("<Return>", send_message)  # 绑定回车键发送消息

# 定义接收消息的函数
def receive_message():
    while True:
        try:
            username_header = client_socket.recv(HEADER_LENGTH)
            if not len(username_header):
                print("连接被服务器关闭")
                break

            username_length = int(username_header.decode().strip())
            username = client_socket.recv(username_length).decode("utf-8")

            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode().strip())
            message = client_socket.recv(message_length).decode("utf-8")

            msg_list.insert(tk.END, f'{username} > {message}')

        except BlockingIOError:
            break

    root.after(100, receive_message)  # 100毫秒后继续接收消息

# 开始接收消息
root.after(100, receive_message)
tk.mainloop()  # 启动Tkinter事件循环

