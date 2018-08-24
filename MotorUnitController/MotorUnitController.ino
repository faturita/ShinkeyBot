/**
   Motor Unit Controller for ShinkeyBot

   It uses Adafruit_MotorShield v2 from Adafruit.

   Gripper 1 DC Motor -> M1
   Shoulder 2 DC Motor 12 V -> M2
   Shoulder Arm 3 DC Motor 12 V -> M3
   Tesaki 4 DC Motor from the broken servo 6 V -> M4

   Servo Wrist 9V 180 -> Servo 1 Pin 10  White, Grey Violet
   Servo Elbow 9V 360 -> Servo 2 Pin 9 Coaxial  Black White Grey

   Encoder (shoulder)
   Pin 12 connected to CLK on KY-040
   Pin 13 connected to DT  on KY-040
   + to Arduino 5V
   GND to Arduino GND

   Encoder (Clavicle)
   Pin 6 connected to CLK on KY-040
   Pin 5 connected to DT  on KY-040
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
Adafruit_DCMotor *clavicle = AFMS.getMotor(3);

class ControlledServo {
public:
  Servo servo;
  int pos;
  int tgtPos;
  int direction = 1;
  int minPos=0;
  int maxPos=180;

  void loop() {
      // Update desired position.
      if (pos<tgtPos)
        direction = 1;
      else
        direction =-1;
  }

  void update() {

    loop();
    if (tgtPos != pos)
    {
      //Serial.print(pos);Serial.print("--");
      //Serial.println(tgtPos);
      servo.write(pos);

      pos+=direction;

      if (pos<minPos)
      {
        //Serial.print("Reset down:");
        //Serial.println(counter++);
        direction=-1;
      }

      if (pos>maxPos)
      {
        //Serial.print("Reset up:");
        //Serial.println(counter++);
        direction=1;
      }
    }

  }
};

ControlledServo wrist;
ControlledServo elbow;

class EncoderDC {
public:
  int pinA = 6;  // Connected to CLK on KY-040
  int pinB = 5;  // Connected to DT on KY-040
  int encoderPosCount;
  int pinALast;
  int aVal;
  boolean bCW;
  void setupEncoder(int cPinA, int cPinB) {
    pinA = cPinA;
    pinB = cPinB;
    pinMode (pinA, INPUT);
    pinMode (pinB, INPUT);
    encoderPosCount = 0;
    /* Read Pin A
      Whatever state it's in will reflect the last position
    */
    pinALast = digitalRead(pinA);
  }
  void updateEncoder() {
    aVal = digitalRead(pinA);
    if (aVal != pinALast) { // Means the knob is rotating
      // if the knob is rotating, we need to determine direction
      // We do that by reading pin B.
      if (digitalRead(pinB) != aVal) {  // Means pin A Changed first - We're Rotating Clockwise
        encoderPosCount ++;
        bCW = true;
      } else {// Otherwise B changed first and we're moving CCW
        bCW = false;
        encoderPosCount--;
      }
      if (debug) Serial.print ("Rotated: ");
      if (bCW) {
        if (debug) Serial.println ("clockwise");
      } else {
        if (debug) Serial.println("counterclockwise");
      }
      if (debug) Serial.print("Encoder Position: ");
      if (debug) Serial.println(encoderPosCount);

    }
    pinALast = aVal;
  }


  int getEncoderPos()
  {
    return encoderPosCount;
  }

  void resetEncoderPos()
  {
    encoderPosCount=0;
  }
};

EncoderDC clavicleEncoder;
EncoderDC shoulderEncoder;

int state = 0;
int controlvalue = 255;


struct sensortype {
  int counter; // 2
  int encoder; // 2
  float cx;    // 4
  float cy;    // 4
  float cz;    // 4
  float angle; // 4
  int wrist;   // 2
  int elbow;   // 2
  int fps;     // 2
} sensor; // 26


void setup() {
  Serial.begin(9600); // set up Serial library at 9600 bps
  Serial.println("Motor Unit Neuron");

  AFMS.begin();  // create with the default frequency 1.6KHz
  //AFMS.begin(1000);  // OR with a different frequency, say 1KHz

  wrist.servo.attach(10);
  wrist.pos=90;
  wrist.tgtPos=90;
  elbow.servo.attach(9);
  elbow.pos=90;
  elbow.tgtPos=90;

  pinMode(laserPin, OUTPUT);

  shoulderEncoder.setupEncoder(12,13);
  clavicleEncoder.setupEncoder(6,5);
  accel.init();
}

int incomingByte = 0;

char buffer[5];


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

int targetPosShoulder=0;
int targetPosClavicle=0;


// =========== DC Control using the encoder.
//int targetpos = 0;
int TORQUE=200;


int setThisTargetPos(int newtargetpos)
{
  return newtargetpos;
}

bool updatethisdc(Adafruit_DCMotor *dcmotor, int torque,int thistargetpos,int currentpos)
{
  if (thistargetpos != currentpos)
  {
    dcmotor->setSpeed(torque);

    if (thistargetpos < currentpos)
      dcmotor->run(FORWARD);
    else
      dcmotor->run(BACKWARD);

    return false;

  } else {
    dcmotor->setSpeed(0);
    return true;
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
    //servo->writeMicroseconds(controlvalue * 10);
  }

}

void setTargetPosElbow(float newtargetpos)
{
  targetposelbow = newtargetpos;
}

void readcommand(int &state, int &controlvalue)
{
  // A1220 >> Close grip
  // A2255 >> Open Grip
  // A6090 >> 90 deg wrist A6010 --> A6180
  // A7150 will keep the shoulder at zero encoder angle arm vertical.
  //       So AA140 will pull it up
  // A8220 Wrist clockwise A9220 counter
  // AA090 -> Elbow is now servo.
  // AC150 -> Clavicle resting
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

    controlvalue = atoi(buffer + 1);
    state = action;

    if (debug) {
      Serial.print("Action:");
      Serial.print(action);
      Serial.print("/");
      Serial.println(controlvalue);
    }
  }
}

/**
 * Homing works by setting servos to 90 degrees, and later to pull
 * or push the shoulder DC so that the angle on the arm reads 90 degrees
 *
 * Then homing is stopped and the encoder is reset to zero.
 */
bool homing=false;

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
        Serial.println("MTRN2");
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
        Serial.println( shoulderEncoder.getEncoderPos() );
        Serial.println( clavicleEncoder.getEncoderPos() );
        break;
      case 'U':
        Serial.print(accel.cx);Serial.print(":");Serial.print(accel.cz);Serial.print(",");Serial.print(accel.cy);Serial.print(",");Serial.print("Angle:");Serial.println(getTilt()*180.0/PI);
        break;
      case '=':
        shoulderEncoder.resetEncoderPos();
        targetPosShoulder=0;
        targetPosShoulder=setThisTargetPos(90/10);
        elbow.tgtPos=90;
        wrist.tgtPos=90;
        homing=true;
        break;
      case 'A':
        readcommand(state,controlvalue);
        break;
      default:
        break;
    }

  }

  // Update the servo wrist position.
  wrist.update();
  sensor.wrist = wrist.pos;

  shoulderEncoder.updateEncoder();
  clavicleEncoder.updateEncoder();

  if (homing) {
    homing = !(updatethisdc(shoulder, TORQUE,targetPosShoulder, (int)((getTilt()*180.0/PI)/(10.0))));

    if (!homing) {
      shoulderEncoder.resetEncoderPos();
      targetPosShoulder=setThisTargetPos(0);
    }

  }
  else {
    updatethisdc(shoulder, TORQUE,targetPosShoulder,shoulderEncoder.getEncoderPos());
  }
  //updaterotservo(elbow, getTilt());

  updatethisdc(clavicle, 80,targetPosClavicle,clavicleEncoder.getEncoderPos());

  elbow.update();
  sensor.elbow = elbow.pos;

  switch (state)
  {
    case 1:
      //grip->write(controlvalue);
      grip->setSpeed(controlvalue);
      grip->run(FORWARD);
      grippercounter = 1;
      break;
    case 2:
      //grip->write(-controlvalue);
      grip->setSpeed(controlvalue);
      grip->run(BACKWARD);
      grippercounter = 1;
      break;
    case 3:
      // Go up
      shoulder->setSpeed(controlvalue);
      shoulder->run(FORWARD);
      break;
    case 4:
      shoulder->setSpeed(controlvalue);
      shoulder->run(BACKWARD);
      break;
    case 7:
      targetPosShoulder=setThisTargetPos(controlvalue - 150);
      break;
    case 5:
      grip->run(RELEASE);
      tesaki->run(RELEASE);
      shoulder->run(RELEASE);
      clavicle->run(RELEASE);
      elbow.servo.detach();
      wrist.servo.detach();
      state = 0;
      break;
    case 6:
      // Update desired position.
      wrist.tgtPos = controlvalue;
      break;
    case 8:
      tesakicounter = 1;
      tesaki->setSpeed(controlvalue);
      tesaki->run(BACKWARD);
      break;
    case 9:
      tesakicounter = 1;
      tesaki->setSpeed(controlvalue);
      tesaki->run(FORWARD);
      break;
    case 0x0a:
      // 150x10 is no movement. 360 servo.
      //elbow.writeMicroseconds(controlvalue * 10);
      elbow.tgtPos=controlvalue;
      elbowcounter = 1;
      break;
    case 0x0b:
      setTargetPosElbow(((float)controlvalue)*PI/180.0);
      elbowcounter = 1;
    case 0x0c:
      targetPosClavicle=setThisTargetPos(controlvalue - 150);
      break;
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
