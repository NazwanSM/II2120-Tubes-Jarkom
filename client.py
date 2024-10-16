import tkinter as tk
from tkinter import scrolledtext, simpledialog
import threading
import socket
import random
import time

CORRECT_PASSWORD = "mysecretpassword"
attempts = 0

server_ip = simpledialog.askstring("Server IP", "Enter the server IP address: ")
client_ip = simpledialog.askstring("Client Ip", "Enter the client IP address: ")

def send_message(event=None):
    # Mengirimkan chat di field entry ke server
    message = message_entry.get()
    if message:
        client.sendto(f"{username}: {message}".encode(), ((server_ip), 9999))
        message_entry.delete(0, tk.END)

def receive_messages():
    # Menerima chat dari server dan ditampilkan di display
    while True:
        try:
            message, _ = client.recvfrom(1024)
            decoded_message = message.decode()
            
            chat_log.config(state=tk.NORMAL)

            # If the message contains the history
               
            if "HISTORY_TAG:" in decoded_message:
                history_message = decoded_message.replace("HISTORY_TAG:", "")
                print(f"{history_message}")
                chat_log.insert(tk.END, history_message + "\n", "history")

            else:
                timestamp = time.strftime("%H:%M") 
                
                if "has joined the room!" in decoded_message:
                    chat_log.insert(tk.END, decoded_message + "\n", "broadcast")  # Apply 'center' tag
                else:    
                    # Menambahkan timestamp dengan tag 'timestamp'
                    chat_log.insert(tk.END, f"[{timestamp}] ", "message")  # Menampilkan pesan utama terlebih dahulu
                    chat_log.insert(tk.END, f"{decoded_message}\n", "timestamp")  # Menampilkan timestamp setelah pesan


            chat_log.config(state=tk.DISABLED)
            chat_log.yview(tk.END)
        except:
            break
        
def request_password():
    # Menerima dan mengecek input password 
    global attempts
    error_label = tk.Label(root, text="", fg="red", font=("Arial", 12))
    error_label.grid(row=2, column=0, columnspan=2)

    while attempts < 3: # Apabila sudah 3 kali salah, client akan diberi jeda sebelum dapat memasukkan password lagi
        password = simpledialog.askstring("Password", "Enter the room password:", show='*', parent=root)
        if password == CORRECT_PASSWORD:
            error_label.grid_remove()  
            return True
        else:
            error_label.config(text="Wrong password! Try again.")
            root.update()  
            attempts += 1

    return False

def retry_password_after_delay():
    # Memberi jeda 10 detik sebelum dapat memasukkan password lagi
    global attempts
    error_label = tk.Label(root, text="", fg="red", font=("Arial", 12))
    error_label.grid(row=2, column=0, columnspan=2)
    countdown_label = tk.Label(root, text="Too many attempts. Please wait...", font=("Arial", 12))
    countdown_label.grid(row=2, column=0, columnspan=2)
    
    for i in range(10, 0, -1):
        countdown_label.config(text=f"Try again in {i} seconds...")
        root.update()  # Memperbarui tampilan GUI
        time.sleep(1)

    countdown_label.grid_remove()
    error_label.grid_remove()
    attempts = 0

# Menginisialisasi thinker windows
root = tk.Tk()
root.title("Chat Room")

# GUI untuk setiap text
chat_log = scrolledtext.ScrolledText(root, state='disabled', wrap=tk.WORD)
chat_log.grid(row=0, column=0, columnspan=2, sticky="nsew")

chat_log.tag_configure("center", justify="center")
chat_log.tag_configure("timestamp", font=("Arial", 10))
chat_log.tag_configure("message", font=("Arial", 10))
chat_log.tag_configure("broadcast", font=("Arial", 10), foreground="black", justify="center")  # Gaya font untuk broadcast
chat_log.tag_configure("history", font=("Arial", 10), foreground="black")

message_entry = tk.Entry(root)
message_entry.grid(row=1, column=0, sticky="ew")

# Tombol send
send_button = tk.Button(root, text="Send", command=send_message)
send_button.grid(row=1, column=1)
message_entry.bind("<Return>", send_message)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Inisialisasi client
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind((client_ip, random.randint(8000, 9000)))

# Proses otentikasi password
while True:
    if request_password():
        break  # Jika password benar, lanjutkan
    else:
        retry_password_after_delay()  # Jika salah 3 kali, tunggu 3 detik

# Menerima input username
username = simpledialog.askstring("Username", "Enter your username:", parent=root)
if username:
    client.sendto(f"SIGNUP_TAG:{username}".encode(), (server_ip, 9999))
    thread = threading.Thread(target=receive_messages)
    thread.daemon = True
    thread.start()

root.mainloop()
