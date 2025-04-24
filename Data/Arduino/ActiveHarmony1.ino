#include <WiFiNINA.h>
#include <ArduinoMqttClient.h>

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

const char* ssid = "A35 van Leni";
const char* password = "HotspotLeni";

const char* mqtt_server = "mqtt.eclipseprojects.io";
const int mqtt_port = 1883;
 

// set topics to subscribe to
// const String topic = "ActiveHarmony/+/+/+/+"; // zetlicht/ mac / kleurencode

// declare variable to story the incoming MQTT payload
String payload;

int roodPin= 9;
int groenPin = 11;
int blauwPin = 10;

const int sensorPin = A0; 

String getMacAdress(){
  char macStr[18];
  
  byte mac[6];
  WiFi.macAddress(mac);

  //Serial.print("MAC Address: ");
  sprintf(macStr, "%02X:%02X:%02X:%02X:%02X:%02X" , mac[0],mac[1], mac[2], mac[3],mac[4], mac[5]);
  //Serial.println(macStr);
  //Serial.println();
  return String(macStr);
}

String maakTopic(){
  String mac = getMacAdress();
  String topic = "ActiveHarmony/" + mac + "/+/+/+" ;
  return topic;
}

void setColor(int redValue, int greenValue,  int blueValue) {
  analogWrite(roodPin, redValue);
  analogWrite(groenPin,  greenValue);
  analogWrite(blauwPin, blueValue);
}

void split(String data, char delimiter, String result[], int maxParts) {
    int start = 0;
    int end = 0;
    int index = 0;
    
    while ((end = data.indexOf(delimiter, start)) != -1 && index < maxParts - 1) {
        result[index++] = data.substring(start, end);
        start = end + 1;
    }
    
    result[index] = data.substring(start); // Add the last part
}

// Callback functie die wordt aangeroepen wanneer een bericht wordt ontvangen
void onMqttMessage(int messageSize) {
  // print out the topic and some message details
  Serial.println("Received a message: ");
  String topic = mqttClient.messageTopic();
  Serial.println(topic);
  Serial.print(mqttClient.messageTopic());

  // read the incoming data and store it into the payload variable
  String payloadString = "";
  for (int i = 0; i < messageSize; i++) {
    payloadString += (char)mqttClient.read();
  }
  payload = payloadString;
  Serial.println(payload);
  zetlicht(topic);
}

void setup() {
  Serial.begin(9600);
  pinMode(roodPin,  OUTPUT);              
  pinMode(groenPin, OUTPUT);
  pinMode(blauwPin, OUTPUT);

  // while (!Serial && millis() < 5000);

  // Verbinden met WiFi
  Serial.print("Verbinden met WiFi... ");
  if (WiFi.begin(ssid, password) != WL_CONNECTED) {
    Serial.println("Mislukt!");
    while (true);
  }
  Serial.println("Verbonden!");
  Serial.print("IP-adres: ");
  Serial.println(WiFi.localIP());

/*
  byte mac[6];
  WiFi.macAddress(mac);

  Serial.print("MAC Address: ");
  sprintf(macStr, "%02X:%02X:%02X:%02X:%02X:%02X" , mac[0],mac[1], mac[2], mac[3],mac[4], mac[5]);
  Serial.println(macStr);
  Serial.println();
*/
  // Verbinden met MQTT-server
  Serial.print("Verbinden met MQTT-broker... ");
  if (!mqttClient.connect(mqtt_server, mqtt_port)) {
    Serial.println("Mislukt!");
    while (true);
  }
  Serial.println("Verbonden met MQTT!");

  // subscribe to the topic
  Serial.print("Subscribing to topic: ");
  String topic = maakTopic();
  Serial.println(topic);
  mqttClient.subscribe(topic);

  // set the message receive callback function:
  // Trigger the 'onMqttMessage' function when mqttClient.poll() (in the loop function) detects a message
  mqttClient.onMessage(onMqttMessage);
}

void zetlicht(String input){
  Serial.println("zetlicht");
  Serial.println(input);
  
  String result[5];
  split(input, '/', result, 5);
  
  if (input.startsWith("ActiveHarmony/")) {
    String mac = result[1];
    String rood = result[2];
    String groen = result[3];
    String blauw = result[4];// MAC-adres is de eerste waarde
    Serial.println(mac);
    Serial.println(rood);
    Serial.println(groen);
    Serial.println(blauw);

  // Vergelijk MAC-adres met macStr
  // if (mac == macStr) {
    setColor(rood.toInt(), groen.toInt(), blauw.toInt());
    delay(2000);
    Serial.println("kleurwaarde");
    Serial.println(rood.toInt());
    Serial.println(groen.toInt());
    Serial.println(blauw.toInt());
  }
}

void loop() {  

  int lichtwaarde = analogRead(A0);  // Lees de analoge waarde van de lichtsensor
    Serial.print("Lichtwaarde: ");
    Serial.println(lichtwaarde);  // Toon de waarde in de seriële monitor
    delay(500);

  char lichtwaardeStr[10]; // Buffer voor de lichtwaarde als string
  sprintf(lichtwaardeStr, "%d", lichtwaarde); // Zet int om naar string

  // Mac adresss als char*
  const char* macStr = getMacAdress().c_str();

  // Stuur een testbericht naar MQTT
  char topic[50] = "ActiveHarmony/" ;
  strcat(topic, macStr) ;
  strcat(topic, "/");
  strcat(topic, lichtwaardeStr); 
  mqttClient.beginMessage(topic);
  mqttClient.print("Hallo vanaf Arduino Nano 33 IoT!");
  mqttClient.endMessage();

  Serial.println("MQTT bericht verzonden!");
  Serial.println(topic);

  delay(100);  // Wacht 5 seconden voordat een nieuw bericht wordt verzonden

  mqttClient.poll();
}
