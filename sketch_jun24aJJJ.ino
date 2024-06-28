const int led_pin = LED_BUILTIN;  // Pin for the built-in LED
//int green = 11;
void setup() {
  pinMode(led_pin, OUTPUT);  // Initialize the LED pin as an output
  //pinMode(green,  OUTPUT);
  Serial.begin(9600);  // Begin serial communication at 9600 baud rate
  while (!Serial) {
    ; // Wait for serial port to connect. Needed for native USB port only
  }
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');  // Read the command from serial

    if (command.startsWith("JOB")) {
      // Parse the command to extract job details
      int job_id, rid, start_time, finish_time;
      sscanf(command.c_str(), "JOB|%d|%d|%d|%d", &job_id, &rid, &start_time, &finish_time);
      
      int processing_time = finish_time - start_time;

      // Handle setup time if provided
      if (command.startsWith("SETUP")) {
        int setup_time;
        sscanf(command.c_str(), "SETUP|%d", &setup_time);
        
        // Hold the LED high for setup time duration
        digitalWrite(led_pin, HIGH);
        delay(setup_time * 1000);  // Convert seconds to milliseconds
        
      }

      // Start time for the job processing
      unsigned long job_start_time = millis();

      // Blink the LED for processing time
      for (int i = 0; i < processing_time; i++) {
        digitalWrite(led_pin, HIGH);  // Turn the LED on
        delay(500);  // Wait for 500 milliseconds
        digitalWrite(led_pin, LOW);  // Turn the LED off
        delay(500);  // Wait for 500 milliseconds
      }

      // End time for the job processing
      unsigned long job_end_time = millis();

      // Send a response back to the Flask application with start and end times
      Serial.print("JOB_COMPLETED|");
      Serial.print(job_id);
      Serial.print("|");
      Serial.print(job_start_time);
      Serial.print("|");
      Serial.println(job_end_time);
    }
  }
}
