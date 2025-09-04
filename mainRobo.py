#!/usr/bin/env python3
import cv2
import socket
import struct
import threading
import time
import RPi.GPIO as GPIO

# ========================
# CONFIG PINS / GPIO
# ========================
# Motor da direita -> 17, 27
# Motor da esquerda -> 23, 24
MOTOR_DIR_IN1 = 17
MOTOR_DIR_IN2 = 27
MOTOR_ESQ_IN1 = 24
MOTOR_ESQ_IN2 = 23

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
for pin in [MOTOR_DIR_IN1, MOTOR_DIR_IN2, MOTOR_ESQ_IN1, MOTOR_ESQ_IN2]:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

gpio_lock = threading.Lock()   # garante que só um comando mexe nos pinos por vez
stop_timer = None              # timer para parar automático após duração

def _cancel_stop_timer():
    global stop_timer
    if stop_timer is not None:
        stop_timer.cancel()
        stop_timer = None

def _schedule_stop(t):
    """Agenda um PARAR em t segundos (cancela o anterior)."""
    global stop_timer
    _cancel_stop_timer()
    if t is not None and t > 0:
        stop_timer = threading.Timer(t, parar)
        stop_timer.daemon = True
        stop_timer.start()

def parar():
    with gpio_lock:
        GPIO.output(MOTOR_DIR_IN1, GPIO.LOW)
        GPIO.output(MOTOR_DIR_IN2, GPIO.LOW)
        GPIO.output(MOTOR_ESQ_IN1, GPIO.LOW)
        GPIO.output(MOTOR_ESQ_IN2, GPIO.LOW)

def frente(duration=None):
    with gpio_lock:
        GPIO.output(MOTOR_DIR_IN1, GPIO.HIGH)
        GPIO.output(MOTOR_DIR_IN2, GPIO.LOW)
        GPIO.output(MOTOR_ESQ_IN1, GPIO.HIGH)
        GPIO.output(MOTOR_ESQ_IN2, GPIO.LOW)
    _schedule_stop(duration)

def tras(duration=None):
    with gpio_lock:
        GPIO.output(MOTOR_DIR_IN1, GPIO.LOW)
        GPIO.output(MOTOR_DIR_IN2, GPIO.HIGH)
        GPIO.output(MOTOR_ESQ_IN1, GPIO.LOW)
        GPIO.output(MOTOR_ESQ_IN2, GPIO.HIGH)
    _schedule_stop(duration)

def esquerda(duration=None):
    with gpio_lock:
        GPIO.output(MOTOR_DIR_IN1, GPIO.LOW)
        GPIO.output(MOTOR_DIR_IN2, GPIO.HIGH)
        GPIO.output(MOTOR_ESQ_IN1, GPIO.HIGH)
        GPIO.output(MOTOR_ESQ_IN2, GPIO.LOW)
    _schedule_stop(duration)

def direita(duration=None):
    with gpio_lock:
        GPIO.output(MOTOR_DIR_IN1, GPIO.HIGH)
        GPIO.output(MOTOR_DIR_IN2, GPIO.LOW)
        GPIO.output(MOTOR_ESQ_IN1, GPIO.LOW)
        GPIO.output(MOTOR_ESQ_IN2, GPIO.HIGH)
    _schedule_stop(duration)

# ========================
# VIDEO STREAM SERVER
# ========================
def video_server(host="0.0.0.0", port=9999, width=640, height=480, fps=15, quality=70):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(1)
    print(f"[VIDEO] Aguardando conexão em {host}:{port} ...")
    conn, addr = server.accept()
    print(f"[VIDEO] Conectado a {addr}")

    cap = cv2.VideoCapture(0)
    # opcional: tentar setar resolução diretamente na câmera
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    frame_delay = 1.0 / float(max(fps, 1))
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # garante resolução desejada (caso a câmera ignore set())
            frame = cv2.resize(frame, (width, height))
            ok, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), int(quality)])
            if not ok:
                continue
            data = buf.tobytes()
            size = len(data)
            # envia tamanho (8 bytes big-endian) + payload
            conn.sendall(struct.pack(">Q", size) + data)
            time.sleep(frame_delay)
    except (BrokenPipeError, ConnectionResetError):
        print("[VIDEO] Cliente desconectou.")
    finally:
        cap.release()
        try:
            conn.close()
        except:
            pass
        server.close()
        print("[VIDEO] Encerrado.")

# ========================
# COMMAND SERVER
# ========================
# Protocolo de texto simples por linha:
# "FRENTE [segundos]"
# "TRAS [segundos]"
# "ESQ [segundos]"
# "DIR [segundos]"
# "PARAR"
def handle_command(cmd_line: str):
    parts = cmd_line.strip().split()
    if not parts:
        return
    cmd = parts[0].upper()
    dur = 1
    if len(parts) >= 2:
        try:
            dur = float(parts[1])
        except ValueError:
            dur = None

    if cmd == "FRENTE":
        frente(dur)
    elif cmd == "TRAS":
        tras(dur)
    elif cmd in ("ESQ", "ESQUERDA"):
        esquerda(dur)
    elif cmd in ("DIR", "DIREITA"):
        direita(dur)
    elif cmd == "PARAR":
        _cancel_stop_timer()
        parar()
    else:
        print(f"[CMD] Comando desconhecido: {cmd_line!r}")

def command_server(host="0.0.0.0", port=8888):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(1)
    print(f"[CMD] Aguardando conexão em {host}:{port} ...")

    while True:
        conn, addr = server.accept()
        print(f"[CMD] Conectado a {addr}")
        try:
            # lê por linhas; cada linha é um comando
            buffer = b""
            while True:
                chunk = conn.recv(1024)
                if not chunk:
                    print("[CMD] Cliente encerrou.")
                    break
                buffer += chunk
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    try:
                        text = line.decode("utf-8", errors="ignore")
                    except:
                        text = ""
                    if text:
                        print(f"[CMD] {text}")
                        handle_command(text)
        except ConnectionResetError:
            print("[CMD] Conexão resetada pelo cliente.")
        finally:
            try:
                conn.close()
            except:
                pass
            # por segurança, para os motores quando o cliente cai
            _cancel_stop_timer()
            parar()

# ========================
# MAIN
# ========================
if __name__ == "__main__":
    try:
        # thread de vídeo
        t_video = threading.Thread(target=video_server, daemon=True)
        t_video.start()

        # servidor de comandos (loop bloqueante, reaproveita conexões)
        command_server()
    except KeyboardInterrupt:
        print("\n[MAIN] Ctrl+C recebido. Encerrando...")
    finally:
        _cancel_stop_timer()
        parar()
        GPIO.cleanup()
        print("[MAIN] GPIO limpa. Fim.")
