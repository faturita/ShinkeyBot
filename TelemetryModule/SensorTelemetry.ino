#define MAX_SIZE_SENSOR_BURST 100

int fps()
{
  static int freqValue = 200;
  static int freqCounter = 0;
  static unsigned long myPreviousMillis = millis();
  unsigned long myCurrentMillis = 0;

  myCurrentMillis = millis();

  if ((myCurrentMillis - myPreviousMillis) > 1000)
  {
    if (debug)
    {
      Serial.print("Frequency:"); Serial.println(freqCounter);
    }
    myPreviousMillis = myCurrentMillis;
    freqValue = freqCounter;
    freqCounter = 0;
  }
  else
  {
    freqCounter++;
  }
  return freqValue;
}

bool sensorburst = false;
int transmittedCounter = 0;
int burstsize = MAX_SIZE_SENSOR_BURST;

int updateFreq = 1;

void setBurstSize(int pburstsize)
{
  burstsize = pburstsize;
}

void setUpdateFreq(int controlvalue) 
{
  updateFreq = controlvalue;
}


bool checksensors()
{
  static int counter = 0;
  if (counter >= 255)
  {
    counter = 0;
  }
  sensor.counter = counter++;
  return (sensorburst);

}


void burstsensors() {
  if (sensorburst)
  {
    if (transmittedCounter % updateFreq == 0)
    {
      transmitsensors();
    }
    transmittedCounter++;
    if (transmittedCounter >= burstsize || transmittedCounter >= MAX_SIZE_SENSOR_BURST)
    {
      sensorburst = false;
      transmittedCounter = 0;
    }
  }
}

void startburst()
{
  sensorburst = true;
  // Reset counter to avoid loosing data.
  transmittedCounter = 0;
}

void stopburst()
{
  sensorburst = false;  
}

void payloadsize()
{
  int len = sizeof(sensor);
  char aux[sizeof(int)];  
  
  memcpy(&aux,&len,sizeof(int));

  Serial.write((uint8_t *)&aux,sizeof(int));
 
}

// FIXME: Modify this.
void payloadstruct()
{
  char aux[5];
  strcpy(aux,"fffhh");
  Serial.write(aux);
}

void transmitsensors() {
  int len = sizeof(sensor);
  char aux[len];  //70
  memcpy(&aux,&sensor,len);

  if (debug)
  {
    Serial.print("Len:");Serial.println(len);
    Serial.print("Counter:");Serial.println(sensor.counter);
    Serial.print("Int:");Serial.println(sizeof(int));
    Serial.print("Long:");Serial.println(sizeof(long));
    Serial.print("int16_t");Serial.println(sizeof(int16_t));
  }
  
  Serial.write('S');
  Serial.write((uint8_t *)&aux,len);
  Serial.write('E');

  if (debug) {
    Serial.println('S');

  }
  

  //Aguarda 5 segundos e reinicia o processo
  //delay(5000);
}


