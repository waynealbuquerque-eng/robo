import RPi.GPIO as GPIO
import time

# Definição dos pinos conectados ao L298
motor1_in1 = 3
motor1_in2 = 4
motor2_in1 = 17
motor2_in2 = 27

# Configuração inicial
GPIO.setmode(GPIO.BCM)  # Usa a numeração BCM
GPIO.setwarnings(False)

# Configura todos como saída
for pin in [motor1_in1, motor1_in2, motor2_in1, motor2_in2]:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)  # Garante que começa desligado

def motor1_forward():
    GPIO.output(motor1_in1, GPIO.HIGH)
    GPIO.output(motor1_in2, GPIO.LOW)

def motor1_backward():
    GPIO.output(motor1_in1, GPIO.LOW)
    GPIO.output(motor1_in2, GPIO.HIGH)

def motor1_stop():
    GPIO.output(motor1_in1, GPIO.LOW)
    GPIO.output(motor1_in2, GPIO.LOW)

def motor2_forward():
    GPIO.output(motor2_in1, GPIO.HIGH)
    GPIO.output(motor2_in2, GPIO.LOW)

def motor2_backward():
    GPIO.output(motor2_in1, GPIO.LOW)
    GPIO.output(motor2_in2, GPIO.HIGH)

def motor2_stop():
    GPIO.output(motor2_in1, GPIO.LOW)
    GPIO.output(motor2_in2, GPIO.LOW)

try:
    print("Motor 1 para frente")
    motor1_forward()
    time.sleep(2)
    motor1_stop()

    print("Motor 1 para trás")
    motor1_backward()
    time.sleep(2)
    motor1_stop()

    print("Motor 2 para frente")
    motor2_forward()
    time.sleep(2)
    motor2_stop()

    print("Motor 2 para trás")
    motor2_backward()
    time.sleep(2)
    motor2_stop()

finally:
    print("Encerrando, limpando GPIO")
    GPIO.cleanup()
