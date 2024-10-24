import os
from socket import socket, AF_INET, SOCK_STREAM
import threading
from tkinter import filedialog

class Client:
    def __init__(self, host='localhost', port=8010, update_callback=None):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.host = host
        self.port = port
        self.username = ""
        self.running = True
        self.is_online = False
        self.is_offline = False
        self.is_check_my_groups = False
        self.is_get_groups = False
        self.is_download_file = False
        self.is_get_download_files = False
        self.current_download_file = ""
        self.update_callback = update_callback
        self.connect()
        self.start_listening()

    def connect(self):
        self.sock.connect((self.host, self.port))

    def start_listening(self):
        listen_thread = threading.Thread(target=self.listen_to_server, daemon=True)
        listen_thread.start()
    
    def listen_to_server(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode()
                if self.is_download_file:
                    self.receive_file(message)
                elif (self.is_online and message) or (self.is_offline and message):
                    self.update_callback(message, option="online" if self.is_online else "offline")
                    self.is_online = False
                    self.is_offline = False
                elif self.is_check_my_groups and message:
                    self.update_callback(message, option='check_my_groups')
                    self.is_check_my_groups = False
                elif self.is_get_groups and message:
                    self.update_callback(message, option='get_groups')
                    self.is_get_groups = False
                elif self.is_get_download_files and message:
                    self.update_callback(message, option='get_download_files')
                    self.is_get_download_files = False
                else:
                    self.update_callback(message)
            except Exception as e:
                print("stop listening:", e)
                break

    def login(self, username):
        """
        用户输入用户名，登录到服务器
        return: [online users] if success else ''
        """
        self.username = username
        self.sock.send(self.username.encode())

    
    def leave_message(self,sender,recipient, message):
        """
        给指定用户发送离线消息
        """
        message = f"{sender}->{recipient}:{message}"
        self.sock.send(f"/leave_message {recipient} {message}".encode())

    
    def send_private_message(self,sender,recipient, message):
        """
        给指定用户发送私聊消息
        """
        recipient = recipient.strip()
        sender = sender.strip()
        message = f"{sender}->{recipient}:{message}"
        self.sock.send(f"/send_private_message {recipient} {message}".encode())

    
    def get_online_users(self):
        """
        获取在线用户
        return: [online users] if success else ''
        """
        self.is_online = True
        self.sock.send("/online".encode())
        

    def get_offline_users(self):
        """
        获取离线用户
        return: [offline users] if success else ''
        """
        self.is_offline = True
        self.sock.send("/offline".encode())

    def build_group(self, user_name, user_lists, group_name):
        """
        创建群组
        """
        user_lists.append(f"'{user_name}'") # 加入自己
        self.sock.send(f"/build_group {group_name} {user_lists}".encode())

    def check_my_groups(self):
        """
        检查自己所在的群组
        """
        self.is_check_my_groups = True
        self.sock.send(f"/check_my_groups".encode())
    
    def send_group_message(self, sender, recipient, message):
        """
        给指定群组发送消息
        """
        self.sock.send(f"/send_group_message {sender} {recipient} {message}".encode())
    
    def join_group(self, sender, recipient):
        """
        加入指定群组
        """
        self.sock.send(f"/join_group {sender} {recipient}".encode())
    
    def get_groups(self):
        """
        获取所有群组
        """
        self.is_get_groups = True
        self.sock.send(f"/get_groups".encode())

    def send_file(self):
        """
        发送文件
        """
        file_path = filedialog.askopenfilename(title="选择要上传的文件", filetypes=[("All files", "*.*")])
        if file_path:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            try:
                # 发送文件信息
                self.sock.send(f"/send_file {file_name} {file_size}".encode())
                # 发送文件数据
                with open(file_path, 'rb') as file:
                    while True:
                        bytes_read = file.read(4096)
                        if not bytes_read:
                            break
                        self.sock.sendall(bytes_read)
                print(f"file {file_name} has been uploaded to server")
                self.update_callback(f"you have uploaded file: {file_name}")
            except Exception as e:
                print(f"upload file error: {e}")
                self.update_callback(f"upload file {file_name} failed")
    
    def get_download_files(self):
        """
        获取下载文件
        """
        self.is_get_download_files = True
        self.sock.send(f"/get_download_files".encode())
    
    def receive_file(self, initial_message):
        """
        接收文件
        """
        try:
            # 解析文件大小
            file_size = int(initial_message)
            # 发送确认信号
            self.sock.send("ready".encode())

            received_size = 0
            download_path = os.path.join(os.getcwd(), "downloads", "client")
            os.makedirs(download_path, exist_ok=True)
            file_name = self.current_download_file

            with open(os.path.join(download_path, file_name), 'wb') as file:
                while received_size < file_size:
                    data = self.sock.recv(4096)
                    if not data:
                        break
                    file.write(data)
                    received_size += len(data)
            self.update_callback(f"you have downloaded file: {file_name}")

        except Exception as e:
            print(f"receive file error: {e}")
            self.update_callback(f"download file {file_name} failed")
        finally:
            self.is_download_file = False

    def download_file(self, file_name):
        """
        下载文件
        """
        
        self.is_download_file = True
        self.current_download_file = file_name
        
        try:
            self.sock.send(f"/download_file {file_name}".encode())

        except Exception as e:
            print(f"download file error: {e}")
            self.update_callback(f"download file {file_name} failed")


    def close_connection(self):
        self.sock.close()
        print("Connection closed.")

