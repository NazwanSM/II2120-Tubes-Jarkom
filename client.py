import customtkinter as ctk
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import socket
import random
import time

# Setting up customtkinter theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

CORRECT_PASSWORD = "1234"
attempts = 0

root = ctk.CTk()
root.title("Chat Room")
root.geometry("600x450")

def custom_dialog(title, prompt, is_password=False):
    dialog = ctk.CTkToplevel(root)
    dialog.title(title)
    
    dialog_width = 300
    dialog_height = 150
    
    # Ensure root window is updated
    root.update_idletasks()
    
    # Calculate center position
    root_x = root.winfo_rootx()
    root_y = root.winfo_rooty()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    
    x_position = root_x + (root_width // 2 - dialog_width // 2)
    y_position = root_y + (root_height // 2 - dialog_height // 2)
    
    dialog.geometry(f"{dialog_width}x{dialog_height}+{x_position}+{y_position}")
    
    label = ctk.CTkLabel(dialog, text=prompt, font=("Helvetica", 12))
    label.pack(pady=(10, 5))
    
    result_var = tk.StringVar(dialog)
    entry = ctk.CTkEntry(dialog, width=200, height=40, textvariable=result_var, show='*' if is_password else '')
    entry.pack(pady=(0, 10))
    
    def close_dialog(event=None):  # Tambahkan parameter event untuk mendukung binding
        result_var.set(entry.get())
        dialog.destroy()
    
    submit_button = ctk.CTkButton(dialog, text="Submit", command=close_dialog)
    submit_button.pack(pady=(5, 10))
    
    entry.bind('<Return>', close_dialog)
    dialog.bind('<Return>', close_dialog)
    
    entry.focus()
    dialog.grab_set()  # Make dialog modal
    dialog.wait_window()
    
    return result_var.get()

# Setup chat log with improved visibility
chat_log = ScrolledText(root, font=('Helvetica', 14), height=20, width=80, bg='#2C2F33', fg='#C4C4C4', wrap=tk.WORD)
chat_log.grid(row=0, column=0, columnspan=2, padx=10, pady=12, sticky='nsew')
chat_log.config(state=tk.DISABLED)

# Configure chat log tags
chat_log.tag_configure('message', foreground='#FFFFFF', font=('Helvetica', 14))
chat_log.tag_configure('broadcast', foreground='#FFFF00', font=('Helvetica', 14), justify='center')
chat_log.tag_configure('history', foreground='#888888', font=('Helvetica', 14))

# Initialize client socket with error handling
try:
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_ip = custom_dialog("Server IP", "Enter server IP address:")
    client_ip = custom_dialog("Client IP", "Enter client IP address:")
    client.bind((client_ip, random.randint(8000, 9000)))
except Exception as e:
    error_label = ctk.CTkLabel(root, text=f"Connection error: {e}", text_color="red")
    error_label.grid(row=2, column=0, columnspan=2)

def send_message(event=None):
    message = message_entry.get().strip()
    if message:
        try:
            client.sendto(f"{username}: {message}".encode('utf-8'), (server_ip, 9999))
            message_entry.delete(0, tk.END)
        except Exception as e:
            update_chat_log(f"Error sending message: {e}\n", "broadcast")

def update_chat_log(decoded_message, tag="message"):
    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, decoded_message + "\n", tag)
    chat_log.see(tk.END)  # Auto-scroll to bottom
    chat_log.config(state=tk.DISABLED)

def receive_messages():
    while True:
        try:
            message, _ = client.recvfrom(1024)
            decoded_message = message.decode('utf-8')
            
            if "HISTORY_TAG:" in decoded_message:
                history_message = decoded_message.replace("HISTORY_TAG:", "")
                root.after(0, update_chat_log, history_message, "history")
            else:
                timestamp = time.strftime("%H:%M")
                if "has joined the room!" in decoded_message:
                    root.after(0, update_chat_log, decoded_message, "broadcast")
                else:
                    formatted_message = f"[{timestamp}] {decoded_message}"
                    root.after(0, update_chat_log, formatted_message, "message")
        except Exception as e:
            root.after(0, update_chat_log, f"Connection error: {e}\n", "broadcast")
            break

# Setup message entry and send button
message_entry = ctk.CTkEntry(root, placeholder_text="Type your message here...", width=400, height=50)
message_entry.grid(row=1, column=0, padx=10, pady=10, sticky='ew')

send_button = ctk.CTkButton(root, text="Send", height=50, command=send_message)
send_button.grid(row=1, column=1, padx=10, pady=10)

message_entry.bind("<Return>", send_message)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

def request_password():
    global attempts
    error_label = ctk.CTkLabel(root, text="", text_color="red", font=("Helvetica", 12))
    error_label.grid(row=2, column=0, columnspan=2)

    while attempts < 3:
        password = custom_dialog("Password", "Enter room password:", is_password=True)
        if password == CORRECT_PASSWORD:
            error_label.grid_remove()
            return True
        else:
            error_label.configure(text=f"Wrong password! {2-attempts} attempts remaining")
            root.update()
            attempts += 1
    
    return False

def request_username_and_password():
    global username
    while True:
        username = custom_dialog("Username", "Enter your username:")
        password = custom_dialog("Password", "Enter your password:", is_password=True)
        if username and password:
            # Kirim username dan password ke server untuk pendaftaran
            client.sendto(f"SIGNUP_TAG:{username}:{password}".encode('utf-8'), (server_ip, 9999))
            # Tunggu respons dari server
            response, _ = client.recvfrom(1024)
            if response.decode('utf-8') == "USERNAME_TAKEN":
                update_chat_log("Username already taken, please choose another.", "broadcast")
            else:
                break  # Username diterima

def request_login():
    global username
    while True:
        username = custom_dialog("Username", "Enter your username:")
        password = custom_dialog("Password", "Enter your password:", is_password=True)
        if username and password:
            # Kirim login ke server
            client.sendto(f"LOGIN_TAG:{username}:{password}".encode('utf-8'), (server_ip, 9999))
            # Tunggu respons dari server
            response, _ = client.recvfrom(1024)
            if response.decode('utf-8') == "LOGIN_SUCCESS":
                break  # Login berhasil
            else:
                update_chat_log("Login failed. Please check your username and password.", "broadcast")

if request_password():  # Meminta password untuk masuk ke chat room
    request_username_and_password() # Untuk login jika pendaftaran gagal

    if username:
        # Send signup message and start receiving thread
        try:
            client.sendto(f"SIGNUP_TAG:{username}".encode('utf-8'), (server_ip, 9999))
            thread = threading.Thread(target=receive_messages)
            thread.daemon = True
            thread.start()
        except Exception as e:
            update_chat_log(f"Connection error: {e}\n", "broadcast")

root.mainloop()