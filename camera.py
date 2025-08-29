import cv2

# Abre a câmera (0 é a câmera padrão, se tiver mais use 1, 2...)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Não foi possível acessar a câmera")
    exit()

while True:
    # Captura frame a frame
    ret, frame = cap.read()
    if not ret:
        print("Erro ao capturar o frame")
        break

    # Mostra a imagem
    cv2.imshow("Minha Câmera", frame)

    # Sai do loop quando pressionar a tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera a câmera e fecha a janela
cap.release()
cv2.destroyAllWindows()
