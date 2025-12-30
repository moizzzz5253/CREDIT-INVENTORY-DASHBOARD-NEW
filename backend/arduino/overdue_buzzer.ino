/*
 * Overdue Detection Buzzer Controller
 * 
 * This Arduino sketch controls a buzzer for overdue email notifications.
 * 
 * Commands:
 * - "SUCCESS": 2 pulses with 1 second delay between them
 * - "FAILURE": 3 short pulses with 0.5 second delay between them
 * - "TEST": Responds with "READY" for connection testing
 * 
 * Hardware:
 * - Buzzer connected to pin 9 (or change BUZZER_PIN below)
 * - Connect buzzer positive to pin 9, negative to GND
 * 
 * Serial Settings:
 * - Baud Rate: 9600 or 115200 (auto-detected by Python)
 */

const int BUZZER_PIN = 9;  // Change this to your buzzer pin
const int SUCCESS_PULSE_DURATION = 500;  // 500ms for success pulse
const int FAILURE_PULSE_DURATION = 200;  // 200ms for failure pulse (short)
const int SUCCESS_DELAY = 1000;  // 1 second delay between success pulses
const int FAILURE_DELAY = 500;   // 0.5 second delay between failure pulses

String inputString = "";  // String to hold incoming data
boolean stringComplete = false;  // Whether the string is complete

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Initialize buzzer pin
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);
  
  // Reserve 200 bytes for the inputString
  inputString.reserve(200);
  
  // Send ready signal
  Serial.println("READY");
  
  // Brief startup beep
  tone(BUZZER_PIN, 1000, 100);
  delay(200);
}

void loop() {
  // Read serial input
  while (Serial.available() > 0) {
    char inChar = (char)Serial.read();
    
    // Add character to input string
    inputString += inChar;
    
    // If newline character, string is complete
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
  
  // Process complete string
  if (stringComplete) {
    // Remove whitespace and convert to uppercase
    inputString.trim();
    inputString.toUpperCase();
    
    // Process command
    if (inputString == "SUCCESS") {
      triggerSuccessBuzzer();
    } else if (inputString == "FAILURE") {
      triggerFailureBuzzer();
    } else if (inputString == "TEST") {
      Serial.println("READY");
    }
    
    // Clear the string for next input
    inputString = "";
    stringComplete = false;
  }
}

void triggerSuccessBuzzer() {
  // 2 pulses with 1 second delay between them
  for (int i = 0; i < 2; i++) {
    tone(BUZZER_PIN, 1000, SUCCESS_PULSE_DURATION);
    delay(SUCCESS_PULSE_DURATION);
    
    // Wait 1 second before next pulse (except after last pulse)
    if (i < 1) {
      delay(SUCCESS_DELAY);
    }
  }
}

void triggerFailureBuzzer() {
  // 3 short pulses with 0.5 second delay between them
  for (int i = 0; i < 3; i++) {
    tone(BUZZER_PIN, 800, FAILURE_PULSE_DURATION);
    delay(FAILURE_PULSE_DURATION);
    
    // Wait 0.5 seconds before next pulse (except after last pulse)
    if (i < 2) {
      delay(FAILURE_DELAY);
    }
  }
}







