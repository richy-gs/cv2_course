import cv2
import mediapipe as mp
import numpy as np

# Inicializa MediaPipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# Configuración del detector de manos
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Captura de video desde la cámara
cap = cv2.VideoCapture(0)

def calcular_angulo(punto1, punto2):
    """Calcula el ángulo entre dos puntos respecto al eje horizontal."""
    delta_x = punto2[0] - punto1[0]
    delta_y = punto2[1] - punto1[1]
    angulo = np.arctan2(delta_y, delta_x) * 180 / np.pi  # Convierte de radianes a grados
    return angulo

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convierte el frame a RGB (MediaPipe trabaja en RGB)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Procesa el frame con MediaPipe Hands
    results = hands.process(frame_rgb)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Obtener la muñeca (landmark 0) y el dedo índice (landmark 5)
            wrist = hand_landmarks.landmark[0]  # Muñeca
            index_finger = hand_landmarks.landmark[5]  # Base del dedo índice
            
            # Convertir coordenadas normalizadas a píxeles
            h, w, _ = frame.shape
            wrist_px = (int(wrist.x * w), int(wrist.y * h))
            index_px = (int(index_finger.x * w), int(index_finger.y * h))
            
            # Calcular el ángulo
            angulo = calcular_angulo(wrist_px, index_px)
            
            # Dibujar puntos y línea entre ellos
            cv2.circle(frame, wrist_px, 8, (0, 255, 0), -1)
            cv2.circle(frame, index_px, 8, (0, 0, 255), -1)
            cv2.line(frame, wrist_px, index_px, (255, 0, 0), 3)
            
            # Mostrar el ángulo en pantalla
            cv2.putText(frame, f'Angulo: {int(angulo)} deg', (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            
            # Dibujar la malla de la mano
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Mostrar el frame
    cv2.imshow("Detección de Mano - Ángulo", frame)

    # Salir con 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar recursos
cap.release()
cv2.destroyAllWindows()

