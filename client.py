import socket
import threading
import random

# Mencari IP dari device
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind((f"{ip_address}", random.randint(8000, 9000)))

name = input("Nickname: ")

def receive():
    while True:
        try:
            message, _ = client.recvfrom(1024)
            print(message.decode())
        except:
            pass
        
t = threading.Thread(target=receive)
t.start()

# Kirim password untuk autentikasi
password = input("Masukkan password: ")
client.sendto(f"PASSWORD:{password}".encode(), ('10.5.104.205', 9999))

# Kirim nickname setelah autentikasi berhasil
client.sendto(f"SIGNUP_TAG:{name}".encode(), ('10.5.104.205', 9999))

# Mulai pengiriman pesan
while True:
    message = input("")
    if message == "!q":
        exit()
    else:
        client.sendto(f"{name}: {message}".encode(), ('10.5.104.205', 9999))