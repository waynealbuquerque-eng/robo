import pygame
import time

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("Nenhum joystick detectado")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Controle detectado: {joystick.get_name()}")

while True:
    pygame.event.pump()  # atualiza estado do joystick

    # --- Botões ---
    for i in range(joystick.get_numbuttons()):
        if joystick.get_button(i):
            print(f"Botão {i} pressionado")

    # --- Eixos (sticks / gatilhos) ---
    for i in range(joystick.get_numaxes()):
        val = joystick.get_axis(i)
        if abs(val) > 0.2:  # só mostra se mexer
            print(f"Eixo {i}: {val:.2f}")

    # --- DPad (hat) ---
    for i in range(joystick.get_numhats()):
        hat = joystick.get_hat(i)
        if hat != (0, 0):
            print(f"DPad: {hat}")

    time.sleep(0.1)
