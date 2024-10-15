import socket
import threading
import queue
import os

messages = queue.Queue()
clients = []
authorized_clients = []
history_file = "chat_history.txt"

# Mencari IP dari device
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

            # Memasukkan alamat client yang belum terdaftar
            if addr not in clients:
                clients.append(addr)

            # Memproses autentikasi jika client belum authorized
            if addr not in authorized_clients:
                if decoded_message.startswith("PASSWORD:"):
                    entered_password = decoded_message.split(":")[1]

                    # Cek apakah password yang dimasukkan benar
                    if entered_password == chatroom_password:
                        authorized_clients.append(addr)
                        send_message_history(addr)  # Kirim riwayat pesan ke client baru
                        server.sendto("Akses diizinkan. Selamat datang di chatroom!".encode(), addr)
                    else:
                        server.sendto("Password salah. Coba lagi.".encode(), addr)
                else:
                    server.sendto("Kamu harus memasukkan password terlebih dahulu. Format: PASSWORD:<password>".encode(), addr)
            else:
                # Jika client sudah authorized, proses pesan
                if decoded_message.startswith("SIGNUP_TAG:"):
                    name = decoded_message[decoded_message.index(":")+1:]
                    broadcast_message = f"{name} joined!"
                    print(broadcast_message)
                    save_message_to_file(broadcast_message)  # Simpan pesan join ke file
                    for client in clients:
                        server.sendto(broadcast_message.encode(), client)
                else:
                    print(decoded_message)
                    save_message_to_file(decoded_message)  # Simpan pesan ke file
                    for client in clients:
                        try:
                            server.sendto(message, client)
                        except:
                            clients.remove(client)

t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=broadcast)

t1.start()
t2.start()
