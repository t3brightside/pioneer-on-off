const int controlPin = 3;

// Common Pioneer Amp Power Toggle code (A55A38C7)
// If this doesn't work, we will try the 16-bit A35C variation.
uint32_t pioneerCode = 0xA55A38C7;

void setup() {
  // CRITICAL: Set to HIGH immediately so the line idles at 5V
  pinMode(controlPin, OUTPUT);
  digitalWrite(controlPin, HIGH); 
  Serial.begin(9600);
  Serial.println("Pioneer M-10X Active-Low Controller Ready.");
}

void sendInvertedPulse(int timeMicro) {
  digitalWrite(controlPin, LOW);  // Pulse is LOW
  delayMicroseconds(timeMicro);
  digitalWrite(controlPin, HIGH); // Return to HIGH (Idle)
}

void sendPioneerCommand(uint32_t data) {
  // 1. Header: 9ms LOW, 4.5ms HIGH
  digitalWrite(controlPin, LOW);
  delayMicroseconds(9000);
  digitalWrite(controlPin, HIGH);
  delayMicroseconds(4500);

  // 2. Data bits
  for (int i = 0; i < 32; i++) {
    bool bit = (data >> (31 - i)) & 1;
    
    // Pulse low for 560us
    digitalWrite(controlPin, LOW);
    delayMicroseconds(560);
    digitalWrite(controlPin, HIGH);

    // Space high: 1690us for '1', 560us for '0'
    if (bit) delayMicroseconds(1690);
    else delayMicroseconds(560);
  }

  // 3. Stop bit
  digitalWrite(controlPin, LOW);
  delayMicroseconds(560);
  digitalWrite(controlPin, HIGH);
}

void loop() {
  if (Serial.available() > 0) {
    if (Serial.read() == '1') {
      Serial.println("Sending Active-Low Command...");
      sendPioneerCommand(pioneerCode);
    }
  }
}