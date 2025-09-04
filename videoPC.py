import cv2
import socket
import struct
import pickle

# Conecta ao servidor
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("192.168.100.217", 9999))

data = b""
payload_size = struct.calcsize(">Q")

while True:
    # Lê o cabeçalho (tamanho do frame)
    while len(data) < payload_size:
        packet = client_socket.recv(4096)
        if not packet:
            break
        data += packet

    if len(data) < payload_size:
        break

    packed_size = data[:payload_size]
    data = data[payload_size:]
    frame_size = struct.unpack(">Q", packed_size)[0]

    # Lê o frame completo
    while len(data) < frame_size:
        packet = client_socket.recv(4096)
        if not packet:
            break
        data += packet

    frame_data = data[:frame_size]
    data = data[frame_size:]

    # Desserializa
    frame = pickle.loads(frame_data)

    cv2.imshow("Video do Robo", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

client_socket.close()
cv2.destroyAllWindows()
