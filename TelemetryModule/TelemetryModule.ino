/*
  ReadAnalogVoltage
  Reads an analog input on pin 0, converts it to voltage, and prints the result to the serial monitor.
  Graphical representation is available using serial plotter (Tools > Serial Plotter menu)
  Attach the center pin of a potentiometer to pin A0, and the outside pins to +5V and ground.


  Current divider

  A0 ----- R2 -------- GND ----
                  |           |
                  R1          |
                  |           |
                  SIGNAL+ --SIGNAL------------------------------------------------
                                                                                  |
  A1 ------ ACS712 (20A) ----- SIGNAL B+ -------- [USB CIRCUIT] ----- SIGNAL B- ---

  https://startingelectronics.org/articles/arduino/measuring-voltage-with-arduino/
*/

int debug=false;

void dump(char *msg)
{
  if (true)
  {
    Serial.println(msg);
  }
}

struct sensortype
{
  float fps;        // +4 = 4
  float voltage;     // +4 = 8
  float current;     // +4 = 12
  int freq;          // +2 = 14
  int counter;       // +2 = 16
} sensor;


// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
  stopburst();
}


// the loop routine runs over and over again forever:
void loop() {
  unsigned long currentMillis = millis();
  
  sensor.freq = freq();
  sensor.fps = 0.0;

  int incomingByte;

  int action, controlvalue;
  
  if (checksensors())
  {
    // Put here all the sensor information that you want to do only when you are transmitting the information.
    //senseCurrentAndVoltage();
  }
  senseCurrentAndVoltage();
  burstsensors();

  incomingByte = 0;//getcommand();
  bool doaction = false;

  if (incomingByte > 0)
  {
    doaction = true;
  }
  
  if (Serial.available() > 0) {
    incomingByte = Serial.read();
    doaction = true;
  }

  if (doaction) 
  {
    switch (incomingByte) {
      case 'I':
        dump("SSMR");
        break;  
      case 'D':
        debug = (!debug);
        break;
      case 'A':
        readcommand(action, controlvalue);
        switch (action) {
          case 0x0b:
            setBurstSize(controlvalue);
            break;
          case 0x0c:
            payloadsize();
            break;
          case 0x0d:
            payloadstruct();
            break;
          case 0x0e:
            setUpdateFreq(controlvalue);
            break;
          default:
            break;
        }
        break;
      case 'S':
        startburst();
        break;
      case 'X':
        stopburst();
        break;
      case 'P':
        senseCurrentAndVoltage();
        break;
      default:
        break;
    }
  }
}

