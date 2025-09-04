import cv2
import socket
import struct
import pickle

# Configura socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 9999))
server_socket.listen(1)

print("Aguardando conexão...")
conn, addr = server_socket.accept()
print("Conectado a:", addr)

camera = cv2.VideoCapture(0)

while True:
    ret, frame = camera.read()
    if not ret:
        break

    # Serializa o frame
    data = pickle.dumps(frame)
    size = len(data)

    # Envia primeiro o tamanho (8 bytes), depois os dados
    conn.sendall(struct.pack(">Q", size) + data)

camera.release()
conn.close()
server_socket.close()
