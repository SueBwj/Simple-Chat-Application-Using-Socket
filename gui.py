import tkinter as tk
from client import Client


class GUIServices:
    
    @staticmethod
    def on_username_entry_click(event, default_text):
        if event.widget.get() == default_text:
            event.widget.delete(0, tk.END)
            event.widget.config(fg='black')

    @staticmethod
    def on_username_entry_focusout(event, default_text):
        if not event.widget.get():
            event.widget.insert(0, default_text)
            event.widget.config(fg='grey')
    
    @staticmethod
    def show_message(message:str, chat_display):
        chat_display.config(state='normal')
        chat_display.insert(tk.END, message)
        chat_display.config(state='disabled')
        chat_display.see(tk.END)

    @staticmethod
    def create_selection_window(root, title='pick a user', width=300, height=200):
        selection_window = tk.Toplevel(root)
        selection_window.title(title)
        selection_window.geometry(f'{width}x{height}')
        return selection_window
    
    @staticmethod
    def create_listbox(selection_window, options:list, selectmode=tk.SINGLE):
        listbox = tk.Listbox(selection_window, selectmode=selectmode, font=('Arial', 10))
        for option in options:
            listbox.insert(tk.END, option)
        listbox.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        return listbox
    
    @staticmethod
    def create_confirm_button(selection_window, command):
        confirm_button = tk.Button(selection_window, text="confirm", command=command,
                                bg='#28a745', fg='white', font=('Arial', 10, 'bold'),
                                padx=10, pady=5, bd=0, relief=tk.FLAT,
                                activebackground='#218838', activeforeground='white',
                                cursor='hand2')
        confirm_button.pack(padx=20, pady=10)
        return confirm_button


class GUI:
    def __init__(self):
        # 创建主窗口
        self.options = ["online users", "offline users", "leave message", "send a private message", "join a group", "check my groups", "send a group message", "build a group", "send a file", "download a file"]
        self.isleave_message = False
        self.issend_private_message = False
        self.ischeck_my_groups = False
        self.isbuild_group = False
        


        self.client = Client(update_callback=self.update_chat_display)
        
        self.root = tk.Tk()
        self.root.title("Chat Room")
        self.root.geometry('600x400')
        self.root.config(background='#F5F5F5')
        

        # 创建标题标签
        title_label = tk.Label(self.root, text="聊天室~~", fg='#384857',
                               font=('Times', 23, 'bold italic underline'))
        title_label.pack(side="top")

        # 创建聊天显示区域
        self.chat_display = tk.Text(
            self.root, state='disabled', height=15)
        self.chat_display.pack(pady=10)

        # 创建用户名输入框和标签
        self.username_frame = tk.Frame(self.root)
        self.username_frame.pack(pady=5)

        username_label = tk.Label(self.username_frame, text="user:",
                                 font=('Arial', 10))
        username_label.pack(side=tk.LEFT, padx=(0, 5))

        self.username_entry = tk.Entry(self.username_frame, width=30, font=('Arial', 10), fg='#333333')
        self.username_entry.pack(side=tk.LEFT)
        self.default_text = "please input your username"
        self.username_entry.insert(0, self.default_text)
        self.username_entry.bind("<FocusIn>", lambda e: GUIServices.on_username_entry_click(e, self.default_text))
        self.username_entry.bind("<FocusOut>", lambda e: GUIServices.on_username_entry_focusout(e, self.default_text))

        self.login_button = tk.Button(self.username_frame, text="login", command=self.handle_login,
                                    bg='#4169E1', fg='white', font=('Arial', 10, 'bold'),
                                    padx=8, pady=3, bd=0, relief=tk.FLAT,
                                    activebackground='#1E90FF', activeforeground='white',
                                    cursor='hand2')
        self.login_button.pack(side=tk.RIGHT)

        # 添加鼠标悬停效果
        self.login_button.bind("<Enter>", lambda e: e.widget.config(bg='#1E90FF'))
        self.login_button.bind("<Leave>", lambda e: e.widget.config(bg='#4169E1'))

        # 创建消息输入框和发送按钮（初始隐藏）
        self.message_frame = tk.Frame(self.root)
        self.message_entry = tk.Entry(self.message_frame, width=50, font=('Arial', 10))
        self.message_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.send_button = tk.Button(self.message_frame, text="send", command=self.handle_send,
                                     bg='#28a745', fg='white', font=('Arial', 10, 'bold'),
                                     padx=8, pady=3, bd=0, relief=tk.FLAT,
                                     activebackground='#218838', activeforeground='white',
                                     cursor='hand2')
        self.send_button.pack(side=tk.LEFT)

        # 添加鼠标悬停效果
        self.send_button.bind("<Enter>", lambda e: e.widget.config(bg='#218838'))
        self.send_button.bind("<Leave>", lambda e: e.widget.config(bg='#28a745'))

        # 查看用户状态 -- function frame
        self.function_frame = tk.Frame(self.root)
        self.menu_buttons  = tk.Button(self.function_frame, text="menu", command=self.handle_menu, 
                                    bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'),
                                    padx=10, pady=5, bd=0, relief=tk.RAISED,
                                    activebackground='#45a049', activeforeground='white',
                                    cursor='hand2')
        # 添加圆角效果
        self.menu_buttons.config(borderwidth=0, highlightthickness=0)
        self.menu_buttons.pack(side=tk.LEFT, padx=(0, 20))

        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_chat_display(self, message, option=None):
        if option == "online":
            self.online_users = message
        elif option == "offline":
            self.offline_users = message
        elif option == "check_my_groups":
            self.groups = message
        elif option == "get_groups":
            self.groups = message
        elif option == "get_download_files":
            self.download_files = message
        else:
            GUIServices.show_message(message, self.chat_display)

    # 登录事件
    def handle_login(self):
        username = self.username_entry.get()
        if username and username != self.default_text:
            self.client.login(username)
            # 登录成功后隐藏用户名框架
            self.username_frame.pack_forget()
            # 显示消息输入框架
            self.message_frame.pack(pady=5)
            self.function_frame.pack(pady=5)

    # 发送消息事件
    def handle_send(self):
        if self.isleave_message:
            """
            给离线用户留言
            """
            self.client.leave_message(self.username_entry.get(),self.selecte_user, self.message_entry.get())
            GUIServices.show_message(f"leave message to {self.selecte_user}\n\n", self.chat_display)
            # 清除选择的用户，以便下次使用
            del self.selecte_user
            # 清空消息输入框
            self.message_entry.delete(0, tk.END)
            self.isleave_message = False
        elif self.issend_private_message:
            """
            发送私聊消息
            """
            self.client.send_private_message(self.username_entry.get(), self.selecte_user, self.message_entry.get())
            GUIServices.show_message(f"send private message to {self.selecte_user}\n\n", self.chat_display)
            # 清除选择的用户，以便下次使用
            del self.selecte_user
            # 清空消息输入框
            self.message_entry.delete(0, tk.END)
            self.issend_private_message = False
        elif self.isbuild_group:
            """
            创建群组
            """
            self.client.build_group(self.username_entry.get(), self.selecte_user , self.message_entry.get())
            del self.selecte_user
            self.message_entry.delete(0, tk.END)
            self.isbuild_group = False
        elif self.issend_group_message:
            """
            发送群组消息
            """
            self.client.send_group_message(self.username_entry.get(), self.selecte_user, self.message_entry.get())
            GUIServices.show_message(f"send group message to group: {self.selecte_user}\n\n", self.chat_display)
            del self.selecte_user
            self.message_entry.delete(0, tk.END)
            self.issend_group_message = False
        else:
            message = self.message_entry.get()
            if message:
                self.client.send_message(message)
                self.message_entry.delete(0, tk.END)
            else:
                GUIServices.show_message("you must input your message\n\n", self.chat_display)
    

    def handle_menu(self):
        selection_window = GUIServices.create_selection_window(self.root,title='pick an option',height=300)
        listbox = GUIServices.create_listbox(selection_window, self.options)
        confirm_button = GUIServices.create_confirm_button(selection_window, lambda: self.confirm_selection(selection_window, listbox))

    # 查看在线用户
    def handle_online_users(self, show_message=True):
        self.client.get_online_users()
        # 等待获取在线用户的操作完成
        while not hasattr(self, 'online_users'):
            pass
        if show_message:
            GUIServices.show_message(f"online users: {self.online_users}\n\n", self.chat_display)
        else:
            return self.online_users

    # 查看离线用户
    def handle_offline_users(self, show_message=True):
        self.client.get_offline_users()
        # 等待获取离线用户的操作完成
        while not hasattr(self, 'offline_users'):
            pass
        if show_message:
            GUIServices.show_message(f"offline users: {self.offline_users}\n\n", self.chat_display)
        else:
            return self.offline_users

    # 聊天
    def handle_chat(self):
        online_users = self.client.get_online_users()
        online_users = online_users.strip('{}').split(',')
        if not online_users:
            GUIServices.show_message("no online users\n\n", self.chat_display)
            return
    
    # 选择用户
    def selected_user(self, selection_window, listbox, is_multiple=False, is_download_file=False):
        selected_indices = listbox.curselection()
        if not selected_indices:
            if is_download_file:
                GUIServices.show_message("please pick a file\n\n", self.chat_display)
            else:
                GUIServices.show_message("please pick at least one user\n\n", self.chat_display)
            return
        if is_multiple:
            self.selecte_user = [listbox.get(index) for index in selected_indices]
        else:
            self.selecte_user = listbox.get(selected_indices[0])
        selection_window.destroy()
    

    def handle_leave_message(self):
        self.isleave_message = True
        # 获取离线用户
        offline_users = self.handle_offline_users(show_message=False)
        if not offline_users:
            GUIServices.show_message("no offline users\n\n", self.chat_display)
            return
        offline_users = offline_users.strip('{}').split(',')
        selection_window = GUIServices.create_selection_window(self.root,title='pick a user',height=300)
        listbox = GUIServices.create_listbox(selection_window, offline_users)
        confirm_button = GUIServices.create_confirm_button(selection_window, lambda: self.selected_user(selection_window, listbox))
        
        # 等待选择窗口关闭
        self.root.wait_window(selection_window)
        
        # 在选择窗口关闭后执行以下代码
        if hasattr(self, 'selecte_user') and self.selecte_user:
            GUIServices.show_message(f"please input your message\n\n", self.chat_display)
        else:
            GUIServices.show_message("you must pick a user\n\n", self.chat_display)
        

    def handle_send_private_message(self):
        self.issend_private_message = True
        online_users = self.handle_online_users(show_message=False)
        online_users = online_users.strip('{}').split(',')
        online_users_list = []
        for online_user in online_users:
            if not online_user.strip() == f"'{self.username_entry.get()}'":
                online_users_list.append(online_user.strip())
        if not online_users_list:
            GUIServices.show_message("no online users\n\n", self.chat_display)
            return
        selection_window = GUIServices.create_selection_window(self.root,title='pick a user',height=300)
        listbox = GUIServices.create_listbox(selection_window, online_users_list)
        confirm_button = GUIServices.create_confirm_button(selection_window, lambda: self.selected_user(selection_window, listbox))

        # 等待选择窗口关闭
        self.root.wait_window(selection_window)

        if hasattr(self, 'selecte_user') and self.selecte_user:
            GUIServices.show_message(f"please input your message\n\n", self.chat_display)
        else:
            GUIServices.show_message(f"you must pick a user\n\n", self.chat_display)
            

    def handle_check_my_groups(self, show=True):
        self.ischeck_my_groups = True
        self.client.check_my_groups()
        while not hasattr(self, 'groups'):
            pass
        if show:
            GUIServices.show_message(f"groups: {self.groups}\n\n", self.chat_display)

    def handle_send_group_message(self):
        self.issend_group_message = True
        if not hasattr(self, 'groups'):
            self.handle_check_my_groups(show=False)

        if self.groups:
            groups = eval(self.groups)
            selection_window = GUIServices.create_selection_window(self.root,title='pick a group',height=300)
            listbox = GUIServices.create_listbox(selection_window, groups)
            confirm_button = GUIServices.create_confirm_button(selection_window, lambda: self.selected_user(selection_window, listbox))
        
        self.root.wait_window(selection_window)

        if hasattr(self, 'selecte_user') and self.selecte_user:
            GUIServices.show_message(f"please input your message\n\n", self.chat_display)
        else:
            GUIServices.show_message(f"you must pick a group\n\n", self.chat_display)


    def handle_build_group(self):
        self.isbuild_group = True
        online_users = self.handle_online_users(show_message=False)
        online_users = online_users.strip('{}').split(',')
        online_users_list = []
        for online_user in online_users:
            if not online_user.strip() == f"'{self.username_entry.get()}'":
                online_users_list.append(online_user.strip())
        if not online_users_list:
            GUIServices.show_message("no online users\n\n", self.chat_display)
            return
        selection_window = GUIServices.create_selection_window(self.root,title='pick users',height=300)
        listbox = GUIServices.create_listbox(selection_window, online_users_list, selectmode=tk.MULTIPLE)
        confirm_button = GUIServices.create_confirm_button(selection_window, lambda: self.selected_user(selection_window, listbox, is_multiple=True))

        self.root.wait_window(selection_window)

        if hasattr(self, 'selecte_user') and self.selecte_user:
            GUIServices.show_message(f"please input your group name\n\n", self.chat_display)
        else:
            GUIServices.show_message(f"you must pick at least one user\n\n", self.chat_display)

    def handle_join_group(self):
        self.isjoin_group = True
        self.client.get_groups()
        while not hasattr(self, 'groups'):
            pass
        
        if self.groups:
            groups = eval(self.groups)
            selection_window = GUIServices.create_selection_window(self.root,title='pick a group',height=300)
            listbox = GUIServices.create_listbox(selection_window, groups)
            confirm_button = GUIServices.create_confirm_button(selection_window, lambda: self.selected_user(selection_window, listbox))

            self.root.wait_window(selection_window)

            if hasattr(self, 'selecte_user') and self.selecte_user:
                self.client.join_group(self.username_entry.get(), self.selecte_user)
            else:
                GUIServices.show_message(f"you must pick a group\n\n", self.chat_display)

    def handle_send_file(self):
        self.issend_file = True
        self.client.send_file()

    
    def get_download_files(self):
        self.client.get_download_files()

    def handle_download_file(self):
        self.isdownload_file = True
        # 选择要下载的文件
        self.get_download_files()
        while not hasattr(self, 'download_files'):
            pass
        if self.download_files:
            download_files = eval(self.download_files)
            selection_window = GUIServices.create_selection_window(self.root,title='pick a file',height=300)
            listbox = GUIServices.create_listbox(selection_window, download_files)
            confirm_button = GUIServices.create_confirm_button(selection_window, lambda: self.selected_user(selection_window, listbox))
        
            self.root.wait_window(selection_window)

            if hasattr(self, 'selecte_user') and self.selecte_user:
                self.client.download_file(self.selecte_user)
            else:
                GUIServices.show_message(f"you must pick a file\n\n", self.chat_display)

    

    # 确认按钮
    def confirm_selection(self, selection_window, listbox):
        selected_indices = listbox.curselection()
        if not selected_indices:
            GUIServices.show_message("please pick a option\n\n", self.chat_display)
            return
        selected_option = listbox.get(selected_indices[0])
        selection_window.destroy()
        if selected_option == "online users":
            self.handle_online_users()
        elif selected_option == "offline users":
            self.handle_offline_users()
        elif selected_option == "leave message":
            self.handle_leave_message()
        elif selected_option == "send a private message":
            self.handle_send_private_message()
        elif selected_option == "check my groups":
            self.handle_check_my_groups()
        elif selected_option == "send a group message":
            self.handle_send_group_message()
        elif selected_option == "build a group":
            self.handle_build_group()
        elif selected_option == "send a file":
            self.handle_send_file()
        elif selected_option == "join a group":
            self.handle_join_group()
        elif selected_option == "download a file":
            self.handle_download_file()

    # 关闭事件
    def on_closing(self):
        self.client.close_connection()
        self.root.destroy()

if __name__ == "__main__":
    gui = GUI()
    gui.root.mainloop()
