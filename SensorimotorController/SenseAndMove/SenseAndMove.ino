/**
   ShinkeyBot - Sensorimotor

   Fuse senses and move the robot wheels.

   HR-SR04 - Distance Sensor
       VCC to Arduino 5v
       GND to Arduino GND
       Echo to Arduino Pin 13
       Trig to Arduino Pin 12
       Red Led to Arduino Pin 11
       Green Led to Arduino Pin 10
       560 ohm resistor to both Led Neg and GND Power rail
       http://goo.gl/kJ8Gl
       http://en.wikiversity.org/wiki/User:Dstaub/robotcar

       Motor Wheel: Pin 5,4,3,2.

       Pan And Tilt Controller: Analog 0(14) tilt, Analog 1(15) pan (on Arduino)
       Digital 6 tilt, Digital 7 Pan on Mega.
*/

#include <stdarg.h>
void p(char *fmt, ... ){
        char buf[128]; // resulting string limited to 128 chars
        va_list args;
        va_start (args, fmt );
        vsnprintf(buf, 128, fmt, args);
        va_end (args);
        Serial.print(buf);
}

//#define trigPin 13
//#define echoPin 12

#define trigPin 22
#define echoPin 23

#define tiltServoPin 24
#define panServoPin  25

bool debug = false;

#define MAX_SIZE_SENSOR_BURST 100

int IN4 = 5;
int IN3 = 4;
int IN2 = 3;
int IN1 = 2;


// constants won't change. Used here to set a pin number :
const int ledPin =  8;      // the number of the LED pin
const int laserPin = 8;

// Variables will change :
int ledState = HIGH;             // ledState used to set the LED

// Generally, you should use "unsigned long" for variables that hold time
// The value will quickly become too large for an int to store
unsigned long previousMillis = 0;        // will store last time LED was updated

// duration of movement.
long interval = 2000;           // interval of duration of movement



struct sensortype
{
  double onYaw;     // +4
  double onPitch;   // +4 = 8
  double onRoll;    // +4 = 12
  float T;          // +4 = 16
  float P;          // +4 = 20
  double light;     // +4 = 24
  int yaw;          // +2 = 26
  int pitch;        // +2 = 28
  int roll;         // +2 = 30
  int geoYaw;       // +2 = 32
  int geoPitch;     // +2 = 34
  int geoRoll;      // +2 = 36
  int sound;        // +2 = 38
  int freq;         // +2 = 40
  int counter;      // +2 = 42

} sensor;


bool serialOpen = 1;

bool sensorburst = false;


void dump(char *msg)
{
  if (serialOpen)
  {
    Serial.println(msg);
  }
}

int leftorright() {
  return random(2) + 4;
}


void setupMotor()
{
  pinMode (IN4, OUTPUT);    // Input4 conectada al pin 4
  pinMode (IN3, OUTPUT);    // Input3 conectada al pin 5
  pinMode (IN2, OUTPUT);    // Input4 conectada al pin 3
  pinMode (IN1, OUTPUT);    // Input3 conectada al pin 2

  // set the digital pin as output:
  pinMode(ledPin, OUTPUT);

  pinMode(laserPin, OUTPUT);

  randomSeed(analogRead(0));

  sensorburst = false;
  initsensors();
}


void setup() {
  Serial.begin (9600);
  dump("Sensorimotor Cortex");

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  setupMotor();
  setupPanAndTilt();
  setupEnvironmentSensor();
  setupir();
}

int const QUIET = 0;
int const STILL = 1;
int const MOVE_FORWARD = 2;
int const MOVE_BACKWARDS = 3;
int const RIGHT = 4;
int const LEFT = 5;

int const STAYSTILL = 6;
int const WANDERING = 1;

// L3 &&  L1 is BACKWARDS
int motorstate = QUIET;
int sampleCounter = 0;

int noAction = STAYSTILL;


int const RELAXED = 0;
int const PHOTOTROPISM = 1;
int const PHONOTROPISM = 2;
int const MAGNETOTROPISM = 3;

int limbic = RELAXED;

char buffer[4];
int value=0;

char readcommand()
{
  int readbytes = Serial.readBytes(buffer,4);
  char action = 0;
  
  if (readbytes == 4) {
    action = buffer[0];
    
    value = atoi(buffer+1); 

    if (debug) {
      Serial.print("Action:");
      Serial.print(action);
      Serial.print("/");
      Serial.println(value);
    }  
  }
  return action;
}

int fps()
{
  static int freqValue=200;
  static int freqCounter=0;
  static unsigned long myPreviousMillis = millis();
  unsigned long myCurrentMillis=0;

  myCurrentMillis = millis();
  
  if ((myCurrentMillis - myPreviousMillis)>1000)
  {
    if (debug) 
    {
      Serial.print("Frequency:");Serial.println(freqCounter);
    }
    myPreviousMillis = myCurrentMillis;
    freqValue = freqCounter;
    freqCounter=0;
  }
  else
  {
    freqCounter++;
  }  
  return freqValue;
}

void blinkme()
{
  // here is where you'd put code that needs to be running all the time.

  // check to see if it's time to blink the LED; that is, if the
  // difference between the current time and last time you blinked
  // the LED is bigger than the interval at which you want to
  // blink the LED.
  unsigned long currentMillis = millis();
  
  sensor.freq = fps();

  int incomingByte;

  char action;
  
  if (sensorburst)
  {
    checksensors();
    transmitsensor();
    sampleCounter++;
    if (sampleCounter > MAX_SIZE_SENSOR_BURST)
    {
      sensorburst = false;
      sampleCounter = 0;
    }
  }

  loopPanAndTilt();

  incomingByte = getcommand();
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
        action = readcommand();
        switch (action) {
          case 'F':
            setPanTgtPos(value);
            break;
          case 'T':
            setTiltTgtPos(value);
            break;
          default:
            break;
        }
        break;
      case 'H':
        if (debug) {
          Serial.println("Pan to 0");
        }
        setPanTgtPos(0);
        break;
      case 'F':
        if (debug) {
          Serial.println("Pan to 180");
        }
        setPanTgtPos(180);
        break;
      case 'G':
        if (debug) {
          Serial.println("Reset Pan and tilt.");
        }
        setPanTgtPos(90);
        setTiltTgtPos(95);
        break;
      case 'T':
        if (debug) {
          Serial.println("Tilt to 170");
        }
        setTiltTgtPos(170);
        break;
      case 'P':
        getBarometricData(sensor.T, sensor.P);
        break;
      case 'S':
        sensorburst = true;
        // Reset counter to avoid loosing data.
        sampleCounter=0;
        break;
      case 'X':
        sensorburst = false;
        break;
      case 'W':
        if (debug) {
          Serial.println("Wandering");
        }
        noAction = WANDERING;
        break;
      case 'C':
        if (debug) {
          Serial.println("Stay Still");
        }
        noAction = STAYSTILL;
        break;
      case 'L':
        if (debug) {
          Serial.println("Laser on");
        }
        digitalWrite(laserPin, HIGH);
        break;
      case 'l':
        if (debug) {
          Serial.println("Laser off");
        }
        digitalWrite(laserPin, LOW);
        break;
      case 'E':
        if (debug) {
          Serial.println("Empire");
        }
        march();
      case 'B':
        if (debug) {
          Serial.println("Buzzer");
        }
        buzz();
      case '-':
        interval = 100;
        break;
      case '+':
        interval = 2000;
        break;
      default:
        if (48 < incomingByte && incomingByte < 58)
        {
          if (debug) {
            Serial.println("Driving");
          }
          motorstate = incomingByte - 48;
          previousMillis = currentMillis;
        }
        break;
    }

  }
  else if (currentMillis - previousMillis >= interval) {
    // save the last time you blinked the LED
    previousMillis = currentMillis;

    // if the LED is off turn it on and vice-versa:
    if (ledState == LOW)
      ledState = HIGH;
    else
      ledState = LOW;

    // set the LED with the ledState of the variable:
    //digitalWrite(ledPin, ledState);

    //Serial.println(limbic);

    switch (limbic) {
      case PHONOTROPISM:
        buzz();
        break;
    }

//    switch (limbic) {
//      case PHOTOTROPISM:
//        motorstate = MOVE_FORWARD;
//        break;
//      case PHONOTROPISM:
//        motorstate = leftorright();
//        break;
//      default:
//        checksensors();// 320 320 160
//        if (debug) p("Geo: %4d, %4d, %4d \n",  sensor.geoYaw, sensor.geoPitch, sensor.geoRoll);
//        if ( (abs(sensor.geoYaw-320)<50) && (abs(sensor.geoPitch-320)<50) && (abs(sensor.geoRoll-160)<50) ) {
//          if (debug) p("FOLLOW!");
//          //motorstate = QUIET;  
//        } else {
//          //motorstate = LEFT;
//        }
//        
//        //long randNumber = random(14);
//        // Plus one is to eliminate the chance to fallback in quit mode
//        //motorstate = ((int)randNumber) + noAction;
//        break;
//    }
    motorstate = QUIET;  
    limbic = QUIET;

  }

}

void loopMotor()
{
  blinkme();

  //if (ledState == HIGH)
  switch (motorstate)
  {
    case MOVE_BACKWARDS:
      // Move Backward.
      //Serial.println("Moving!");
      digitalWrite (IN4, HIGH);
      digitalWrite (IN3, LOW);
      digitalWrite (IN2, HIGH);
      digitalWrite (IN1, LOW);
      break;
    case MOVE_FORWARD:
      // Go ahead and move forward
      //Serial.println("Moving!");
      digitalWrite (IN4, LOW);
      digitalWrite (IN3, HIGH);
      digitalWrite (IN2, LOW);
      digitalWrite (IN1, HIGH);
      break;
    case LEFT:
      // Move the right caterpiller
      //Serial.println("Moving!");
      digitalWrite (IN4, HIGH); // LOW, HIGH for back
      digitalWrite (IN3, LOW);
      digitalWrite (IN2, LOW);
      digitalWrite (IN1, HIGH);
      break;
    case RIGHT:
      // Move the left Caterpiller
      //Serial.println("Moving!");
      digitalWrite (IN4, LOW);
      digitalWrite (IN3, HIGH);
      digitalWrite (IN2, HIGH);  // LOW, HIGH for back
      digitalWrite (IN1, LOW);
      break;
    default:
      // Stop All Motors
      digitalWrite (IN4, LOW);
      digitalWrite (IN3, LOW);
      digitalWrite (IN2, LOW);
      digitalWrite (IN1, LOW);
      break;
  }

}



void loop() {
  long duration, distance;
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(5);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH);
  distance = (duration / 2) / 29.1;
  if (distance == 0) {
    // This is likely an error with the sensor.
    //buzz();
  } else if (distance < 12) {  

    if (debug)
    {
      Serial.print("OBSTACLE !");Serial.println(distance);
    }

    motorstate = MOVE_BACKWARDS;
    interval = 100;
  } else {
    //motorstate=STILL;
    //digitalWrite(led,LOW);
    //digitalWrite(led2,HIGH);
  }
  if (distance >= 200 || distance <= 0) {
    //Serial.println("200");
  }
  else {
    //Serial.print(distance);
    //Serial.println(" cm");
  }

  // Check light and sound sensors.
  if (isDark()) {
    //limbic = PHOTOTROPISM;
  }
  if (isBarking()) {
    limbic = PHONOTROPISM;
  }


  loopMotor();
  //delay(10);
}






