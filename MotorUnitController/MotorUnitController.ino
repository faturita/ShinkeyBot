/**
   Motor Unit Controller for ShinkeyBot

   It uses Adafruit_MotorShield v2 from Adafruit.

   Gripper 1 DC Motor -> M1
   Shoulder 2 DC Motor 12 V -> M2
   Tesaki 4 DC Motor from the broken servo 6 V -> M4

   Servo Wrist 9V 180 -> Servo 1 Pin 10  White, Grey Violet
   Servo Elbow 9V 360 -> Servo 2 Pin 9 Coaxial  Black White Grey

   Encoder (shoulder)
   Pin 12 connected to CLK on KY-040
   Pin 13 connected to DT  on KY-040
   + to Arduino 5V
   GND to Arduino GND


   Tilt Sensor (Elbow)
   SCL connected to SCL on MMA8452
   SDA connected to SDA on MMA8452   (I2C port is 60)
   3.3V connected to Arduino 3.3 V
   GND to Arduino GND 
   
*/


// I2C is 0x60
#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_MS_PWMServoDriver.h"

#include <SparkFun_MMA8452Q.h> // Includes the SFE_MMA8452Q library

// I2C Address is 0x1D (connect SA0 to ground to be 0x1C)
MMA8452Q accel;

#include <Servo.h>

bool debug = false;

const int laserPin = 8;

// Create the motor shield object with the default I2C address
Adafruit_MotorShield AFMS = Adafruit_MotorShield();
// Or, create it with a different I2C address (say for stacking)
// Adafruit_MotorShield AFMS = Adafruit_MotorShield(0x61);

// Select which 'port' M1, M2, M3 or M4. In this case, M1
Adafruit_DCMotor *grip = AFMS.getMotor(1);
Adafruit_DCMotor *tesaki = AFMS.getMotor(4);
Adafruit_DCMotor *shoulder = AFMS.getMotor(2);

Servo wrist;
Servo elbow;


int state = 0;
int speeds = 255;


struct sensortype {
  int counter;
  int encoder;
  float cx;
  float cy;
  float cz;
  float angle;
  int fps;
} sensor;


void setup() {
  Serial.begin(9600); // set up Serial library at 9600 bps
  Serial.println("Motor Unit Neuron");

  AFMS.begin();  // create with the default frequency 1.6KHz
  //AFMS.begin(1000);  // OR with a different frequency, say 1KHz

  wrist.attach(10);
  elbow.attach(9);

  pinMode(laserPin, OUTPUT);

  setupEncoder();
  accel.init();
}

int incomingByte = 0;

char buffer[5];

int direction = 0;
int pos = 48;
int desiredpos = 48;

void update(Servo servo) {

  if (desiredpos != pos)
  {
    //Serial.print(pos);Serial.print("--");
    //Serial.println(desiredpos);
    servo.write(pos);

    pos += direction;

    if (pos >= 185)
    {
      //Serial.print("Reset down:");
      //Serial.println(counter++);
      direction = -1;
    }

    if (pos <= 48)
    {
      //Serial.print("Reset up:");
      //Serial.println(counter++);
      direction = 1;
    }
  }

}

void push(Adafruit_DCMotor *motor) {
  motor->run(FORWARD);
  motor->setSpeed(0);
  delay(50);
  motor->setSpeed(255);
  delay(50);
}

void pull(Adafruit_DCMotor *motor) {
  motor->run(BACKWARD);
  motor->setSpeed(0);
  delay(50);
  motor->setSpeed(255);
  delay(250);
}

int elbowcounter = 0;
int tesakicounter = 0;
int grippercounter = 0;

int targetpos = 0;

void setTargetPos(int newtargetpos)
{
  targetpos = newtargetpos;
}


void updatedc(Adafruit_DCMotor *dcmotor, int currentpos)
{
  if (targetpos != currentpos)
  {
    dcmotor->setSpeed(90);

    if (targetpos < currentpos)
      dcmotor->run(FORWARD);
    else
      dcmotor->run(BACKWARD);

  } else {
    dcmotor->setSpeed(0);
  }

}

float targetposelbow=1.72;


float fdet(float val)
{
  return val*(-0.3)+204;
}

void updaterotservo(Servo servo, float currentpos)
{
  //Serial.print(currentpos);Serial.print("->");Serial.print(targetposelbow);Serial.print("--");Serial.print(accel.cx);Serial.print(":");Serial.print(accel.cz);Serial.print(",");Serial.print(accel.cy);Serial.print(",");Serial.print("Angle:");Serial.println(getTilt()*180.0/PI);
  
  //if (true || abs(targetposelbow-currentpos)<0.20)
  //if (abs(targetposelbow-currentpos)>0.1)
  {
    int direction=1;
    if (targetposelbow < currentpos)
      direction=1;
    else
      direction=-1;
      
    servo.writeMicroseconds((fdet(targetposelbow*180.0/PI)+10*direction) * 10);
    //Serial.println( (fdet(targetposelbow*180.0/PI))+10*direction );

  //} else {
    //servo->writeMicroseconds(speeds * 10);
  }

}

void setTargetPosElbow(float newtargetpos)
{
  targetposelbow = newtargetpos;  
}

void readcommand(int &state, int &speeds)
{
  // Format A1000 >> A1220   --> Close grip
  // A2255 >> Open Grip
  // A6090 >> 90 deg wrist A6010 --> A6180
  // A3220 or A4220 Move forward backward shoulder
  // A7150 will keep the elbow at zero encoder angle arm vertical. So AA140 will pull it up
  // A8220 clockwise A9220 counter
  // AA150 -> Keep elbow steady, AA140 backward AA160 forward (AA100 --> AA150 --> AA200)
  // Format A5000  Reset everything.
  memset(buffer, 0, 5);
  int readbytes = Serial.readBytes(buffer, 4);

  if (readbytes == 4) {
    if (debug) Serial.println ( (int)buffer[0] );
    int action = 0;
    if (buffer[0] >= 65)  // send alpha hexa actions.
      action = buffer[0] - 65 + 10;
    else
      action = buffer[0] - 48;
    int a = buffer[1] - 48;
    int b = buffer[2] - 48;
    int c = buffer[3] - 48;

    speeds = atoi(buffer + 1);
    state = action;

    if (debug) {
      Serial.print("Action:");
      Serial.print(action);
      Serial.print("/");
      Serial.println(speeds);
    }
  }
}


void loop() {
  if (accel.available())
  {
    // First, use accel.read() to read the new variables:
    accel.read();
    //printCalculatedAccels();
  }

  //Serial.print("Angle:");Serial.print(accel.cz);Serial.print(",");Serial.print(accel.cy);Serial.print(",");Serial.println(getTilt());
  sensor.fps = fps();
  checksensors();
  burstsensors();

  if (Serial.available() > 0) 
  {

    char syncbyte = Serial.read();

    switch (syncbyte) 
    {
      case 'I':
        Serial.println("MTRN");
        break;
      case 'S':
        startburst();
        break;
      case 'X':
        stopburst();
        break;
      case 'D':
        debug = (!debug);
        break;
      case 'L':
        digitalWrite(laserPin, HIGH);
        break;
      case 'l':
        digitalWrite(laserPin, LOW);
        break;
      case 'Q':
        Serial.println( getEncoderPos() );
        break;
      case 'U':
        Serial.print(accel.cx);Serial.print(":");Serial.print(accel.cz);Serial.print(",");Serial.print(accel.cy);Serial.print(",");Serial.print("Angle:");Serial.println(getTilt()*180.0/PI);
        break;
      case '=':
        resetEncoderPos();
        targetpos=0;
        break;
      case 'A':
        readcommand(state,speeds);
        break;
      default:
        break;
    }

  }

  // Update the servo wrist position.
  update(wrist);

  updateEncoder();

  updatedc(shoulder, getEncoderPos());

  //updaterotservo(elbow, getTilt());

  switch (state)
  {
    case 1:
      //grip->write(speeds);
      grip->setSpeed(speeds);
      grip->run(FORWARD);
      grippercounter = 1;
      break;
    case 2:
      //grip->write(-speeds);
      grip->setSpeed(speeds);
      grip->run(BACKWARD);
      grippercounter = 1;
      break;
    case 3:
      // Go up
      shoulder->setSpeed(speeds);
      shoulder->run(FORWARD);
      break;
    case 4:
      shoulder->setSpeed(speeds);
      shoulder->run(BACKWARD);
      break;
    case 7:
      setTargetPos(speeds - 150);
      break;
    case 5:
      grip->run(RELEASE);
      tesaki->run(RELEASE);
      shoulder->run(RELEASE);
      elbow.detach();
      wrist.detach();
      state = 0;
      break;
    case 6:
      // Update desired position.
      desiredpos = speeds;
      if (pos < desiredpos)
        direction = 1;
      else
        direction = -1;
      break;
    case 8:
      tesakicounter = 1;
      tesaki->setSpeed(speeds);
      tesaki->run(BACKWARD);
      break;
    case 9:
      tesakicounter = 1;
      tesaki->setSpeed(speeds);
      tesaki->run(FORWARD);
      break;
    case 0x0a:
      // 150x10 is no movement. 360 servo.
      elbow.writeMicroseconds(speeds * 10);
      elbowcounter = 1;
      break;
    case 0x0b:
      setTargetPosElbow(((float)speeds)*PI/180.0);
      elbowcounter = 1;
    default:
      // Do Nothing
      state = 0;
      break;

  }

  // Limit Elbow movement.  This servo will try to stay on that position for 1000 cycles.
/**  elbowcounter = elbowcounter + 1;


  if (elbowcounter >= 3000) {
    elbow.writeMicroseconds(1500);
    elbowcounter = 0;
  }**/


  // Limit The movement of the wrist rolling.
  tesakicounter = tesakicounter + 1;

  if (tesakicounter > 50) {
    tesaki->setSpeed(0);
    tesakicounter = 0;
  }


  // Limit the gripper force.
  grippercounter = grippercounter + 1;

  if (grippercounter > 400) {
    grip->setSpeed(0);
    grippercounter = 0;
  }


  //delay(10);
  state = 0;  // State is reset after the command has been given and processesd.

}
