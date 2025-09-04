import pygame
import time

# Inicializa pygame e joystick
pygame.init()
pygame.joystick.init()

# Pega o primeiro controle conectado
joystick = pygame.joystick.Joystick(0)
joystick.init()

print(f"Usando controle: {joystick.get_name()}")

# Guarda estados anteriores para debounce
prev_buttons = [0] * joystick.get_numbuttons()
prev_axes = [0.0] * joystick.get_numaxes()

# (Opcional) tempo mínimo entre eventos (em segundos)
DEBOUNCE_TIME = 0.2
last_press_time = [0] * joystick.get_numbuttons()

while True:
    pygame.event.pump()  # Atualiza os eventos

    # --- Botões (com debounce)
    for i in range(joystick.get_numbuttons()):
        state = joystick.get_button(i)
        now = time.time()
        if state == 1 and prev_buttons[i] == 0:  # transição 0 -> 1
            if now - last_press_time[i] > DEBOUNCE_TIME:
                print(f"Botão {i} pressionado")
                # aqui você poderia enviar via TCP
                last_press_time[i] = now
        prev_buttons[i] = state

    # --- Eixos (sticks e gatilhos) com filtro de mudança
    for i in range(joystick.get_numaxes()):
        val = joystick.get_axis(i)
        if abs(val - prev_axes[i]) > 0.05:  # só quando mudar
            print(f"Eixo {i}: {val:.2f}")
            # aqui você poderia enviar via TCP
            prev_axes[i] = val

    # --- DPad (pode tratar como botão também)
    for i in range(joystick.get_numhats()):
        hat = joystick.get_hat(i)
        if hat != (0, 0):
            print(f"DPad: {hat}")
