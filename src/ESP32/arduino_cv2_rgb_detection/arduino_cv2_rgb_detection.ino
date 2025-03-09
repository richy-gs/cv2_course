#include <WiFi.h>
#include <WiFiUdp.h>

const char* ssid = "Tu_Red_WiFi";  // Reemplaza con tu red WiFi
const char* password = "Tu_Contraseña";  // Reemplaza con la contraseña

WiFiUDP udp;
const int localPort = 12345;  // Puerto de escucha
char packetBuffer[255];

// Pines del L298N
const int motorPWM = 13;  // Pin PWM (ENA)
const int motorIN1 = 14;  // IN1 del motor
const int motorIN2 = 27;  // IN2 del motor

void setup() {
    Serial.begin(115200);
    
    // Conectar a WiFi
    WiFi.begin(ssid, password);
    Serial.print("Conectando a WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nConectado a la red WiFi");
    Serial.print("Dirección IP: ");
    Serial.println(WiFi.localIP());

    // Iniciar UDP
    udp.begin(localPort);
    Serial.println("Servidor UDP iniciado");

    // Configurar pines del motor
    pinMode(motorPWM, OUTPUT);
    pinMode(motorIN1, OUTPUT);
    pinMode(motorIN2, OUTPUT);
}

void mover_motor(int velocidad) {
    if (velocidad == 0) {
        digitalWrite(motorIN1, LOW);
        digitalWrite(motorIN2, LOW);
    } else {
        digitalWrite(motorIN1, HIGH);
        digitalWrite(motorIN2, LOW);
    }
    analogWrite(motorPWM, velocidad);  // Control de velocidad PWM
}

void loop() {
    int packetSize = udp.parsePacket();
    if (packetSize) {
        int len = udp.read(packetBuffer, 255);
        if (len > 0) {
            packetBuffer[len] = '\0';  // Finalizar la cadena correctamente
        }

        String colorRecibido = String(packetBuffer);
        colorRecibido.trim();  // Eliminar espacios o caracteres extra

        Serial.print("Color recibido: ");
        Serial.println(colorRecibido);

        // Control del motor según el color recibido
        if (colorRecibido == "rojo") {
            Serial.println("Deteniendo motor...");
            mover_motor(0);  // Motor apagado
        } else if (colorRecibido == "verde") {
            Serial.println("Motor a máxima velocidad...");
            mover_motor(255);  // Velocidad máxima
        } else if (colorRecibido == "azul") {
            Serial.println("Motor a velocidad baja...");
            mover_motor(100);  // Velocidad baja
        }
    }
}
