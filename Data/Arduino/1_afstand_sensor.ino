const int trigPin = 12;
const int echoPin = 8;

float duur;
float afstand;

void setup() {
  Serial.begin(9600);               // Start seriële communicatie
  pinMode(trigPin, OUTPUT);         // trigPin als output
  pinMode(echoPin, INPUT);          // echoPin als input
}

void loop() {
  // Zorg dat de trigPin laag is
  digitalWrite(trigPin, LOW);
  delay(200);

  // Stuur een korte puls van 10 microseconden
  digitalWrite(trigPin, HIGH);
  delay(1000);
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
}
