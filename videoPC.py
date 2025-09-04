import cv2
import socket
import struct
import pickle

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("IP_DA_RASP", 9999))

data = b""
payload_size = struct.calcsize("L")

while True:
    while len(data) < payload_size:
        data += client_socket.recv(4096)

    packed_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("L", packed_size)[0]

    while len(data) < msg_size:
        data += client_socket.recv(4096)

    frame_data = data[:msg_size]
    data = data[msg_size:]

    frame = pickle.loads(frame_data)
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
    cv2.imshow("Video do Robo", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

client_socket.close()
