int roodPin = 9;
int groenPin = 11;
int blauwPin = 10;

const int sensorPin = A0;

void setup() {
  Serial.begin(9600);
  pinMode(roodPin, OUTPUT);
  pinMode(groenPin, OUTPUT);
  pinMode(blauwPin, OUTPUT);
}

void loop() {
  int lichtwaarde = analogRead(sensorPin);
  Serial.print("Lichtwaarde: ");
  Serial.println(lichtwaarde);
  delay(500);

  if (lichtwaarde < 650) {
    setColor(255, 0, 0); // Rood bij weinig licht
  } else {
    setColor(0, 0, 0);   // LED uit
  }
}

void setColor(int redValue, int greenValue, int blueValue) {
  analogWrite(roodPin, redValue);
  analogWrite(groenPin, greenValue);
  analogWrite(blauwPin, blueValue);
}
