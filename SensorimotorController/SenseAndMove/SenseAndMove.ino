/**
 * ShinkeyBot - Sensorimotor
 * 
 * Fuse senses and move the robot wheels.
 * 
 * HR-SR04 - Distance Sensor
 *     VCC to Arduino 5v 
 *     GND to Arduino GND
 *     Echo to Arduino Pin 13
 *     Trig to Arduino Pin 12
 *     Red Led to Arduino Pin 11
 *     Green Led to Arduino Pin 10
 *     560 ohm resistor to both Led Neg and GND Power rail
 *     http://goo.gl/kJ8Gl    
 *     http://en.wikiversity.org/wiki/User:Dstaub/robotcar 
 *     
 *     Motor Wheel: Pin 5,4,3,2.
 */


#define trigPin 13
#define echoPin 12


int IN4 = 5;
int IN3 = 4; 
int IN2 = 3; 
int IN1 = 2;


// constants won't change. Used here to set a pin number :
const int ledPin =  13;      // the number of the LED pin

// Variables will change :
int ledState = HIGH;             // ledState used to set the LED

// Generally, you should use "unsigned long" for variables that hold time
// The value will quickly become too large for an int to store
unsigned long previousMillis = 0;        // will store last time LED was updated

// constants won't change :
const long interval = 2000;           // interval at which to blink (milliseconds)



struct sensortype
{
  double onYaw;
  double onPitch;
  double onRoll;
  int yaw;
  int pitch;
  int roll;
  int geoYaw;
  int geoPitch;
  int geoRoll;
  float T;
  float P;
  
} sensor;


bool serialOpen = 1;


void dump(char *msg)
{
  if (serialOpen)
  {
    Serial.println(msg);
  }
}



void setupMotor()
{
  pinMode (IN4, OUTPUT);    // Input4 conectada al pin 4 
  pinMode (IN3, OUTPUT);    // Input3 conectada al pin 5
  pinMode (IN2, OUTPUT);    // Input4 conectada al pin 3 
  pinMode (IN1, OUTPUT);    // Input3 conectada al pin 2

  // set the digital pin as output:
  pinMode(ledPin, OUTPUT);  

  randomSeed(analogRead(0));

  initsensors();
}


void setup() {
  Serial.begin (115200);
  dump("Sensorimotor Cortex");

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  setupMotor();
}

int const QUIET = 0;
int const STILL = 1;
int const MOVE_FORWARD = 2;
int const MOVE_BACKWARDS = 3;
int const RIGHT = 4;
int const LEFT = 5;

// L3 &&  L1 is BACKWARDS

int motorstate=STILL;

int txSensor = 0;

int minRange = 1;

void blinkme()
{
  // here is where you'd put code that needs to be running all the time.

  // check to see if it's time to blink the LED; that is, if the
  // difference between the current time and last time you blinked
  // the LED is bigger than the interval at which you want to
  // blink the LED.
  unsigned long currentMillis = millis();

  int incomingByte;


  if (txSensor == 1)
  {
    checksensors();
  }
    
  if (Serial.available() > 0) {
    incomingByte = Serial.read();

    if (incomingByte == 'S')
    {
      txSensor = 1;
    } else if (incomingByte == 'X')
    {
      txSensor = 0;
    } else if (incomingByte == 'W')
    {
      minRange=1;
    } else if (incomingByte == 'C')
    {
      minRange=6;
    }
    else
    if (48<incomingByte && incomingByte<58)
    {
      motorstate = incomingByte-48;
      previousMillis = currentMillis; 
    }
  } 
  else
  if(currentMillis - previousMillis >= interval) {
    // save the last time you blinked the LED 
    previousMillis = currentMillis; 

    // if the LED is off turn it on and vice-versa:
    if (ledState == LOW)
      ledState = HIGH;
    else
      ledState = LOW;

    // set the LED with the ledState of the variable:
    digitalWrite(ledPin, ledState);

    long randNumber = random(14);

    if (motorstate != QUIET)
    {
      // Plus one is to eliminate the chance to fallback in quit mode
      motorstate = ((int)randNumber)+minRange;
    }
    //motorstate = STILL;
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
      digitalWrite (IN4, LOW); // LOW, HIGH for back
      digitalWrite (IN3, LOW); 
      digitalWrite (IN2, LOW);
      digitalWrite (IN1, HIGH); 
      break;
    case RIGHT: 
      // Move the left Caterpiller
      //Serial.println("Moving!");
      digitalWrite (IN4, LOW);
      digitalWrite (IN3, HIGH); 
      digitalWrite (IN2, LOW);  // LOW, HIGH for back
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
  distance = (duration/2) / 29.1;
  if (distance < 14) {  // This is where the LED On/Off happens
    //digitalWrite(led,HIGH); // When the Red condition is met, the Green LED should turn off
    //digitalWrite(led2,LOW);

    motorstate=MOVE_BACKWARDS;
  }
  else {
    //motorstate=STILL;
    //digitalWrite(led,LOW);
    //digitalWrite(led2,HIGH);
  }
  if (distance >= 200 || distance <= 0){
    //Serial.println("200");
  }
  else {
    //Serial.print(distance);
    //Serial.println(" cm");
  }

  loopMotor();
  delay(10);
}






