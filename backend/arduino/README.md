# Arduino Buzzer Setup for Overdue Detection

This directory contains the Arduino code for the buzzer notification system that alerts when overdue email checks are performed.

## Hardware Requirements

- Arduino board (Uno, Nano, or compatible)
- Buzzer (active or passive)
- Jumper wires

## Wiring

1. Connect buzzer positive terminal to **Pin 9** on Arduino
2. Connect buzzer negative terminal to **GND** on Arduino

**Note:** If you want to use a different pin, change `BUZZER_PIN` in the Arduino code.

## Software Setup

### 1. Install Arduino IDE

Download and install Arduino IDE from [arduino.cc](https://www.arduino.cc/en/software)

### 2. Upload Code

1. Open `overdue_buzzer.ino` in Arduino IDE
2. Select your Arduino board and port from Tools menu
3. Click Upload button

### 3. Verify Connection

After uploading, open Serial Monitor (Tools → Serial Monitor) and set baud rate to 9600. You should see "READY" message.

## How It Works

The Arduino receives commands from the Python backend via serial communication:

- **SUCCESS**: Triggers 2 buzzer pulses with 1 second delay between them
  - Sent when overdue emails are successfully sent to borrowers
  
- **FAILURE**: Triggers 3 short buzzer pulses with 0.5 second delay between them
  - Sent when overdue email check fails or emails cannot be sent

- **TEST**: Responds with "READY" for connection testing

## Serial Communication

- **Baud Rate:** 9600 (or 115200 - auto-detected by Python)
- **Format:** Commands sent as text strings ending with newline (`\n`)

## Troubleshooting

### Arduino Not Detected

1. Check USB cable connection
2. Verify Arduino drivers are installed
3. Check Device Manager (Windows) or `ls /dev/tty*` (Linux/Mac) for COM port
4. Try different USB port or cable

### Buzzer Not Working

1. Verify wiring (positive to Pin 9, negative to GND)
2. Test buzzer directly with 5V and GND
3. Check if buzzer is active or passive (code uses `tone()` which works with both)
4. Try changing `BUZZER_PIN` to a different pin

### Serial Communication Issues

1. Close Serial Monitor in Arduino IDE (only one program can access serial port)
2. Check baud rate matches (9600 or 115200)
3. Restart Arduino by unplugging and replugging USB
4. Check Python logs for connection errors

## Customization

### Change Buzzer Pin

Edit `BUZZER_PIN` constant in the code:
```cpp
const int BUZZER_PIN = 9;  // Change to your pin
```

### Adjust Pulse Durations

Edit these constants:
```cpp
const int SUCCESS_PULSE_DURATION = 500;  // milliseconds
const int FAILURE_PULSE_DURATION = 200;  // milliseconds
```

### Adjust Delays

Edit these constants:
```cpp
const int SUCCESS_DELAY = 1000;  // 1 second between success pulses
const int FAILURE_DELAY = 500;   // 0.5 seconds between failure pulses
```

## Testing

You can test the buzzer manually using Serial Monitor:

1. Open Serial Monitor (9600 baud)
2. Type `SUCCESS` and press Enter → Should hear 2 pulses
3. Type `FAILURE` and press Enter → Should hear 3 short pulses
4. Type `TEST` and press Enter → Should see "READY" response







