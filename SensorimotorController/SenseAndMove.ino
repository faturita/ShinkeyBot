/*
HC-SR04 Ping distance sensor]
VCC to arduino 5v GND to arduino GND
Echo to Arduino pin 13 Trig to Arduino pin 12
Red POS to Arduino pin 11
Green POS to Arduino pin 10
560 ohm resistor to both LED NEG and GRD power rail
More info at: http://goo.gl/kJ8Gl
Original code improvements to the Ping sketch sourced from Trollmaker.com
Some code and wiring inspired by http://en.wikiversity.org/wiki/User:Dstaub/robotcar
*/

//#define trigPin 13
//#define echoPin 12
#define led 11
#define led2 10


#define trigPin 13
#define echoPin 12


int IN4 = 5;
int IN3 = 4; 
int IN2 = 3; 
int IN1 = 2;


// constants won't change. Used here to set a pin number :
const int ledPin =  13;      // the number of the LED pin

// Variables will change :
int ledState = LOW;             // ledState used to set the LED

// Generally, you should use "unsigned long" for variables that hold time
// The value will quickly become too large for an int to store
unsigned long previousMillis = 0;        // will store last time LED was updated

// constants won't change :
const long interval = 800;           // interval at which to blink (milliseconds)


void setupMotor()
{
  pinMode (IN4, OUTPUT);    // Input4 conectada al pin 4 
  pinMode (IN3, OUTPUT);    // Input3 conectada al pin 5
  pinMode (IN2, OUTPUT);    // Input4 conectada al pin 3 
  pinMode (IN1, OUTPUT);    // Input3 conectada al pin 2

  // set the digital pin as output:
  pinMode(ledPin, OUTPUT);  
}


void setup() {
  Serial.begin (9600);
  //pinMode(trigPin, OUTPUT);
  //pinMode(echoPin, INPUT);
  //pinMode(led, OUTPUT);
  //pinMode(led2, OUTPUT);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  setupMotor();

}

int motorstate=40;


void blinkme()
{
  // here is where you'd put code that needs to be running all the time.

  // check to see if it's time to blink the LED; that is, if the
  // difference between the current time and last time you blinked
  // the LED is bigger than the interval at which you want to
  // blink the LED.
  unsigned long currentMillis = millis();
 
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
  }
}

void loopMotor()
{
  blinkme();

  if (ledState == HIGH)
  switch (motorstate)
  {
    case 0: 
      // Motor gira en un sentido
      Serial.println("Moving!");
      digitalWrite (IN4, HIGH);
      digitalWrite (IN3, LOW); 
      digitalWrite (IN2, HIGH);
      digitalWrite (IN1, LOW); 
      motorstate++;
      break;
    default:
      // Motor no gira
      Serial.println("Stopping");
      digitalWrite (IN4, LOW);
      digitalWrite (IN3, LOW); 
      digitalWrite (IN2, LOW);
      digitalWrite (IN1, LOW); 
      break;
  }

  delay(10);
}



void loop() {
  long duration, distance;
  digitalWrite(trigPin, LOW);  // Added this line
  delayMicroseconds(2); // Added this line
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(5); // Added this line
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH);
  distance = (duration/2) / 29.1;
  if (distance < 4) {  // This is where the LED On/Off happens
    //digitalWrite(led,HIGH); // When the Red condition is met, the Green LED should turn off
    //digitalWrite(led2,LOW);

    motorstate=0;
  }
  else {
    //digitalWrite(led,LOW);
    //digitalWrite(led2,HIGH);
  }
  if (distance >= 200 || distance <= 0){
    Serial.println("Out of range");
  }
  else {
    Serial.print(distance);
    Serial.println(" cm");
  }

  loopMotor();
  delay(10);
}






