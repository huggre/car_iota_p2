// Include the IRemote library
#include <IRremote.h>
IRsend irsend;

// A hexadecimal representation of the IOTA payment address
// where each element in the array consist of four characters
const int long msgArray[] = {0x47545a55,0x48515350,0x52415143,0x54535142,0x5a45454d,0x4c5a5051,0x55504141,0x394c504c,0x4757434b,0x464e4556,0x4b42494e,0x5845585a,0x52414356,0x4b4b4b43,0x59505750,0x4b483941,0x574c474a,0x48504c4f,0x5a5a4f59,0x54414c41,0x574f5653,0x494a4959,0x565a};

// Defines the delay in milliseconds between each IR message
const int delay_time = 500;
                             
void setup()  
{  
}  
                               
void loop()  
{  

  // Send start sequence message...
  irsend.sendNEC(0x30303030, 32);

  delay(delay_time);

  // Loop message elements
  for (int i=0; i<sizeof msgArray/sizeof msgArray[0]; i++) {

    // Send IR message element
    irsend.sendNEC(msgArray[i], 32);

    delay(delay_time);
    
  }

} 