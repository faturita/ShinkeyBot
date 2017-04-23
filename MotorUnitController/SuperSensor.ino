#define MAX_SIZE_SENSOR_BURST 100

void printCalculatedAccels()
{
  Serial.print(accel.cx, 3);
  Serial.print("\t");
  Serial.print(accel.cy, 3);
  Serial.print("\t");
  Serial.print(accel.cz, 3);
  Serial.print("\t");
}

float getTilt()
{
  if (accel.cz < 0)
  {
    return 2*PI+atan2(accel.cz,accel.cy);
  } else
  {
    return atan2(accel.cz,accel.cy);
  }
}

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

void checksensors()
{
  static int counter = 0;
  if (counter >= 255)
  {
    counter = 0;
  }
  sensor.counter = counter++;

  sensor.cx = accel.cx;
  sensor.cy = accel.cy;
  sensor.cz = accel.cz;

  sensor.angle = getTilt()*180.0/PI;

  sensor.encoder = getEncoderPos();
}

bool sensorburst = false;
int sampleCounter = 0;

void burstsensors() {
  if (sensorburst)
  {
    transmitsensors();
    sampleCounter++;
    if (sampleCounter > MAX_SIZE_SENSOR_BURST)
    {
      sensorburst = false;
      sampleCounter = 0;
    }
  }
}

void startburst()
{
  sensorburst = true;
  // Reset counter to avoid loosing data.
  sampleCounter = 0;
}

void stopburst()
{
  sensorburst = false;  
}

void transmitsensors() {
  int len = sizeof(sensor);
  char aux[len];  //38
  memcpy(&aux, &sensor, len);

  Serial.write('S');
  Serial.write((uint8_t *)&aux, len);
  Serial.write('E');

  if (debug) {
    Serial.println('S');
    Serial.print("Cx:"); Serial.println(sensor.cx);
    Serial.print("Cy:"); Serial.println(sensor.cy);
    Serial.print("Cz:"); Serial.println(sensor.cz);
    Serial.print("Angle:"); Serial.println(sensor.angle);
    Serial.print("Encoder:"); Serial.println(sensor.encoder);
    Serial.println(']');
  }


  //Aguarda 5 segundos e reinicia o processo
  //delay(5000);
}
