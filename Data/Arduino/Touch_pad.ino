#if defined(ARDUINO_ARCH_SAMD)
  #define SERIAL Serial
  #define TRANS_SERIAL Serial1
#else
  #include <SoftwareSerial.h>
  SoftwareSerial mySerial(2, 3);
  #define SERIAL Serial
  #define TRANS_SERIAL mySerial
#endif

void setup() {
  TRANS_SERIAL.begin(9600);  // UART van keypad
  SERIAL.begin(9600);        // USB naar computer
  while (!SERIAL);           // Wacht tot USB actief is
  SERIAL.println("Start: Capacitive Keypad UART v1.0");
}

void loop() {
  printData();
}

void printData() {
  while (TRANS_SERIAL.available()) {
    uint8_t data = TRANS_SERIAL.read();
    switch (data) {
      case 0xE1: SERIAL.println("1"); break;
      case 0xE2: SERIAL.println("2"); break;
      case 0xE3: SERIAL.println("3"); break;
      case 0xE4: SERIAL.println("4"); break;
      case 0xE5: SERIAL.println("5"); break;
      case 0xE6: SERIAL.println("6"); break;
      case 0xE7: SERIAL.println("7"); break;
      case 0xE8: SERIAL.println("8"); break;
      case 0xE9: SERIAL.println("9"); break;
      case 0xEA: SERIAL.println("*"); break;
      case 0xEB: SERIAL.println("0"); break;
      case 0xEC: SERIAL.println("#"); break;
      default: 
        SERIAL.print("Onbekend byte: 0x");
        SERIAL.println(data, HEX);
        break;
    }
  }
}
