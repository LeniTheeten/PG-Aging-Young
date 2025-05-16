const int trigPin = 12;
const int echoPin = 8;

float duur;
float afstand;

int roodPin= 9;
int groenPin = 11;
int blauwPin = 10;


void setup() {
  Serial.begin(9600);               // Start seriële communicatie
  pinMode(trigPin, OUTPUT);         // trigPin als output
  pinMode(echoPin, INPUT);          // echoPin als input
  pinMode(roodPin,  OUTPUT);              
  pinMode(groenPin, OUTPUT);
  pinMode(blauwPin, OUTPUT);
}

void loop() {
  // Zorg dat de trigPin laag is
  digitalWrite(trigPin, LOW);
  delay(200);

  // Stuur een korte puls van 10 microseconden
  digitalWrite(trigPin, HIGH);
  delay(500);
  digitalWrite(trigPin, LOW);

  // Meet de duur van de puls op echoPin
  duur = pulseIn(echoPin, HIGH);
  // Bereken afstand in cm (geluidssnelheid = 343 m/s = 0.0343 cm/μs)
  afstand = (duur * 0.0343) / 2;

  // Toon afstand
  Serial.print("Afstand = ");
  Serial.print(afstand);
  Serial.println(" cm");

  delay(100); // Korte pauze voor stabiliteit

  if (afstand < 2.00) {
    setColor(255, 0, 0); // Rood
  } else {
    setColor(0, 0, 0);   // Uit
  }

  delay(100);
}

void setColor(int redValue, int greenValue,  int blueValue) {
  analogWrite(roodPin, redValue);
  analogWrite(groenPin,  greenValue);
  analogWrite(blauwPin, blueValue);
}