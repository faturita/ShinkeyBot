#include "MeOrion.h"
//#include <Servo.h>

// Pan And Tilt requires 9v power.

class ControlledServo {
public:
  Servo servo;
  int pos;
  int tgtPos;
  int direction = 1;
  int minPos=0;
  int maxPos=180;

  void setTgtPos(int ptgtPos) {
    tgtPos = ptgtPos;
  }
  
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
      //Serial.println(desiredpos);
      servo.write(pos);
    
      pos+=direction;
      
      if (pos>=minPos)
      {
        //Serial.print("Reset down:");
        //Serial.println(counter++);
        direction=-1;
      }
    
      if (pos<=maxPos)
      {
        //Serial.print("Reset up:");
        //Serial.println(counter++);
        direction=1;    
      }
    }

  } 
};

ControlledServo tilt;
ControlledServo pan;

ControlledServo scan;

void setTiltTgtPos(int tgtPos) {
  tilt.tgtPos = tgtPos;
}

void setPanTgtPos(int tgtPos) {
  pan.tgtPos = tgtPos;
}

void setScanTgtPos(int tgtPos) {
  scan.tgtPos = tgtPos;
}

void setupPanAndTilt() {
  tilt.servo.attach(tiltServoPin); 
  pan.servo.attach(panServoPin); 
  tilt.pos = 95;
  pan.pos = 90;
  tilt.tgtPos = 95;
  pan.tgtPos = 90;
  pan.minPos=0;
  pan.maxPos=180;
  tilt.minPos=0;
  tilt.maxPos=140;

  scan.servo.attach(scanServoPin);
  scan.pos=90;
  scan.minPos=0;
  scan.maxPos=180;
  scan.tgtPos = 90;

  pinMode(scanTrigPin, OUTPUT);
  pinMode(scanEchoPin, INPUT);
}

void loopPanAndTilt() {
  tilt.update();
  pan.update();
  scan.update();

  sensor.tilt = tilt.pos;
  sensor.pan = pan.pos;
  sensor.scan = scan.pos;
}

int doScan()
{
  long duration, distance;
  digitalWrite(scanTrigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(scanTrigPin, HIGH);
  delayMicroseconds(5);
  digitalWrite(scanTrigPin, LOW);
  duration = pulseIn(scanEchoPin, HIGH);
  distance = (duration / 2) / 29.1;
  sensor.distance = distance;
  if (distance == 0) {
    // This is likely an error with the sensor.
    //buzz();
    return 0;
  } else {
    return distance;
  }
}


