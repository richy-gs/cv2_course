import socket

import cv2
import numpy as np

# Dirección IP del ESP32 (CAMBIA según la IP de tu ESP32)
ESP32_IP = "192.168.43.244"  # Reemplaza con la IP de tu ESP32
ESP32_PORT = 12345  # Puerto UDP en el ESP32

# Configurar socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Inicializa la captura de video
cap = cv2.VideoCapture(0)

# Definir rangos de colores en HSV
rangos_colores = {
    "rojo": [(0, 120, 70), (10, 255, 255)],  # Rojo (tono bajo)
    "rojo2": [(170, 120, 70), (180, 255, 255)],  # Rojo (tono alto)
    "verde": [(40, 40, 40), (80, 255, 255)],  # Verde
    "azul": [(90, 50, 50), (130, 255, 255)],  # Azul
}

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Espejar la imagen para una mejor visualización
    frame = cv2.flip(frame, 1)

    # Convertir a espacio HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    color_detectado = None  # Variable para almacenar el color detectado

    for color, (lower, upper) in rangos_colores.items():
        lower = np.array(lower, dtype=np.uint8)
        upper = np.array(upper, dtype=np.uint8)
        mask = cv2.inRange(hsv, lower, upper)

        # Encontrar contornos
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) > 500:  # Filtrar objetos pequeños
                x, y, w, h = cv2.boundingRect(contour)

                # Detección de color
                if "rojo" in color:
                    color_detectado = "rojo"
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                elif color == "verde":
                    color_detectado = "verde"
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                elif color == "azul":
                    color_detectado = "azul"
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # Si se detectó un color, enviarlo al ESP32
    if color_detectado:
        sock.sendto(color_detectado.encode(), (ESP32_IP, ESP32_PORT))
        cv2.putText(
            frame,
            f"Color: {color_detectado}",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
        )

    # Mostrar la imagen procesada
    cv2.imshow("Detección de colores", frame)

    # Salir con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Liberar recursos
sock.close()
cap.release()
cv2.destroyAllWindows()
