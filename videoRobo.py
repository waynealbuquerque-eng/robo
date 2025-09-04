import time
import cv2
import socket
import struct

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
    frame = cv2.resize(frame, (640, 480))  # ou 320x240 para mais leve

    if not ret:
        break

    # Serializa o frame
    ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
    data = buffer.tobytes()

    size = len(data)

    # Envia primeiro o tamanho (8 bytes), depois os dados
    conn.sendall(struct.pack(">Q", size) + data)
    time.sleep(1 / 15)  # trava o loop em 15 frames por segundo

camera.release()
conn.close()
server_socket.close()
