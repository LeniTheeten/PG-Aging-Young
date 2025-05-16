int roodPin = 9;
int groenPin = 11;
int blauwPin = 10;

const int knopPin = 2;  // Drukknop aangesloten op pin 2

void setup() {
  Serial.begin(9600);
  pinMode(roodPin, OUTPUT);
  pinMode(groenPin, OUTPUT);
  pinMode(blauwPin, OUTPUT);
  pinMode(knopPin, INPUT); // GEEN INPUT_PULLUP, want je gebruikt externe pull-down weerstand
}

void loop() {
  int knopStatus = digitalRead(knopPin);
  Serial.print("Knopstatus: ");
  Serial.println(knopStatus);  // 1 = ingedrukt, 0 = niet ingedrukt
  delay(100);

  if (knopStatus == HIGH) {
    setColor(255, 0, 0); // Rood bij ingedrukte knop
  } else {
    setColor(0, 0, 0);   // LED uit
  }
}

void setColor(int redValue, int greenValue, int blueValue) {
  analogWrite(roodPin, redValue);
  analogWrite(groenPin, greenValue);
  analogWrite(blauwPin, blueValue);
}
