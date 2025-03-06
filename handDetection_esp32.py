import cv2
import mediapipe as mp
import numpy as np
import socket

# Dirección IP del ESP32 (Cámbiala según tu red)
ESP32_IP = "192.168.1.100"  # Reemplaza con la IP de tu ESP32
ESP32_PORT = 12345  # Puerto UDP en el ESP32

# Configurar socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Inicializa MediaPipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Captura de video
cap = cv2.VideoCapture(0)

def calcular_angulo(punto1, punto2):
    """Calcula el ángulo entre dos puntos respecto al eje horizontal."""
    delta_x = punto2[0] - punto1[0]
    delta_y = punto2[1] - punto1[1]
    angulo = np.arctan2(delta_y, delta_x) * 180 / np.pi  # Convierte radianes a grados

    # Convertir el ángulo a un rango de 0° a 180°
    if angulo < 0:
        angulo += 360
    if angulo > 180:
        angulo = 360 - angulo  # Invertir si está fuera del rango

    return int(angulo)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Espejar la imagen para una mejor visualización
    frame = cv2.flip(frame, 1)

    # Convertir a RGB para MediaPipe
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Obtener la muñeca (landmark 0) y el centro de la palma (landmark 9)
            h, w, _ = frame.shape
            wrist_px = (int(hand_landmarks.landmark[0].x * w), int(hand_landmarks.landmark[0].y * h))
            palm_center_px = (int(hand_landmarks.landmark[9].x * w), int(hand_landmarks.landmark[9].y * h))
            
            # Calcular el ángulo de inclinación de la mano
            angulo = calcular_angulo(wrist_px, palm_center_px)
            
            # Enviar ángulo al ESP32 por UDP
            mensaje = f"{angulo}"
            sock.sendto(mensaje.encode(), (ESP32_IP, ESP32_PORT))

            # Dibujar puntos y línea
            cv2.circle(frame, wrist_px, 8, (0, 255, 0), -1)  # Punto en la muñeca
            cv2.circle(frame, palm_center_px, 8, (0, 0, 255), -1)  # Punto en la palma
            cv2.line(frame, wrist_px, palm_center_px, (255, 0, 0), 3)  # Línea entre los puntos
            
            # Mostrar ángulo en pantalla
            cv2.putText(frame, f'Angulo: {angulo} deg', (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            
            # Dibujar malla de la mano
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Mostrar el frame
    cv2.imshow("Detección de Mano - Ángulo", frame)
    
    # Salir con 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

sock.close()
cap.release()
cv2.destroyAllWindows()
