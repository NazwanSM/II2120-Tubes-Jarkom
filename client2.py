import customtkinter as ctk
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import socket
import random
import time

# Mengatur tema dan tampilan customtkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

CORRECT_PASSWORD = "mysecretpassword"
attempts = 0

# Membuat root window dengan customtkinter
root = ctk.CTk()
root.title("Chat Room")
root.geometry("600x450")

# Fungsi dialog untuk meminta informasi dari pengguna
def custom_dialog(title, prompt, is_password=False):
    dialog = ctk.CTkToplevel(root)
    dialog.title(title)
    
    dialog_width = 300
    dialog_height = 150
    
    root.update_idletasks()

    # Menghitung posisi tengah dari root window
    root_x = root.winfo_rootx()
    root_y = root.winfo_rooty()
    root_width = root.winfo_width()
    root_height = root.winfo_height()

    # Posisi x dan y sehingga dialog muncul di tengah root window
    x_position = root_x + (root_width // 2 - dialog_width // 2)
    y_position = root_y + (root_height // 2 - dialog_height // 2)

    # Mengatur posisi dan ukuran dialog
    dialog.geometry(f"{dialog_width}x{dialog_height}+{x_position}+{y_position}")
    
    label = ctk.CTkLabel(dialog, text=prompt, font=("Arial", 12))
    label.pack(pady=(10, 5))

    # Gunakan StringVar untuk menyimpan hasil
    result_var = tk.StringVar(dialog)
    entry = ctk.CTkEntry(dialog, width=200, height=40, textvariable=result_var, show='*' if is_password else '')
    entry.pack(pady=(0, 10))

    # Fungsi untuk menutup dialog dan menyimpan nilai
    def close_dialog():
        result_var.set(entry.get())
        dialog.destroy()

    submit_button = ctk.CTkButton(dialog, text="Submit", command=close_dialog)
    submit_button.pack(pady=(5, 10))
    entry.focus()

    # Tunggu dialog untuk ditutup
    dialog.wait_window()
    return result_var.get()


# ScrolledText dengan font yang lebih besar dan modern
chat_log = ScrolledText(root, font=('Arial', 20), height=20, width=80, bg='#2C2F33', fg='#C4C4C4', wrap=tk.WORD)
chat_log.grid(row=0, column=0, columnspan=2, padx=10, pady=12, sticky='nsew')

# Konfigurasi style untuk chat log
chat_log.tag_configure('message', foreground='#FFFFFF', font=('Arial', 20))
chat_log.tag_configure('broadcast', foreground='#FFFF00', font=('Arial', 20), justify='center')
chat_log.tag_configure('history', foreground='#888888', font=('Arial', 20))


# Inisialisasi client socket
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_ip = custom_dialog("Server IP", "Enter the server IP address:")
client_ip = custom_dialog("Client IP", "Enter the client IP address:")
client.bind((client_ip, random.randint(8000, 9000)))

def send_message(event=None):
    message = message_entry.get()
    if message:
        client.sendto(f"{username}: {message}".encode(), (server_ip, 9999))
        message_entry.delete(0, tk.END)

def receive_messages():
    while True:
        try:
            message, _ = client.recvfrom(1024)
            decoded_message = message.decode()
            chat_log.config(state=tk.NORMAL)
            
            # Cek apakah pesan berisi history
            if "HISTORY_TAG:" in decoded_message:
                history_message = decoded_message.replace("HISTORY_TAG:", "")
                chat_log.insert(tk.END, history_message + "\n", "history")

            else:
                timestamp = time.strftime("%H:%M")
                
                if "has joined the room!" in decoded_message:
                    chat_log.insert(tk.END, decoded_message + "\n", "broadcast")
                else:
                    chat_log.insert(tk.END, f"[{timestamp}] {decoded_message}\n", "message")

            chat_log.config(state=tk.DISABLED)
            chat_log.yview(tk.END)
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

message_entry = ctk.CTkEntry(root, placeholder_text="Type your message here...", width=400, height=50)
message_entry.grid(row=1, column=0, padx=10, pady=10, sticky='ew')

send_button = ctk.CTkButton(root, text="Send", height=50, command=lambda: send_message())
send_button.grid(row=1, column=1, padx=10, pady=10)
message_entry.bind("<Return>", send_message)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

def request_password():
    global attempts
    error_label = ctk.CTkLabel(root, text="", text_color="red", font=("Arial", 12))
    error_label.grid(row=2, column=0, columnspan=2)

    while attempts < 3:
        password = custom_dialog("Password", "Enter the room password:", is_password=True)
        if password == CORRECT_PASSWORD:
            error_label.grid_remove()  
            return True
        else:
            error_label.configure(text="Wrong password! Try again.")
            root.update()  
            attempts += 1

    return False

# Fungsi untuk menunda percobaan password setelah terlalu banyak percobaan yang gagal
def retry_password_after_delay():
    global attempts
    error_label = ctk.CTkLabel(root, text="", text_color="red", font=("Arial", 12))
    error_label.grid(row=2, column=0, columnspan=2)
    countdown_label = ctk.CTkLabel(root, text="Too many attempts. Please wait...", font=("Arial", 12))
    countdown_label.grid(row=2, column=0, columnspan=2)
    
    for i in range(10, 0, -1):
        countdown_label.configure(text=f"Try again in {i} seconds...")
        root.update()  # Memperbarui tampilan GUI
        time.sleep(1)

    countdown_label.grid_remove()
    error_label.grid_remove()
    attempts = 0

while True:
    if request_password():
        break  # Jika password benar, lanjutkan
    else:
        retry_password_after_delay()

if request_password():
    username = custom_dialog("Username", "Enter your username:")
    if username:
        client.sendto(f"SIGNUP_TAG:{username}".encode(), (server_ip, 9999))
        thread = threading.Thread(target=receive_messages)
        thread.daemon = True
        thread.start()

root.mainloop()
