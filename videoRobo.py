# tentativa de stremming

import cv2
import socket
import struct
import pickle

# Configura o socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 9999))
server_socket.listen(1)
print("Aguardando conexão para streaming de vídeo...")

conn, addr = server_socket.accept()
print("Conectado a:", addr)

camera = cv2.VideoCapture(0)

while True:
    ret, frame = camera.read()
    if not ret:
        break

    # Codifica frame em JPEG
    _, buffer = cv2.imencode('.jpg', frame)

    # Serializa os dados
    data = pickle.dumps(buffer)

    # Envia tamanho + frame
    conn.sendall(struct.pack("L", len(data)) + data)

camera.release()
conn.close()
