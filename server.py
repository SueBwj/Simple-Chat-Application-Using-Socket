import os
import select
from socket import socket, AF_INET, SOCK_STREAM
import threading
import time
from files import remove_files, save_files, read_files, get_download_files



class Server:
    def __init__(self, host='localhost', port=8010):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.host = host
        self.port = port
        self.clients = {}
        self.usernames = set() # 表示当前在线的user
        self.offline_users = set() # 表示当前离线的user
        # 创建一个线程事件对象，用于控制服务器的停止
        self.stop_event = threading.Event()
        self.groups = {}
        self.bind_and_listen()

    # 绑定和监听
    def bind_and_listen(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        print(f"Server listening on {self.host}:{self.port}")

    # 接受连接
    def accept_connections(self):
        while not self.stop_event.is_set():
            try:
                connection, address = self.sock.accept()
                thread = threading.Thread(target=self.handle_login, args=(connection,))
                thread.start()
            except Exception as e:
                print(f"Error accepting connection: {e}")


    def handle_client(self, connection, username):
        while not self.stop_event.is_set():
            try:
                # 使用 select 来检查连接是否有数据可读，设置超时时间    
                ready = select.select([connection], [], [], 1)
                if ready[0]:
                    data = connection.recv(1024)
                    if not data:
                        # 如果没有接收到数据，说明客户端已断开连接
                        print(f"用户 {username} 断开连接")
                        self.offline_users.add(username)
                        print(self.offline_users)
                        self.remove_client(connection, username)
                        break
                    # 处理接收到的数据
                    if(data.decode() == "/online"):
                        connection.send(f"{str(self.usernames)}".encode())
                    elif(data.decode() == "/offline"):
                        if self.offline_users:
                            connection.send(f"{str(self.offline_users)}".encode())
                        else:
                            connection.send("no offline users\n".encode())
                    elif data.decode().startswith("/leave_message"):
                        _, recipient, message = data.decode().split(' ', 2)
                        save_files(recipient, message)
                    elif data.decode().startswith("/send_private_message"):
                        _, recipient, message = data.decode().split(' ', 2)
                        recipient = eval(recipient)
                        if recipient in self.clients.keys():
                            self.clients[recipient].send(f"{message}\n".encode())
                        else:
                            connection.send(f"{recipient} is not online. Leave a message\n".encode())
                            save_files(recipient, f"{message}")
                    elif data.decode().startswith("/build_group"):
                        _, group_name, user_lists = data.decode().split(' ', 2)
                        self.build_group(connection, group_name, user_lists)
                    elif data.decode().startswith("/check_my_groups"):
                        self.check_my_groups(connection)
                    elif data.decode().startswith("/send_group_message"):
                        _, sender, recipient, message = data.decode().split(' ', 3)
                        self.send_group_message(connection, sender, recipient, message)
                    elif data.decode().startswith("/join_group"):
                        _, sender, recipient = data.decode().split(' ', 2)
                        self.join_group(connection, recipient)
                    elif data.decode().startswith("/get_groups"):
                        self.get_groups(connection)
                    elif data.decode().startswith("/send_file"):
                        _, file_name, file_size = data.decode().split(' ', 2)
                        file_size = int(file_size)
                        self.receive_file(connection, file_name, file_size)
                    elif data.decode().startswith("/get_download_files"):
                        self.get_download_files(connection)
                    elif data.decode().startswith("/download_file"):
                        _, file_name = data.decode().split(' ', 1)
                        self.download_file(connection, file_name)

            except Exception as e:
                print(f"handle client {username} error: {e}")
                self.offline_users.add(username)
                self.remove_client(connection, username)
                self.close_connection(connection)
                break

    # 处理客户端登录
    def handle_login(self, connection):
        if not self.stop_event.is_set():
            try:
                user_name = connection.recv(1024)
                if not user_name:
                    connection.send("user name is empty".encode())
                    self.close_connection(connection)
                    return
                user_name = user_name.decode()
                # 重复登录
                if user_name in self.usernames:
                    connection.send(f"{user_name} already login in\n".encode())
                    self.close_connection(connection)
                    return
                # 重新上线
                elif user_name in self.offline_users:
                    self.offline_users.discard(user_name)
                    self.usernames.add(user_name)
                    # 接收别人的留言
                    messages = read_files(user_name)
                    # 删除已接受的留言
                    remove_files(user_name)
                    connection.send(f"welcome {user_name}, messages: {messages}\n".encode()) 
                # 新用户登录
                else:
                    self.usernames.add(user_name)
                    self.clients[user_name] = connection
                    connection.send(f"online users: {str(self.usernames)}\n".encode())
                    # 登录成功之后开始处理客户端的消息
                    self.handle_client(connection, user_name)
            except Exception as e:
                print(f"处理登录时出错: {e}")
                self.remove_client(connection, user_name)
                self.close_connection(connection)
                return

    def remove_client(self, connection, username):
        if username in self.clients.keys():
            del self.clients[username]
            self.usernames.discard(username)
            print(f'remove {username} from server')
        try:
            connection.close()
        except Exception as e:
            print(f"关闭连接时出错: {e}")

    def build_group(self, connection, group_name:str, user_lists:str):
        # user_lists '[user1, user2, ...]'
        user_lists = eval(user_lists)
        if group_name not in self.groups.keys():
            self.groups[group_name] = []
            for user in user_lists:
                user = eval(user)
                if user in self.clients.keys():
                    self.groups[group_name].append(self.clients[user])
                else:
                    connection.send(f"{user} is not online. Can't build group\n".encode())
                    return
            connection.send(f"Group {group_name} created with users: {', '.join(user_lists)}\n".encode())
        else:
            connection.send(f"Group {group_name} already exists.\n".encode())
    
    def check_my_groups(self, connection):
        if self.groups:
            group_names = []
            for group_name in self.groups.keys():
                if connection in self.groups[group_name]:
                    group_names.append(group_name)
            if group_names:
                connection.send(f"{group_names}".encode())
            else:
                connection.send(f"You are not in any group.\n".encode())
        else:
            connection.send(f"No groups created.\n".encode())

    def send_group_message(self, connection, sender, recipient, message):
        for client in self.groups[recipient]:
            if client != connection:
                client.send(f"from group {recipient}: {sender}: {message}\n".encode())

    def join_group(self, connection, recipient):
        if recipient in self.groups.keys():
            self.groups[recipient].append(connection)
            connection.send(f"You have joined the group: {recipient}\n".encode())
        else:
            connection.send(f"Group {recipient} does not exist.\n".encode())
    
    def get_groups(self, connection):
        connection.send(f"{str(list(self.groups.keys()))}".encode())

    def get_download_files(self, connection):
        connection.send(f"{str(get_download_files())}".encode())
    
    def receive_file(self, connection, file_name, file_size):
        file_path = os.path.join("uploads", file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as file:
            remaining = file_size
            while remaining > 0:
                chunk_size = 4096 if remaining >= 4096 else remaining
                chunk = connection.recv(chunk_size)
                if not chunk:
                    break
                file.write(chunk)
                remaining -= len(chunk)
        print(f"文件 {file_name} 已接收并保存到 {file_path}")
        connection.send(f"文件 {file_name} 已上传成功。\n".encode())
    
    def download_file(self, connection, file_name):
        file_path = os.path.join("downloads", file_name)
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            connection.send(f"{file_size}".encode())

            conformation = connection.recv(1024).decode()
            if conformation == "ready":
                with open(file_path, 'rb') as file:
                    while True:
                        data = file.read(4096)
                        if not data:
                            break
                        connection.sendall(data)
                print(f"file {file_name} has been sent to {connection}")
            else:
                print(f"client {connection} is not ready to receive file {file_name}")
        else:
            connection.send(f"file {file_name} does not exist".encode())

    # 关闭连接
    def close_connection(self, connection):
        connection.close()


    # 停止服务器
    def stop(self):
        self.stop_event.set()
        for client in self.clients.values():
            self.close_connection(client)
        self.clients.clear()
        self.usernames.clear()
        self.sock.close()
        print("Server stopped")


if __name__ == "__main__":
    server = Server()
    # 启动接受连接的线程
    server_thread = threading.Thread(target=server.accept_connections)
    server_thread.start()

    # 主线程等待用户输入来停止服务器
    input("Press Enter to stop the server...")

    # 停止服务器
    server.stop()
    server_thread.join()
    print("Server stopped.")


