import threading
from socket import *
from customtkinter import *

class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('400x350')
        self.label = None
        self.entry = None
        self.save_btn = None
        self.avatar_label = None
        self.avatar_entry = None
        
        self.menu_frame = CTkFrame(self, width=30, height=350)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)
        
        self.is_show_menu = False
        self.speed_animate_menu = -5
        
        self.btn = CTkButton(
            self, text='▶️', command=self.toggle_show_menu, width=30)
        self.btn.place(x=0, y=0)
        
        self.chat_field = CTkTextbox(self, font=(
            'Arial', 14, 'bold'), state='disabled')
        self.chat_field.place(x=0, y=0)
        
        self.message_entry = CTkEntry(
            self, placeholder_text='Введіть повідомлення:', height=40)
        self.message_entry.place(x=0, y=0)
        
        self.send_button = CTkButton(
            self, text='>', width=50, height=40, command=self.send_message)
        self.send_button.place(x=0, y=0)

        self.username = 'P1nokio' 
        self.avatar = '😎'  # Аватарка по умолчанию (эмодзи)
        
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('2.tcp.eu.ngrok.io', 13090))
            hello = f"TEXT@{self.avatar} {self.username}@[SYSTEM] {self.avatar} {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"Не вдалося підключитися до сервера: {e}")

        self.adaptive_ui()

    def save_profile(self):
        if self.entry and self.avatar_entry:
            new_name = self.entry.get().strip()
            new_avatar = self.avatar_entry.get().strip()
            
            if new_name:
                self.username = new_name
            if new_avatar:
                self.avatar = new_avatar

            # Отправляем сообщение всем, что профиль обновлен
            sys_msg = f"TEXT@{self.avatar} {self.username}@[SYSTEM] оновив(ла) профіль на {self.avatar} {self.username}\n"
            try:
                self.sock.sendall(sys_msg.encode('utf-8'))
            except:
                pass

    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.speed_animate_menu *= -1
            self.btn.configure(text='▶️')
            self.show_menu()
        else:
            self.is_show_menu = True
            self.speed_animate_menu *= -1
            self.btn.configure(text='◀️')
            self.show_menu()
            
            self.label = CTkLabel(self.menu_frame, text='Імʼя')
            self.label.pack(pady=(20, 2))
            
            self.entry = CTkEntry(self.menu_frame)
            self.entry.insert(0, self.username)
            self.entry.pack(pady=2, padx=5)

            self.avatar_label = CTkLabel(self.menu_frame, text='Аватарка (значок):')
            self.avatar_label.pack(pady=(10, 2))

            self.avatar_entry = CTkEntry(self.menu_frame)
            self.avatar_entry.insert(0, self.avatar)
            self.avatar_entry.pack(pady=2, padx=5)
            
            self.save_btn = CTkButton(
                self.menu_frame, 
                text='Зберегти', 
                width=100, 
                command=self.save_profile
            )
            self.save_btn.pack(pady=10)

    def show_menu(self):
        self.menu_frame.configure(
            width=self.menu_frame.winfo_width() + self.speed_animate_menu)
        if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
            self.after(10, self.show_menu)
        elif self.menu_frame.winfo_width() >= 40 and not self.is_show_menu:
            self.after(10, self.show_menu)
            if self.label:
                self.label.destroy()
            if self.entry:
                self.entry.destroy()
            if self.avatar_label:
                self.avatar_label.destroy()
            if self.avatar_entry:
                self.avatar_entry.destroy()
            if self.save_btn:
                self.save_btn.destroy()
                
            self.label = None
            self.entry = None
            self.avatar_label = None
            self.avatar_entry = None
            self.save_btn = None

    def adaptive_ui(self):
        self.menu_frame.configure(height=self.winfo_height())
        self.chat_field.place(x=self.menu_frame.winfo_width())
        self.chat_field.configure(width=max(1, self.winfo_width() - self.menu_frame.winfo_width()),
        height=max(1, self.winfo_height() - 40))
        self.send_button.place(x=self.winfo_width() - 50,
        y=self.winfo_height() - 40)
        self.message_entry.place(
        x=self.menu_frame.winfo_width(), y=self.send_button.winfo_y())
        self.message_entry.configure(
        width=max(1, self.winfo_width() - self.menu_frame.winfo_width() - self.send_button.winfo_width()))

        self.after(50, self.adaptive_ui)

    def add_message(self, text):
        self.chat_field.configure(state='normal')
        self.chat_field.insert(END, text + '\n')
        self.chat_field.configure(state='disabled')

    def send_message(self):
        message = self.message_entry.get()
        if message:
            data = f"TEXT@{self.avatar} {self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode('utf-8'))
            except:
                pass
        self.message_entry.delete(0, END)

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode('utf-8')

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        if hasattr(self, 'sock'):
            self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        msg_type = parts[0]

        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                self.add_message(f"{author}: {message}")
        elif msg_type == "IMAGE":
            if len(parts) >= 4:
                author = parts[1]
                filename = parts[2]
                self.add_message(
                    f"{author} надіслав(ла) зображення: {filename}")
        else:
            self.add_message(line)

win = MainWindow()
win.mainloop()