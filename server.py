import socket
import threading
import queue
import os
import time

messages = queue.Queue()
clients = []
message_history = []
history_file = "chat_history.txt"
user_credentials = {}

def load_history():
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding='utf-8') as f:
                for line in f:
                    message_history.append(line.strip())
                    print(f"Loaded history message: {line.strip()}")
            print("Chat history loaded.")
        except Exception as e:
            print(f"Error loading history: {e}")

def save_history(message):
    try:
        timestamp = time.strftime("%H:%M")
        message_with_time = f"[{timestamp}] {message}"
        with open(history_file, "a", encoding='utf-8') as f:
            f.write(message_with_time + "\n")
            f.flush()
    except Exception as e:
        print(f"Error saving history: {e}")

def save_message_to_file(message):
    if "joined" not in message:
        try:
            with open(history_file, "a", encoding='utf-8') as f:
                f.write(message + "\n")
                f.flush()
        except Exception as e:
            print(f"Error saving message: {e}")

def send_message_history(addr):
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding='utf-8') as f:
                messages = f.readlines()
            
            for message in messages:
                server.sendto(f"HISTORY_TAG:{message.strip()}".encode('utf-8'), addr)
                time.sleep(0.1)  # Delay kecil untuk mencegah overwhelm
        except Exception as e:
            print(f"Error sending history: {e}")

def receive():
    while True:
        try:
            message, addr = server.recvfrom(1024)
            messages.put((message, addr))
        except Exception as e:
            print(f"Error receiving message: {e}")

def broadcast():
    while True:
        while not messages.empty():
            try:
                message, addr = messages.get()
                decoded_message = message.decode('utf-8')
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Received: {decoded_message}")

                if addr not in clients:
                    clients.append(addr)
                    print(f"New client connected from {addr}")

                if decoded_message.startswith("SIGNUP_TAG:"):
                    username, password = decoded_message.split(":")[1:3]
                    if username in user_credentials:
                        server.sendto("USERNAME_TAKEN".encode('utf-8'), addr)
                    else:
                        user_credentials[username] = password  # Simpan username dan password
                        welcome_message = f"{username} has joined the room!"
                        print(f"New user joined: {username}")

                        send_message_history(addr)
                        time.sleep(0.5)

                        for client in clients:
                            server.sendto(welcome_message.encode('utf-8'), client)
                elif decoded_message.startswith("LOGIN_TAG:"):
                    username, password = decoded_message.split(":")[1:3]
                    if username in user_credentials and user_credentials[username] == password:
                        server.sendto("LOGIN_SUCCESS".encode('utf-8'), addr)
                    else:
                        server.sendto("LOGIN_FAILED".encode('utf-8'), addr)
                else:
                    save_history(decoded_message)
                    for client in clients:
                        server.sendto(message, client)
            except Exception as e:
                print(f"Error in broadcast: {e}")

# Setup server
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

try:
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((ip_address, 9999))
    print(f"Server running on {ip_address}:9999")
except Exception as e:
    print(f"Error starting server: {e}")
    exit(1)

# Load history and start threads
print("Server is running...")
load_history()

t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=broadcast)

t1.daemon = True
t2.daemon = True

t1.start()
t2.start()

# Keep main thread running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Server shutting down...")