import cv2
import socket
import struct
import numpy as np
import pygame
import threading
import time

# -------------------------------
# Configuração
ROBO_IP = "192.168.100.217"  # IP da Raspberry
VIDEO_PORT = 9999
CMD_PORT = 8888
# -------------------------------

# --- Função: recebe vídeo do robô ---
def receber_video():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ROBO_IP, VIDEO_PORT))

    data = b""
    payload_size = struct.calcsize(">Q")

    while True:
        # Recebe cabeçalho do tamanho do frame
        while len(data) < payload_size:
            packet = client_socket.recv(4096)
            if not packet:
                return
            data += packet

        packed_size = data[:payload_size]
        data = data[payload_size:]
        frame_size = struct.unpack(">Q", packed_size)[0]

        # Recebe o frame inteiro
        while len(data) < frame_size:
            packet = client_socket.recv(4096)
            if not packet:
                return
            data += packet

        frame_data = data[:frame_size]
        data = data[frame_size:]

        # Converte em imagem OpenCV
        frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)

        cv2.imshow("Video do Robo", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    client_socket.close()
    cv2.destroyAllWindows()


# --- Função: envia comandos do controle ---
def enviar_comandos():
    # Conecta no socket de comandos
    cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cmd_socket.connect((ROBO_IP, CMD_PORT))

    # Inicializa pygame e joystick
    pygame.init()
    pygame.joystick.init()

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    print(f"Usando controle: {joystick.get_name()}")

    prev_buttons = [0] * joystick.get_numbuttons()
    prev_axes = [0.0] * joystick.get_numaxes()
    DEBOUNCE_TIME = 0.2
    last_press_time = [0] * joystick.get_numbuttons()

    while True:
        pygame.event.pump()

        # --- Botões ---
        for i in range(joystick.get_numbuttons()):
            state = joystick.get_button(i)
            now = time.time()
            if state == 1 and prev_buttons[i] == 0:  # 0 -> 1
                if now - last_press_time[i] > DEBOUNCE_TIME:
                    msg = f"BOTAO {i}\n"
                    # cmd_socket.sendall(msg.encode())
                    if i == 0:
                        msg = "FRENTE\n"
                        cmd_socket.sendall(msg.encode())
                    if i == 3:
                        msg = "TRAS\n"
                        cmd_socket.sendall(msg.encode())

                    if i == 7:
                        msg = "PARAR\n"
                        cmd_socket.sendall(msg.encode())
                    print("Enviado:", msg.strip())
                    last_press_time[i] = now
            prev_buttons[i] = state

        # --- Eixos ---
        for i in range(joystick.get_numaxes()):
            val = joystick.get_axis(i)
            if abs(val - prev_axes[i]) > 0.1:  # só se mudar bastante
                msg = f"EIXO {i} {val:.2f}\n"
                # cmd_socket.sendall(msg.encode())
                print("Enviado:", msg.strip())
                prev_axes[i] = val

        # --- DPad ---
        for i in range(joystick.get_numhats()):
            hat = joystick.get_hat(i)
            if hat != (0, 0):
                msg = f"DPAD {hat}\n"
                # cmd_socket.sendall(msg.encode())

                if hat == (1, 0):
                    msg = "ESQ\n"
                    cmd_socket.sendall(msg.encode())
                if hat == (1, 0):
                    msg = "DIR\n"
                    cmd_socket.sendall(msg.encode())
                print("Enviado:", msg.strip())


# --- Threads: roda vídeo e comandos ao mesmo tempo ---
t_video = threading.Thread(target=receber_video, daemon=True)
t_video.start()

enviar_comandos()  # roda no main thread
