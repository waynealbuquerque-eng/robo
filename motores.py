import RPi.GPIO as GPIO
import time

# --- Configuração ---
motorA_in1 = 3
motorA_in2 = 4
motorB_in1 = 17
motorB_in2 = 27

GPIO.setmode(GPIO.BCM)  # usa numeração BCM
GPIO.setwarnings(False)

# Define os pinos como saída
for pin in [motorA_in1, motorA_in2, motorB_in1, motorB_in2]:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

def parar():
    GPIO.output(motorA_in1, GPIO.LOW)
    GPIO.output(motorA_in2, GPIO.LOW)
    GPIO.output(motorB_in1, GPIO.LOW)
    GPIO.output(motorB_in2, GPIO.LOW)
    print("parando")
    time.sleep(2)

def frente(t=2):
    GPIO.output(motorA_in1, GPIO.HIGH)
    GPIO.output(motorA_in2, GPIO.LOW)
    GPIO.output(motorB_in1, GPIO.HIGH)
    GPIO.output(motorB_in2, GPIO.LOW)
    time.sleep(t)
    parar()

def tras(t=2):
    GPIO.output(motorA_in1, GPIO.LOW)
    GPIO.output(motorA_in2, GPIO.HIGH)
    GPIO.output(motorB_in1, GPIO.LOW)
    GPIO.output(motorB_in2, GPIO.HIGH)
    time.sleep(t)
    parar()

def esquerda(t=1):
    GPIO.output(motorA_in1, GPIO.LOW)
    GPIO.output(motorA_in2, GPIO.HIGH)
    GPIO.output(motorB_in1, GPIO.HIGH)
    GPIO.output(motorB_in2, GPIO.LOW)
    time.sleep(t)
    parar()

def direita(t=1):
    GPIO.output(motorA_in1, GPIO.HIGH)
    GPIO.output(motorA_in2, GPIO.LOW)
    GPIO.output(motorB_in1, GPIO.LOW)
    GPIO.output(motorB_in2, GPIO.HIGH)
    time.sleep(t)
    parar()

# --- Teste Sequencial ---
try:
    print("Frente")
    frente(2)

    print("Trás")
    tras(2)

    print("Esquerda")
    esquerda(2)

    print("Direita")
    direita(2)

    print("Parado")
    parar()

finally:
    GPIO.cleanup()
