import socket
import threading
import queue
import os
import time

messages = queue.Queue()
clients = []
message_history = []
history_file = "chat_history.txt"

# Load chat dari file (kalo ada)
def load_history():
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            for line in f:
                message_history.append(line.strip())
                print(f"Loaded history message: {line.strip()}")
        print("Chat history loaded.")

# Menyimpan chat ke file
def save_history(message):
    timestamp = time.strftime("%H:%M")
    message_with_time = f"[{timestamp}] {message}"
    with open(history_file, "a") as f:
        f.write(message_with_time + "\n")
        f.flush()

# Menerima input IP dari device
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((f"{ip_address}", 9999))

# Password untuk akses ke Chatroom
chatroom_password = "1234"

# Fungsi untuk menyimpan pesan ke dalam file, kecuali pesan join
def save_message_to_file(message):
    # Jangan simpan pesan yang berisi kata "joined"
    if "joined" not in message:
        with open(history_file, "a") as f:
            f.write(message + "\n")

# Fungsi untuk mengirimkan riwayat pesan ke client baru
def send_message_history(addr):
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            messages = f.readlines()

        # Gabungkan semua pesan menjadi satu string dipisahkan oleh enter
        combined_messages = "".join([message for message in messages])
        
        # Kirimkan pesan yang sudah digabungkan ke client
        if combined_messages:
            server.sendto(combined_messages.encode(), addr)

# Menerima pesan dari client
def receive():
    while True:
        try:
            message, addr = server.recvfrom(1024)
            messages.put((message, addr))
        except:
            pass

# Mengirimkan pesan ke semua client yang terdaftar
def broadcast(): 
    while True:
        while not messages.empty():
            message, addr = messages.get()
            decoded_message = message.decode()
            print(time.strftime("%Y-%m-%d %H:%M:%S") + ": " + message.decode())

            if addr not in clients:
                clients.append(addr)
            decoded_message = message.decode()

            if decoded_message.startswith("SIGNUP_TAG:"):
                name = decoded_message.split(":")[1]
                welcome_message = f"{name} has joined the room!"

            # Memindahkan fungsi password chat room ke client.py
            
                # Menampilkan histroy chat saat client keluar 
                for hist_msg in message_history:
                    try:
                        server.sendto(f"HISTORY_TAG:{hist_msg}".encode(), addr)
                    except:
                        clients.remove(addr)

                for client in clients:
                    try:
                        server.sendto(welcome_message.encode(), client)
                    except:
                        clients.remove(client)
            else:
                timestamped_message = f"{decoded_message} [{time.strftime('%H:%M')}]"
                message_history.append(timestamped_message)
                save_history(decoded_message) # Simpen chat ke file
                for client in clients:
                    try:
                        server.sendto(message, client)
                    except:
                        clients.remove(client)

print("Server is running...") 
load_history()
t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=broadcast)

t1.start()
t2.start()
