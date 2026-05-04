import processing.serial.*;
import java.io.PrintWriter;

// Serial connection
Serial arduinoPort;

// File output
PrintWriter csvWriter;
String outputFile = "heart_rate_raw.csv";

// Sampling settings
int samplingRate = 250;  // Hz
float samplingInterval = 1000.0 / samplingRate;  // 4 ms if sampling rate is 250 Hz
float currentTime = 0;
boolean loggingStarted = false;  // Flag to check if logging has started
long startMillis;  // Variable to store start time

// Data arrays for real-time plotting
ArrayList<Float> timeData = new ArrayList<Float>();
ArrayList<Float> signalData = new ArrayList<Float>();

// Plotting settings
int maxPoints = 500;  // Maximum number of points to display
float yMin = -10;  
float yMax = 1024;  // Arduino Uno's 10-bit ADC range (0-1023)

void setup() {
  size(800, 400);
  println(Serial.list());  // List available ports
  arduinoPort = new Serial(this, "COM7", 9600);  // Replace "COM7" with your port if necessary
  arduinoPort.bufferUntil('\n');
  
  csvWriter = createWriter(outputFile);
  csvWriter.println("Time (ms),Heart Signal");
  println("Saving data to " + outputFile);
  
  startMillis = millis();  // Store the starting time
}

void draw() {
  background(255);
  stroke(0);
  fill(0);
  
  // Draw axis
  textSize(14);
  text("Heart Signal (Real-Time)", width / 2 - 80, 20);
  line(50, 350, 750, 350);  // X-axis
  line(50, 50, 50, 350);    // Y-axis
  text("Time (ms)", width / 2 - 20, 380);
  text("Signal", 10, 200);
  
  // Scale data
  float xScale = 700.0 / maxPoints;  // Map time to width
  float yScale = 300.0 / (yMax - yMin);  // Map signal to height
  
  // Plot data
  noFill();
  stroke(0, 0, 255);
  beginShape();
  for (int i = 0; i < timeData.size(); i++) {
    float x = 50 + i * xScale;
    float y = 350 - (signalData.get(i) - yMin) * yScale;
    vertex(x, y);
  }
  endShape();
  
  // If the delay is over, start logging data
  if (!loggingStarted && (millis() - startMillis >= 200)) {
    loggingStarted = true;  // Logging starts after 200 ms to improve stability
    println("Starting data logging after 200ms delay...");
  }
}

void serialEvent(Serial port) {
  String data = port.readStringUntil('\n');
  if (data != null && loggingStarted) {  // Process data if logging has started
    try {
      float signal = float(trim(data));
      timeData.add(currentTime);
      signalData.add(signal);
      
      // Keep data arrays within maxPoints limit
      if (timeData.size() > maxPoints) {
        timeData.remove(0);
        signalData.remove(0);
      }
      
      // Save data to CSV, starting from 0
      csvWriter.println(currentTime + "," + signal);
      
      // Increment time
      currentTime += samplingInterval;
    } catch (Exception e) {
      println("Error processing data: " + e.getMessage());
    }
  }
}

void keyPressed() {
  if (key == 'q' || key == 'Q') {
    csvWriter.flush();
    csvWriter.close();
    println("Data saved to " + outputFile);
    exit();
  }
}
