/**
 * The S goes pulled down with 10k ohms resistence connected to ground.
 * The S goes to A0, analog output (pulled down from the resistor).
 * 
 * The (-) goes to 5V
 * 
 * The middle is not being used.
 * 
 * Callibration:
 * 
 * Above light: 700
 * Dark room: 500
 * Lightern above: 1000
 * Finger on top: 260
 */

#define c 261
#define d 294
#define e 329
#define f 349
#define g 391
#define gS 415
#define a 440
#define aS 455
#define b 466
#define cH 523
#define cSH 554
#define dH 587
#define dSH 622
#define eH 659
#define fH 698
#define fSH 740
#define gH 784
#define gSH 830
#define aH 880
//frequencies for the tones we're going to use
//used http://home.mit.bme.hu/~bako/tonecalc/tonecalc.htm to get these



int photoresistorPin = A3; // analog input
int sensorPin = A2;   // Analog input 
int speakerPin = 11;

int soundSensorValue = 0;
int minSoundThreshold = 160;

double analogValue;
double minLightValue = 650.0; // min analog value to turn on LED

void setupEnvironmentSensor() {
  // sets up pin input/output
  pinMode(photoresistorPin, INPUT);
  pinMode(sensorPin, INPUT);
  pinMode(speakerPin, OUTPUT); 
}

void beep (unsigned char speakerPin, int frequencyInHertz, long timeInMilliseconds)
{ 
    digitalWrite(ledPin, HIGH);  
    //use led to visualize the notes being played
    
    int x;   
    long delayAmount = (long)(1000000/frequencyInHertz);
    long loopTime = (long)((timeInMilliseconds*1000)/(delayAmount*2));
    for (x=0;x<loopTime;x++)   
    {    
        digitalWrite(speakerPin,HIGH);
        delayMicroseconds(delayAmount);
        digitalWrite(speakerPin,LOW);
        delayMicroseconds(delayAmount);
    }    
    
    digitalWrite(ledPin, LOW);
    //set led back to low
    
    delay(20);
    //a little delay to make all notes sound separate
} 

     
void march()
{    
    //for the sheet music see:
    //http://www.musicnotes.com/sheetmusic/mtd.asp?ppn=MN0016254
    //this is just a translation of said sheet music to frequencies / time in ms
    //used 500 ms for a quart note
    
    beep(speakerPin, a, 500); 
    beep(speakerPin, a, 500);     
    beep(speakerPin, a, 500); 
    beep(speakerPin, f, 350); 
    beep(speakerPin, cH, 150);
    
    beep(speakerPin, a, 500);
    beep(speakerPin, f, 350);
    beep(speakerPin, cH, 150);
    beep(speakerPin, a, 1000);
    //first bit
    
    beep(speakerPin, eH, 500);
    beep(speakerPin, eH, 500);
    beep(speakerPin, eH, 500);    
    beep(speakerPin, fH, 350); 
    beep(speakerPin, cH, 150);
    
    beep(speakerPin, gS, 500);
    beep(speakerPin, f, 350);
    beep(speakerPin, cH, 150);
    beep(speakerPin, a, 1000);
    //second bit...
    
    beep(speakerPin, aH, 500);
    beep(speakerPin, a, 350); 
    beep(speakerPin, a, 150);
    beep(speakerPin, aH, 500);
    beep(speakerPin, gSH, 250); 
    beep(speakerPin, gH, 250);
    
    beep(speakerPin, fSH, 125);
    beep(speakerPin, fH, 125);    
    beep(speakerPin, fSH, 250);
    delay(250);
    beep(speakerPin, aS, 250);    
    beep(speakerPin, dSH, 500);  
    beep(speakerPin, dH, 250);  
    beep(speakerPin, cSH, 250);  
    //start of the interesting bit
    
    beep(speakerPin, cH, 125);  
    beep(speakerPin, b, 125);  
    beep(speakerPin, cH, 250);      
    delay(250);
    beep(speakerPin, f, 125);  
    beep(speakerPin, gS, 500);  
    beep(speakerPin, f, 375);  
    beep(speakerPin, a, 125); 
    
    beep(speakerPin, cH, 500); 
    beep(speakerPin, a, 375);  
    beep(speakerPin, cH, 125); 
    beep(speakerPin, eH, 1000); 
    //more interesting stuff (this doesn't quite get it right somehow)
    
    beep(speakerPin, aH, 500);
    beep(speakerPin, a, 350); 
    beep(speakerPin, a, 150);
    beep(speakerPin, aH, 500);
    beep(speakerPin, gSH, 250); 
    beep(speakerPin, gH, 250);
    
    beep(speakerPin, fSH, 125);
    beep(speakerPin, fH, 125);    
    beep(speakerPin, fSH, 250);
    delay(250);
    beep(speakerPin, aS, 250);    
    beep(speakerPin, dSH, 500);  
    beep(speakerPin, dH, 250);  
    beep(speakerPin, cSH, 250);  
    //repeat... repeat
    
    beep(speakerPin, cH, 125);  
    beep(speakerPin, b, 125);  
    beep(speakerPin, cH, 250);      
    delay(250);
    beep(speakerPin, f, 250);  
    beep(speakerPin, gS, 500);  
    beep(speakerPin, f, 375);  
    beep(speakerPin, cH, 125); 
           
    beep(speakerPin, a, 500);            
    beep(speakerPin, f, 375);            
    beep(speakerPin, c, 125);            
    beep(speakerPin, a, 1000);       
    //and we're done \ó/    
}


bool isBarking() {
  bool retval = false;
  soundSensorValue = analogRead(sensorPin);

  if (soundSensorValue>minSoundThreshold) {
    //digitalWrite (ledPin, HIGH); 
    //beep(speakerPin, a, 10); 
    retval = true;
  }
    
  if (debug) { Serial.print("Sound:");Serial.println (soundSensorValue, DEC); }

  sensor.sound = soundSensorValue;
  
  return retval;
}

bool isDark() {
  bool retval = false;
  // reads analog input
  analogValue = analogRead(photoresistorPin);
  // if input is less than minLightValue turn on LED
  
  if (analogValue < minLightValue) {
    //digitalWrite(ledPin, HIGH);
    retval = true;
  } else {
     //digitalWrite(ledPin, LOW); 
  }
  if (debug) {Serial.print("Light:");Serial.println(analogValue);}
  
  // reads photoresistor every half second
  //delay(500);
  sensor.light = analogValue;
  return retval;
}

void buzz() {
  beep(speakerPin, a, 300);
}
