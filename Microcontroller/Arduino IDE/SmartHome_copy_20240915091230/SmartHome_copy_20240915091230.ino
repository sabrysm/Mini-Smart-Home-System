#define pirPin 17
#define ldrPin 19
#define SER 10
#define RCLK 11
#define SRCLK 13
#define servoPin 8
#define tempPin 18
#define MOTOR_IN1_PIN 16
#define MOTOR_IN2_PIN 12
#define enablePin 3
const int WHITE_LED = 0;    // Q0 -> White Led
const int BUZZER_PIN = 1; // Q1 -> Buzzer
const int RED_LED = 5; // Q5 -> Red Led
const int GREEN_LED = 6; // Q6 -> Green Led
const int BLUE_LED = 7; // Q7 -> Blue Led
bool doorOpen = false;
#include <Servo.h>
#include <Keypad.h>

// Keypad configuration
const byte ROWS = 4;
const byte COLS = 4;
const char keys[ROWS][COLS] = {
  {'1', '2', '3', 'A'},
  {'4', '5', '6', 'B'},
  {'7', '8', '9', 'C'},
  {'*', '0', '#', 'D'}
};
const byte rowPins[ROWS] = {14, 15, 7, 6};
const byte colPins[COLS] = {5, 4, 2, 9};
Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

// Thermistor and servo setup
const float nominalResistance = 10000.0;
const float nominalTemperature = 25.0;
const float bCoefficient = 3950;
const int seriesResistor = 10000;
const char correctPassword[] = "1234";  // Correct password
char inputPassword[5];  // Buffer for 4-digit password + null terminator
byte inputPos = 0;
byte dataToSend = 0b00000000;
Servo myservo;

void setup() {
    Serial.begin(9600);
    keypad.setDebounceTime(10);
    pinMode(pirPin, INPUT);
    pinMode(SER, OUTPUT);
    pinMode(RCLK, OUTPUT);
    pinMode(SRCLK, OUTPUT);
    pinMode(MOTOR_IN1_PIN, OUTPUT);
    pinMode(MOTOR_IN2_PIN, OUTPUT);
    pinMode(enablePin, OUTPUT);
    // Initialize all components to OFF
    setWhiteLed(false);
    setBuzzer(false);
    setMotor(false);   // Stop motor
    myservo.attach(servoPin);
    setServo(false);
    resetPassword();
}

void loop() {
    float temperatureC = readTemperature();
    char keyPressed = keypad.getKey();
    if (doorOpen) {
        //Serial.println(F("Door is open"));
        controlRgbLedBuzzerAndFan(temperatureC);
        checkLightIntensity();
        controlServoAndWhiteLed();
    }
    handleKeyPressed(keyPressed);
    checkFace();
    delay(200);
}

void handleKeyPressed(char keyPressed) {
    if (keyPressed) {
        Serial.print(F("Key pressed: "));
        Serial.println(keyPressed);
        checkPassword(keyPressed);  // Process the key press
    }
}

void checkPassword(char keyPressed) {
    if (keyPressed == '#') {
        // Validate the entered password
        if (inputPos == 4) {  // Only check if exactly 4 digits are entered
            Serial.print(F("Entered password: "));
            Serial.println(inputPassword);

            // Send data to Python serial
            Serial.println(inputPassword);

        } 
        // else {
        //     Serial.println(F("Password must be exactly 4 digits."));
        //     triggerBuzzer();        // Alert with buzzer
        //     turnOffAll();
        // }
        resetPassword();  // Reset password input after checking
    } else if (keyPressed == '*') {
        resetPassword();  // Reset if '*' is pressed
        Serial.println(F("Password reset."));
    } else if (inputPos < 4 && keyPressed != '*' && keyPressed != '#') {
        inputPassword[inputPos++] = keyPressed;  // Add key to password
        inputPassword[inputPos] = '\0';  // Ensure null termination for strcmp
        Serial.print(F("Current input: "));
        Serial.println(inputPassword);
    } else {
        Serial.println(F("Maximum 4 digits allowed."));
        resetPassword();  // Reset if '*' is pressed
        Serial.println(F("Password reset."));
    }
}
void checkFace() {
  if (Serial.available() > 0) {
    char data = Serial.read();  // Read the incoming data
    
    if (data == '1' && !doorOpen) {
      Serial.println("Face Recognized");
      triggerBuzzer();    // Alert with buzzer
      makeDoorState("open");
      delay(500);         // Keep it open for 500ms
    } else if (data == '0' && doorOpen) {
      Serial.println("Face Unrecognized");
      turnOffAll();       // Turn off all components
    }
  }
}

void resetPassword() {
    memset(inputPassword, 0, sizeof(inputPassword));  // Clear the input buffer
    inputPos = 0;  // Reset input position
}

void triggerBuzzer() {
    setBuzzer(true);
    delay(500);
    setBuzzer(false);
}

// Function to turn off all components
void turnOffAll() {
    setWhiteLed(false);
    setBlueLed(false);
    setGreenLed(false);
    setRedLed(false);
    setBuzzer(false);
    setMotor(false);    // Stop motor
    makeDoorState("off");
}


void makeDoorState(const char* state) {
    if (strcmp(state, "open") == 0) {
        setServo(true);
        doorOpen=true;
    } else {
        setServo(false);
        doorOpen=false;
    }
}

void setMotor(bool state) {
    if (state) {
        // Motor Forward (IN1 = 1, IN2 = 0)
        digitalWrite(MOTOR_IN1_PIN, HIGH);
        digitalWrite(MOTOR_IN2_PIN, LOW);
    } else {
        // Motor Stop (IN1 = 0, IN2 = 0)
        digitalWrite(MOTOR_IN1_PIN, LOW);
        digitalWrite(MOTOR_IN2_PIN, LOW);
    }
}

void setServo(bool state) {
    if (state) {
      myservo.write(90);  // Open servo (e.g., to 90 degrees)
    } else {
      myservo.write(0);   // Reset servo (e.g., back to 0 degrees)
    }
}

void checkLightIntensity() {
    int ldrReading = analogRead(ldrPin);
    if (ldrReading < 120) {
        //Serial.println(F("Dark"));
        setWhiteLed(true);
    } else {
       //Serial.println(F("Bright"));
        setWhiteLed(false);
    }
}

void controlRgbLedBuzzerAndFan(float temperatureC) {
    // Turn off all LEDs before setting the correct one
    Serial.println(F("Tempreature:"));
    Serial.println(temperatureC);
    if (temperatureC > 40) {
        setRedLed(true);
        setGreenLed(false);
        setBlueLed(false);
        controlFanSpeed(2);
    } else if (temperatureC > 30) {
        setGreenLed(true);
        setRedLed(false);
        setBlueLed(false);
        controlFanSpeed(1);
    } else {
        setBlueLed(true);
        setGreenLed(false);
        setRedLed(false);
        controlFanSpeed(0);
    }
}

void controlFanSpeed(int speed) {
    /*
    Speed 0: Fan off
    Speed 1: Low speed
    Speed 2: High speed
    */
    if (speed == 0) {
        //Serial.println(F("Fan speed: 0 (Off)"));
        analogWrite(enablePin, 0);
        setMotor(false);
    } else if (speed == 1) {
        //Serial.println(F("Fan speed: 1 (Medium)"));
        analogWrite(enablePin, 128);
        setMotor(true);
    } else {
        //Serial.println(F("Fan speed: 2 (High)"));
        analogWrite(enablePin, 255);
        setMotor(true);
    }
}

void controlServoAndWhiteLed() {
    if (digitalRead(pirPin) == HIGH) {
        Serial.println(F("Motion detected!!!!!"));
    }
}

void setGreenLed(bool state) {
    if (state) {
      dataToSend |= (1 << GREEN_LED);
    } else {
      dataToSend &= ~(1 << GREEN_LED);
    }
    shiftOut(dataToSend);  // Send updated data to shift register
}

void setRedLed(bool state) {
    if (state) {
      dataToSend |= (1 << RED_LED);
    } else {
      dataToSend &= ~(1 << RED_LED);
    }
    shiftOut(dataToSend);  // Send updated data to shift register
}

void setBlueLed(bool state) {
    if (state) {
      dataToSend |= (1 << BLUE_LED);
    } else {
      dataToSend &= ~(1 << BLUE_LED);
    }
    shiftOut(dataToSend);  // Send updated data to shift register
}

void setWhiteLed(bool state) {
    if (state) {
        dataToSend |= (1 << WHITE_LED);  // Turn on LED
    } else {
        dataToSend &= ~(1 << WHITE_LED); // Turn off LED
    }
    shiftOut(dataToSend);  // Send updated data to shift register
}

void setBuzzer(bool state) {
    if (state) {
        dataToSend |= (1 << BUZZER_PIN);  // Turn on Buzzer
    } else {
        dataToSend &= ~(1 << BUZZER_PIN); // Turn off Buzzer
    }
    shiftOut(dataToSend);  // Send updated data to shift register

}
// Temperature reading function
float readTemperature() {
    int tempReading = analogRead(tempPin);
    float voltage = tempReading * (5.0 / 1023.0);
    float ntcResistance = seriesResistor / ((5.0 / voltage) - 1);
    float steinhart = log(ntcResistance / nominalResistance);
    steinhart /= bCoefficient;
    steinhart += 1.0 / (nominalTemperature + 273.15);
    return (1.0 / steinhart) - 273.15 + 20;
}

void shiftOut(byte data) {
    for (int i = 7; i >= 0; i--) {  // Loop over each bit (MSB first)
        digitalWrite(SER, (data >> i) & 0x01);  // Write each bit to SER

        // Pulse the shift clock
        digitalWrite(SRCLK, HIGH);
        delayMicroseconds(5);  // Small delay for stability
        digitalWrite(SRCLK, LOW);
    }

    // Pulse the storage register clock to update the outputs
    digitalWrite(RCLK, HIGH);
    delayMicroseconds(5);  // Small delay for stability
    digitalWrite(RCLK, LOW);
}
