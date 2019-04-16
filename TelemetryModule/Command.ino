int incomingByte = 0;

char buffer[5];

void readcommand(int &state, int &controlvalue)
{
  // Format ACNNN, 'A', C is command, NNN is the controlvalue.
  memset(buffer, 0, 5);
  int readbytes = Serial.readBytes(buffer, 4);

  if (readbytes == 4) {
    if (debug) Serial.println ( (int)buffer[0] );
    int action = 0;
    if ((buffer[0] == 'B') || (buffer[0] == 'C') || (buffer[0] == 'D'))  // send alpha hexa actions.
      action = buffer[0] - 65 + 10;
    else
      action = buffer[0];
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


