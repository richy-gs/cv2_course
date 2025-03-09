#include <WiFi.h>
#include <WiFiUdp.h>
#include <ESP32Servo.h>

const char* ssid = "Tu_Red_WiFi";     // Reemplaza con el nombre de tu red WiFi
const char* password = "Tu_Contraseña"; // Reemplaza con la contraseña de tu WiFi

WiFiUDP udp;
const int localPort = 12345; // Puerto donde escucha el ESP32
char packetBuffer[255];

Servo myServo;
const int servoPin = 13; // GPIO para el servo

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

    // Iniciar servidor UDP
    udp.begin(localPort);
    Serial.println("Servidor UDP iniciado");

    // Configurar Servo
    myServo.attach(servoPin);
    myServo.write(90); // Posición inicial (mitad)
}

void loop() {
    int packetSize = udp.parsePacket();
    if (packetSize) {
        int len = udp.read(packetBuffer, 255);
        if (len > 0) {
            packetBuffer[len] = '\0'; // Finalizar la cadena correctamente
        }

        int angulo = atoi(packetBuffer); // Convertir el mensaje a número
        if (angulo >= 0 && angulo <= 180) { // Verificar rango válido
            myServo.write(angulo);
            Serial.print("Moviendo servo a: ");
            Serial.println(angulo);
        }
    }
}
