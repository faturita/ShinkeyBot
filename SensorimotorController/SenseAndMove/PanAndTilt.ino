#include <Servo.h>

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

void setTiltTgtPos(int tgtPos) {
  tilt.tgtPos = tgtPos;
}

void setPanTgtPos(int tgtPos) {
  pan.tgtPos = tgtPos;
}

void setupPanAndTilt() {
  tilt.servo.attach(14);
  pan.servo.attach(15);
  tilt.pos = 90;
  pan.pos = 90;
  tilt.tgtPos = 90;
  pan.tgtPos = 90;
  tilt.minPos=90;
  tilt.maxPos=180;
}

void loopPanAndTilt() {
  tilt.update();
  pan.update();
}



