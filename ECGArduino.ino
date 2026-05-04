unsigned long previousTime = 0; // Store the last sampling time
const int samplingInterval = 4; // 4 milliseconds for 250 Hz sampling rate

void setup() {
  Serial.begin(9600); // Indicate that the serial port is capable of transferring a maximum of 9600 bits/s
}

void loop() {
  unsigned long currentTime = millis(); // Get the current time in milliseconds

  if (currentTime - previousTime >= samplingInterval) {
    previousTime = currentTime; // 

    int signal = analogRead(A0); // Read the signal from the A0 port of Arduino Uno connected to AD8232
    Serial.println(signal);      // Send the signal to the serial monitor
  }
}