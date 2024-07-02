const int led_pin = 13;  // Pin for the built-in LED
const int led_pin2 = 12;
void setup() {
  pinMode(led_pin, OUTPUT);  // Initialize the LED pin as an output
  pinMode(led_pin2, OUTPUT);
  Serial.begin(9600);  // Begin serial communication at 9600 baud rate
  while (!Serial) {
    ; // Wait for serial port to connect. Needed for native USB port only
  }
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');  // Read the command from serial

    if (command.startsWith("SETUP")) {
      int setup_time;
      sscanf(command.c_str(), "SETUP|%d", &setup_time);

      // Hold the LED high for setup time duration
      digitalWrite(led_pin2, HIGH);
      delay(setup_time * 1000);  // Convert seconds to milliseconds
      digitalWrite(led_pin2, LOW);  // Turn the LED off after setup time
    } 
    else if (command.startsWith("JOB")) {
      // Parse the command to extract job details
      int job_id, rid, start_time, finish_time;
      sscanf(command.c_str(), "JOB|%d|%d|%d|%d", &job_id, &rid, &start_time, &finish_time);
      
      int processing_time = finish_time - start_time;

      // Blink the LED for processing time
      for (int i = 0; i < processing_time; i++) {
        digitalWrite(led_pin, HIGH);  // Turn the LED on
        delay(500);  // Wait for 500 milliseconds
        digitalWrite(led_pin, LOW);  // Turn the LED off
        delay(500);  // Wait for 500 milliseconds
      }

      // Send a response back to the Flask application indicating job completion
      Serial.println("JOB_COMPLETED");
    }
  }
}
